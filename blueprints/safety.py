from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from datetime import datetime

safety_bp = Blueprint('safety', __name__)

def get_db():
    """Get database connection"""
    from flask import current_app
    return current_app.get_db()

@safety_bp.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    db = get_db()
    incidents = db.execute(
        'SELECT i.*, p.name as project_name '
        'FROM incidents i '
        'LEFT JOIN projects p ON i.project_id = p.id '
        'ORDER BY i.created_at DESC'
    ).fetchall()
    
    # Get statistics
    stats = {
        'total_incidents': len(incidents),
        'open_incidents': len([i for i in incidents if i['status'] == 'open']),
        'high_severity': len([i for i in incidents if i['severity'] == 'high']),
        'this_month': len([i for i in incidents if i['date_occurred'] and 
                          i['date_occurred'].startswith(datetime.now().strftime('%Y-%m'))])
    }
    
    return render_template('safety/index.html', incidents=incidents, stats=stats)

@safety_bp.route('/new', methods=['GET', 'POST'])
def new():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    db = get_db()
    projects = db.execute('SELECT id, name FROM projects ORDER BY name').fetchall()
    
    if request.method == 'POST':
        project_id = request.form.get('project_id')
        title = request.form.get('title')
        description = request.form.get('description')
        severity = request.form.get('severity', 'low')
        date_occurred = request.form.get('date_occurred')
        location = request.form.get('location')
        reported_by = request.form.get('reported_by')
        
        if not title:
            flash('Incident title is required', 'error')
            return render_template('safety/form.html', projects=projects)
        
        try:
            db.execute(
                'INSERT INTO incidents (project_id, title, description, severity, '
                'date_occurred, location, reported_by) '
                'VALUES (?, ?, ?, ?, ?, ?, ?)',
                (project_id or None, title, description, severity,
                 date_occurred or None, location, reported_by)
            )
            db.commit()
            flash('Incident reported successfully', 'success')
            return redirect(url_for('safety.index'))
        except Exception as e:
            flash('Error reporting incident', 'error')
    
    return render_template('safety/form.html', projects=projects)

@safety_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
def edit(id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    db = get_db()
    incident = db.execute('SELECT * FROM incidents WHERE id = ?', (id,)).fetchone()
    projects = db.execute('SELECT id, name FROM projects ORDER BY name').fetchall()
    
    if not incident:
        flash('Incident not found', 'error')
        return redirect(url_for('safety.index'))
    
    if request.method == 'POST':
        project_id = request.form.get('project_id')
        title = request.form.get('title')
        description = request.form.get('description')
        severity = request.form.get('severity')
        date_occurred = request.form.get('date_occurred')
        location = request.form.get('location')
        reported_by = request.form.get('reported_by')
        status = request.form.get('status')
        
        if not title:
            flash('Incident title is required', 'error')
            return render_template('safety/form.html', incident=incident, projects=projects)
        
        try:
            db.execute(
                'UPDATE incidents SET project_id = ?, title = ?, description = ?, '
                'severity = ?, date_occurred = ?, location = ?, reported_by = ?, status = ? '
                'WHERE id = ?',
                (project_id or None, title, description, severity,
                 date_occurred or None, location, reported_by, status, id)
            )
            db.commit()
            flash('Incident updated successfully', 'success')
            return redirect(url_for('safety.index'))
        except Exception as e:
            flash('Error updating incident', 'error')
    
    return render_template('safety/form.html', incident=incident, projects=projects)

@safety_bp.route('/<int:id>/delete', methods=['POST'])
def delete(id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    db = get_db()
    incident = db.execute('SELECT * FROM incidents WHERE id = ?', (id,)).fetchone()
    
    if not incident:
        flash('Incident not found', 'error')
        return redirect(url_for('safety.index'))
    
    try:
        db.execute('DELETE FROM incidents WHERE id = ?', (id,))
        db.commit()
        flash('Incident deleted successfully', 'success')
    except Exception as e:
        flash('Error deleting incident', 'error')
    
    return redirect(url_for('safety.index'))
