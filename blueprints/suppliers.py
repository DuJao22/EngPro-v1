from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import json

suppliers_bp = Blueprint('suppliers', __name__)

def get_db():
    """Get database connection"""
    from flask import current_app
    return current_app.get_db()

@suppliers_bp.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    db = get_db()
    suppliers = db.execute(
        'SELECT * FROM suppliers ORDER BY name'
    ).fetchall()
    
    # Get purchase order statistics
    for supplier in suppliers:
        orders_count = db.execute(
            'SELECT COUNT(*) as count FROM purchase_orders WHERE supplier_id = ?',
            (supplier['id'],)
        ).fetchone()['count']
        
        total_amount = db.execute(
            'SELECT SUM(total_amount) as total FROM purchase_orders WHERE supplier_id = ?',
            (supplier['id'],)
        ).fetchone()['total'] or 0
        
        supplier = dict(supplier)
        supplier['orders_count'] = orders_count
        supplier['total_amount'] = total_amount
    
    return render_template('suppliers/index.html', suppliers=suppliers)

@suppliers_bp.route('/new', methods=['GET', 'POST'])
def new():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        cnpj_id = request.form.get('cnpj_id')
        contact_person = request.form.get('contact_person')
        email = request.form.get('email')
        phone = request.form.get('phone')
        address = request.form.get('address')
        category = request.form.get('category')
        rating = request.form.get('rating', 0)
        
        if not name:
            flash('Supplier name is required', 'error')
            return render_template('suppliers/form.html')
        
        try:
            db = get_db()
            db.execute(
                'INSERT INTO suppliers (name, cnpj_id, contact_person, email, '
                'phone, address, category, rating) '
                'VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                (name, cnpj_id, contact_person, email, phone, address, 
                 category, float(rating) if rating else 0)
            )
            db.commit()
            flash('Supplier added successfully', 'success')
            return redirect(url_for('suppliers.index'))
        except Exception as e:
            flash('Error adding supplier', 'error')
    
    return render_template('suppliers/form.html')

@suppliers_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
def edit(id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    db = get_db()
    supplier = db.execute('SELECT * FROM suppliers WHERE id = ?', (id,)).fetchone()
    
    if not supplier:
        flash('Supplier not found', 'error')
        return redirect(url_for('suppliers.index'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        cnpj_id = request.form.get('cnpj_id')
        contact_person = request.form.get('contact_person')
        email = request.form.get('email')
        phone = request.form.get('phone')
        address = request.form.get('address')
        category = request.form.get('category')
        rating = request.form.get('rating', 0)
        
        if not name:
            flash('Supplier name is required', 'error')
            return render_template('suppliers/form.html', supplier=supplier)
        
        try:
            db.execute(
                'UPDATE suppliers SET name = ?, cnpj_id = ?, contact_person = ?, '
                'email = ?, phone = ?, address = ?, category = ?, rating = ? '
                'WHERE id = ?',
                (name, cnpj_id, contact_person, email, phone, address,
                 category, float(rating) if rating else 0, id)
            )
            db.commit()
            flash('Supplier updated successfully', 'success')
            return redirect(url_for('suppliers.index'))
        except Exception as e:
            flash('Error updating supplier', 'error')
    
    return render_template('suppliers/form.html', supplier=supplier)

@suppliers_bp.route('/<int:id>/delete', methods=['POST'])
def delete(id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    db = get_db()
    supplier = db.execute('SELECT * FROM suppliers WHERE id = ?', (id,)).fetchone()
    
    if not supplier:
        flash('Supplier not found', 'error')
        return redirect(url_for('suppliers.index'))
    
    try:
        db.execute('DELETE FROM suppliers WHERE id = ?', (id,))
        db.commit()
        flash('Supplier deleted successfully', 'success')
    except Exception as e:
        flash('Error deleting supplier', 'error')
    
    return redirect(url_for('suppliers.index'))

@suppliers_bp.route('/orders')
def orders():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    db = get_db()
    orders = db.execute(
        'SELECT po.*, p.name as project_name, s.name as supplier_name '
        'FROM purchase_orders po '
        'LEFT JOIN projects p ON po.project_id = p.id '
        'LEFT JOIN suppliers s ON po.supplier_id = s.id '
        'ORDER BY po.created_at DESC'
    ).fetchall()
    
    return render_template('suppliers/orders.html', orders=orders)

@suppliers_bp.route('/orders/new', methods=['GET', 'POST'])
def new_order():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    db = get_db()
    projects = db.execute('SELECT id, name FROM projects ORDER BY name').fetchall()
    suppliers = db.execute('SELECT id, name FROM suppliers ORDER BY name').fetchall()
    
    if request.method == 'POST':
        project_id = request.form.get('project_id')
        supplier_id = request.form.get('supplier_id')
        order_number = request.form.get('order_number')
        order_date = request.form.get('order_date')
        expected_delivery = request.form.get('expected_delivery')
        total_amount = request.form.get('total_amount', 0)
        items = request.form.get('items', '[]')
        
        if not all([supplier_id, order_number]):
            flash('Supplier and order number are required', 'error')
            return render_template('suppliers/order_form.html', 
                                 projects=projects, suppliers=suppliers)
        
        try:
            db.execute(
                'INSERT INTO purchase_orders (project_id, supplier_id, order_number, '
                'order_date, expected_delivery, total_amount, items) '
                'VALUES (?, ?, ?, ?, ?, ?, ?)',
                (project_id or None, supplier_id, order_number,
                 order_date or None, expected_delivery or None,
                 float(total_amount) if total_amount else 0, items)
            )
            db.commit()
            flash('Purchase order created successfully', 'success')
            return redirect(url_for('suppliers.orders'))
        except Exception as e:
            flash('Error creating purchase order', 'error')
    
    return render_template('suppliers/order_form.html', 
                         projects=projects, suppliers=suppliers)
