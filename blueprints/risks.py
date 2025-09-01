from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from subscription_utils import require_pro

risks_bp = Blueprint('risks', __name__)

def get_db():
    """Get database connection"""
    from flask import current_app
    return current_app.get_db()

@risks_bp.route('/')
@require_pro
def index():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    db = get_db()
    risks = db.execute(
        'SELECT r.*, p.name as project_name '
        'FROM risks r '
        'LEFT JOIN projects p ON r.project_id = p.id '
        'ORDER BY r.risk_score DESC, r.created_at DESC'
    ).fetchall()
    
    # Risk statistics
    total_risks = len(risks)
    high_risks = len([r for r in risks if r['risk_score'] >= 15])  # probability 3+ and impact 5 or probability 5 and impact 3+
    medium_risks = len([r for r in risks if 6 <= r['risk_score'] < 15])
    low_risks = len([r for r in risks if r['risk_score'] < 6])
    
    stats = {
        'total_risks': total_risks,
        'high_risks': high_risks,
        'medium_risks': medium_risks,
        'low_risks': low_risks
    }
    
    return render_template('risks/index.html', risks=risks, stats=stats)

@risks_bp.route('/new', methods=['GET', 'POST'])
def new():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    db = get_db()
    projects = db.execute('SELECT id, name FROM projects ORDER BY name').fetchall()
    
    if request.method == 'POST':
        project_id = request.form.get('project_id')
        title = request.form.get('title')
        description = request.form.get('description')
        category = request.form.get('category')
        probability = request.form.get('probability', 1)
        impact = request.form.get('impact', 1)
        responsible_person = request.form.get('responsible_person')
        mitigation_plan = request.form.get('mitigation_plan')
        
        if not title:
            flash('Risk title is required', 'error')
            return render_template('risks/form.html', projects=projects)
        
        try:
            probability = int(probability)
            impact = int(impact)
            risk_score = probability * impact
            
            db.execute(
                'INSERT INTO risks (project_id, title, description, category, '
                'probability, impact, risk_score, responsible_person, mitigation_plan) '
                'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                (project_id or None, title, description, category,
                 probability, impact, risk_score, responsible_person, mitigation_plan)
            )
            db.commit()
            flash('Risk added successfully', 'success')
            return redirect(url_for('risks.index'))
        except ValueError:
            flash('Invalid probability or impact value', 'error')
        except Exception as e:
            flash('Error adding risk', 'error')
    
    return render_template('risks/form.html', projects=projects)

@risks_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
def edit(id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    db = get_db()
    risk = db.execute('SELECT * FROM risks WHERE id = ?', (id,)).fetchone()
    projects = db.execute('SELECT id, name FROM projects ORDER BY name').fetchall()
    
    if not risk:
        flash('Risk not found', 'error')
        return redirect(url_for('risks.index'))
    
    if request.method == 'POST':
        project_id = request.form.get('project_id')
        title = request.form.get('title')
        description = request.form.get('description')
        category = request.form.get('category')
        probability = request.form.get('probability')
        impact = request.form.get('impact')
        responsible_person = request.form.get('responsible_person')
        mitigation_plan = request.form.get('mitigation_plan')
        status = request.form.get('status')
        
        if not title:
            flash('Risk title is required', 'error')
            return render_template('risks/form.html', risk=risk, projects=projects)
        
        try:
            probability = int(probability)
            impact = int(impact)
            risk_score = probability * impact
            
            db.execute(
                'UPDATE risks SET project_id = ?, title = ?, description = ?, '
                'category = ?, probability = ?, impact = ?, risk_score = ?, '
                'responsible_person = ?, mitigation_plan = ?, status = ? '
                'WHERE id = ?',
                (project_id or None, title, description, category,
                 probability, impact, risk_score, responsible_person, 
                 mitigation_plan, status, id)
            )
            db.commit()
            flash('Risk updated successfully', 'success')
            return redirect(url_for('risks.index'))
        except ValueError:
            flash('Invalid probability or impact value', 'error')
        except Exception as e:
            flash('Error updating risk', 'error')
    
    return render_template('risks/form.html', risk=risk, projects=projects)

@risks_bp.route('/<int:id>/delete', methods=['POST'])
def delete(id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    db = get_db()
    risk = db.execute('SELECT * FROM risks WHERE id = ?', (id,)).fetchone()
    
    if not risk:
        flash('Risk not found', 'error')
        return redirect(url_for('risks.index'))
    
    try:
        db.execute('DELETE FROM risks WHERE id = ?', (id,))
        db.commit()
        flash('Risk deleted successfully', 'success')
    except Exception as e:
        flash('Error deleting risk', 'error')
    
    return redirect(url_for('risks.index'))

@risks_bp.route('/matrix')
def matrix():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    db = get_db()
    risks = db.execute(
        'SELECT r.*, p.name as project_name '
        'FROM risks r '
        'LEFT JOIN projects p ON r.project_id = p.id '
        'ORDER BY r.probability, r.impact'
    ).fetchall()
    
    # Group risks by probability and impact for matrix display
    matrix = {}
    for i in range(1, 6):  # probability 1-5
        matrix[i] = {}
        for j in range(1, 6):  # impact 1-5
            matrix[i][j] = []
    
    for risk in risks:
        prob = risk['probability']
        imp = risk['impact']
        if 1 <= prob <= 5 and 1 <= imp <= 5:
            matrix[prob][imp].append(risk)
    
    return render_template('risks/matrix.html', matrix=matrix)
