from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from subscription_utils import require_pro

sustainability_bp = Blueprint('sustainability', __name__)

def get_db():
    """Get database connection"""
    from flask import current_app
    return current_app.get_db()

@sustainability_bp.route('/')
@require_pro
def index():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    db = get_db()
    
    # Get material usage logs with project and material info
    material_logs = db.execute(
        'SELECT ml.*, p.name as project_name, m.name as material_name '
        'FROM material_logs ml '
        'LEFT JOIN projects p ON ml.project_id = p.id '
        'LEFT JOIN materials m ON ml.material_id = m.id '
        'ORDER BY ml.date_used DESC'
    ).fetchall()
    
    # Calculate total emissions by project
    project_emissions = db.execute(
        'SELECT p.name as project_name, SUM(ml.total_emissions) as total_emissions '
        'FROM material_logs ml '
        'JOIN projects p ON ml.project_id = p.id '
        'GROUP BY p.id, p.name '
        'ORDER BY total_emissions DESC'
    ).fetchall()
    
    # Calculate total emissions by material category
    category_emissions = db.execute(
        'SELECT m.category, SUM(ml.total_emissions) as total_emissions '
        'FROM material_logs ml '
        'JOIN materials m ON ml.material_id = m.id '
        'WHERE m.category IS NOT NULL '
        'GROUP BY m.category '
        'ORDER BY total_emissions DESC'
    ).fetchall()
    
    return render_template('sustainability/index.html',
                         material_logs=material_logs,
                         project_emissions=project_emissions,
                         category_emissions=category_emissions)

@sustainability_bp.route('/materials')
def materials():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    db = get_db()
    materials = db.execute(
        'SELECT m.*, s.name as supplier_name '
        'FROM materials m '
        'LEFT JOIN suppliers s ON m.supplier_id = s.id '
        'ORDER BY m.category, m.name'
    ).fetchall()
    
    return render_template('sustainability/materials.html', materials=materials)

@sustainability_bp.route('/materials/new', methods=['GET', 'POST'])
def new_material():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    db = get_db()
    suppliers = db.execute('SELECT id, name FROM suppliers ORDER BY name').fetchall()
    
    if request.method == 'POST':
        name = request.form.get('name')
        category = request.form.get('category')
        unit = request.form.get('unit')
        carbon_emissions_per_unit = request.form.get('carbon_emissions_per_unit', 0)
        cost_per_unit = request.form.get('cost_per_unit', 0)
        supplier_id = request.form.get('supplier_id') or None
        
        if not name:
            flash('Material name is required', 'error')
            return render_template('sustainability/material_form.html', suppliers=suppliers)
        
        try:
            db.execute(
                'INSERT INTO materials (name, category, unit, carbon_emissions_per_unit, '
                'cost_per_unit, supplier_id) '
                'VALUES (?, ?, ?, ?, ?, ?)',
                (name, category, unit,
                 float(carbon_emissions_per_unit) if carbon_emissions_per_unit else 0,
                 float(cost_per_unit) if cost_per_unit else 0,
                 supplier_id)
            )
            db.commit()
            flash('Material added successfully', 'success')
            return redirect(url_for('sustainability.materials'))
        except Exception as e:
            flash('Error adding material', 'error')
    
    return render_template('sustainability/material_form.html', suppliers=suppliers)

@sustainability_bp.route('/log', methods=['GET', 'POST'])
def log_usage():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    db = get_db()
    projects = db.execute('SELECT id, name FROM projects ORDER BY name').fetchall()
    materials = db.execute('SELECT id, name, carbon_emissions_per_unit, cost_per_unit FROM materials ORDER BY name').fetchall()
    
    if request.method == 'POST':
        project_id = request.form.get('project_id')
        material_id = request.form.get('material_id')
        quantity = request.form.get('quantity')
        date_used = request.form.get('date_used')
        notes = request.form.get('notes')
        
        if not all([material_id, quantity]):
            flash('Material and quantity are required', 'error')
            return render_template('sustainability/log_form.html', 
                                 projects=projects, materials=materials)
        
        try:
            quantity = float(quantity)
            
            # Get material emissions and cost per unit
            material = db.execute(
                'SELECT carbon_emissions_per_unit, cost_per_unit FROM materials WHERE id = ?',
                (material_id,)
            ).fetchone()
            
            total_emissions = quantity * material['carbon_emissions_per_unit']
            total_cost = quantity * material['cost_per_unit']
            
            db.execute(
                'INSERT INTO material_logs (project_id, material_id, quantity, '
                'date_used, total_emissions, total_cost, notes) '
                'VALUES (?, ?, ?, ?, ?, ?, ?)',
                (project_id or None, material_id, quantity,
                 date_used or None, total_emissions, total_cost, notes)
            )
            db.commit()
            flash('Material usage logged successfully', 'success')
            return redirect(url_for('sustainability.index'))
        except ValueError:
            flash('Invalid quantity', 'error')
        except Exception as e:
            flash('Error logging material usage', 'error')
    
    return render_template('sustainability/log_form.html', 
                         projects=projects, materials=materials)

@sustainability_bp.route('/report/<int:project_id>')
def project_report(project_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    db = get_db()
    
    # Get project info
    project = db.execute('SELECT * FROM projects WHERE id = ?', (project_id,)).fetchone()
    if not project:
        flash('Project not found', 'error')
        return redirect(url_for('sustainability.index'))
    
    # Get material usage for this project
    material_usage = db.execute(
        'SELECT ml.*, m.name as material_name, m.category '
        'FROM material_logs ml '
        'JOIN materials m ON ml.material_id = m.id '
        'WHERE ml.project_id = ? '
        'ORDER BY ml.date_used DESC',
        (project_id,)
    ).fetchall()
    
    # Calculate totals
    total_emissions = sum(log['total_emissions'] for log in material_usage)
    total_cost = sum(log['total_cost'] for log in material_usage)
    
    # Group by category
    category_totals = {}
    for log in material_usage:
        category = log['category'] or 'Uncategorized'
        if category not in category_totals:
            category_totals[category] = {'emissions': 0, 'cost': 0}
        category_totals[category]['emissions'] += log['total_emissions']
        category_totals[category]['cost'] += log['total_cost']
    
    return render_template('sustainability/project_report.html',
                         project=project,
                         material_usage=material_usage,
                         total_emissions=total_emissions,
                         total_cost=total_cost,
                         category_totals=category_totals)
