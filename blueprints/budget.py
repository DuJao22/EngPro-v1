from flask import Blueprint, render_template, request, redirect, url_for, flash, session

budget_bp = Blueprint('budget', __name__)

def get_db():
    """Get database connection"""
    from flask import current_app
    return current_app.get_db()

@budget_bp.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    db = get_db()
    
    # Get budget items with project and supplier info
    budget_items = db.execute(
        'SELECT b.*, p.name as project_name, s.name as supplier_name '
        'FROM budget_items b '
        'LEFT JOIN projects p ON b.project_id = p.id '
        'LEFT JOIN suppliers s ON b.supplier_id = s.id '
        'ORDER BY b.created_at DESC'
    ).fetchall()
    
    # Get projects for filter
    projects = db.execute('SELECT id, name FROM projects ORDER BY name').fetchall()
    
    # Calculate totals by category
    totals = db.execute(
        'SELECT category, SUM(total_cost) as total '
        'FROM budget_items GROUP BY category ORDER BY total DESC'
    ).fetchall()
    
    return render_template('budget/index.html', 
                         budget_items=budget_items,
                         projects=projects,
                         totals=totals)

@budget_bp.route('/new', methods=['GET', 'POST'])
def new():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    db = get_db()
    projects = db.execute('SELECT id, name FROM projects ORDER BY name').fetchall()
    suppliers = db.execute('SELECT id, name FROM suppliers ORDER BY name').fetchall()
    
    if request.method == 'POST':
        project_id = request.form.get('project_id')
        category = request.form.get('category')
        description = request.form.get('description')
        quantity = request.form.get('quantity', 1)
        unit_cost = request.form.get('unit_cost')
        supplier_id = request.form.get('supplier_id') or None
        
        if not all([category, unit_cost]):
            flash('Category and unit cost are required', 'error')
            return render_template('budget/form.html', projects=projects, suppliers=suppliers)
        
        try:
            quantity = float(quantity)
            unit_cost = float(unit_cost)
            total_cost = quantity * unit_cost
            
            db.execute(
                'INSERT INTO budget_items (project_id, category, description, '
                'quantity, unit_cost, total_cost, supplier_id) '
                'VALUES (?, ?, ?, ?, ?, ?, ?)',
                (project_id or None, category, description, 
                 quantity, unit_cost, total_cost, supplier_id)
            )
            db.commit()
            flash('Budget item added successfully', 'success')
            return redirect(url_for('budget.index'))
        except ValueError:
            flash('Invalid quantity or unit cost', 'error')
        except Exception as e:
            flash('Error adding budget item', 'error')
    
    return render_template('budget/form.html', projects=projects, suppliers=suppliers)

@budget_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
def edit(id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    db = get_db()
    budget_item = db.execute('SELECT * FROM budget_items WHERE id = ?', (id,)).fetchone()
    projects = db.execute('SELECT id, name FROM projects ORDER BY name').fetchall()
    suppliers = db.execute('SELECT id, name FROM suppliers ORDER BY name').fetchall()
    
    if not budget_item:
        flash('Budget item not found', 'error')
        return redirect(url_for('budget.index'))
    
    if request.method == 'POST':
        project_id = request.form.get('project_id')
        category = request.form.get('category')
        description = request.form.get('description')
        quantity = request.form.get('quantity', 1)
        unit_cost = request.form.get('unit_cost')
        supplier_id = request.form.get('supplier_id') or None
        
        if not all([category, unit_cost]):
            flash('Category and unit cost are required', 'error')
            return render_template('budget/form.html', 
                                 budget_item=budget_item,
                                 projects=projects, 
                                 suppliers=suppliers)
        
        try:
            quantity = float(quantity)
            unit_cost = float(unit_cost)
            total_cost = quantity * unit_cost
            
            db.execute(
                'UPDATE budget_items SET project_id = ?, category = ?, '
                'description = ?, quantity = ?, unit_cost = ?, '
                'total_cost = ?, supplier_id = ? WHERE id = ?',
                (project_id or None, category, description,
                 quantity, unit_cost, total_cost, supplier_id, id)
            )
            db.commit()
            flash('Budget item updated successfully', 'success')
            return redirect(url_for('budget.index'))
        except ValueError:
            flash('Invalid quantity or unit cost', 'error')
        except Exception as e:
            flash('Error updating budget item', 'error')
    
    return render_template('budget/form.html',
                         budget_item=budget_item,
                         projects=projects,
                         suppliers=suppliers)

@budget_bp.route('/<int:id>/delete', methods=['POST'])
def delete(id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    db = get_db()
    budget_item = db.execute('SELECT * FROM budget_items WHERE id = ?', (id,)).fetchone()
    
    if not budget_item:
        flash('Budget item not found', 'error')
        return redirect(url_for('budget.index'))
    
    try:
        db.execute('DELETE FROM budget_items WHERE id = ?', (id,))
        db.commit()
        flash('Budget item deleted successfully', 'success')
    except Exception as e:
        flash('Error deleting budget item', 'error')
    
    return redirect(url_for('budget.index'))
