import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
from datetime import datetime

permits_bp = Blueprint('permits', __name__)

def get_db():
    """Get database connection"""
    from flask import current_app
    return current_app.get_db()

ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@permits_bp.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    db = get_db()
    permits = db.execute(
        'SELECT p.*, pr.name as project_name '
        'FROM permits p '
        'LEFT JOIN projects pr ON p.project_id = pr.id '
        'ORDER BY p.created_at DESC'
    ).fetchall()
    
    # Check for expiring permits
    expiring_soon = db.execute(
        'SELECT p.*, pr.name as project_name '
        'FROM permits p '
        'LEFT JOIN projects pr ON p.project_id = pr.id '
        'WHERE p.expiry_date <= date("now", "+30 days") AND p.expiry_date >= date("now") '
        'ORDER BY p.expiry_date ASC'
    ).fetchall()
    
    # Calculate threshold date for 30 days from now
    from datetime import datetime, timedelta
    threshold_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
    
    return render_template('permits/index.html', 
                         permits=permits,
                         expiring_soon=expiring_soon,
                         threshold_date=threshold_date)

@permits_bp.route('/new', methods=['GET', 'POST'])
def new():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    db = get_db()
    projects = db.execute('SELECT id, name FROM projects ORDER BY name').fetchall()
    
    if request.method == 'POST':
        project_id = request.form.get('project_id')
        name = request.form.get('name')
        type_field = request.form.get('type')
        status = request.form.get('status', 'pending')
        issue_date = request.form.get('issue_date')
        expiry_date = request.form.get('expiry_date')
        issuing_authority = request.form.get('issuing_authority')
        
        if not name:
            flash('Permit name is required', 'error')
            return render_template('permits/form.html', projects=projects)
        
        # Handle file upload
        document_path = None
        if 'document' in request.files:
            file = request.files['document']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
                filename = timestamp + filename
                file_path = os.path.join('uploads', filename)
                file.save(file_path)
                document_path = file_path
        
        try:
            db.execute(
                'INSERT INTO permits (project_id, name, type, status, '
                'issue_date, expiry_date, issuing_authority, document_path) '
                'VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                (project_id or None, name, type_field, status,
                 issue_date or None, expiry_date or None,
                 issuing_authority, document_path)
            )
            db.commit()
            flash('Permit added successfully', 'success')
            return redirect(url_for('permits.index'))
        except Exception as e:
            flash('Error adding permit', 'error')
    
    return render_template('permits/form.html', projects=projects)

@permits_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
def edit(id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    db = get_db()
    permit = db.execute('SELECT * FROM permits WHERE id = ?', (id,)).fetchone()
    projects = db.execute('SELECT id, name FROM projects ORDER BY name').fetchall()
    
    if not permit:
        flash('Permit not found', 'error')
        return redirect(url_for('permits.index'))
    
    if request.method == 'POST':
        project_id = request.form.get('project_id')
        name = request.form.get('name')
        type_field = request.form.get('type')
        status = request.form.get('status')
        issue_date = request.form.get('issue_date')
        expiry_date = request.form.get('expiry_date')
        issuing_authority = request.form.get('issuing_authority')
        
        if not name:
            flash('Permit name is required', 'error')
            return render_template('permits/form.html', permit=permit, projects=projects)
        
        # Handle file upload
        document_path = permit['document_path']  # Keep existing path
        if 'document' in request.files:
            file = request.files['document']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
                filename = timestamp + filename
                file_path = os.path.join('uploads', filename)
                file.save(file_path)
                document_path = file_path
        
        try:
            db.execute(
                'UPDATE permits SET project_id = ?, name = ?, type = ?, status = ?, '
                'issue_date = ?, expiry_date = ?, issuing_authority = ?, document_path = ? '
                'WHERE id = ?',
                (project_id or None, name, type_field, status,
                 issue_date or None, expiry_date or None,
                 issuing_authority, document_path, id)
            )
            db.commit()
            flash('Permit updated successfully', 'success')
            return redirect(url_for('permits.index'))
        except Exception as e:
            flash('Error updating permit', 'error')
    
    return render_template('permits/form.html', permit=permit, projects=projects)

@permits_bp.route('/<int:id>/delete', methods=['POST'])
def delete(id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    db = get_db()
    permit = db.execute('SELECT * FROM permits WHERE id = ?', (id,)).fetchone()
    
    if not permit:
        flash('Permit not found', 'error')
        return redirect(url_for('permits.index'))
    
    try:
        # Delete associated file if exists
        if permit['document_path'] and os.path.exists(permit['document_path']):
            os.remove(permit['document_path'])
        
        db.execute('DELETE FROM permits WHERE id = ?', (id,))
        db.commit()
        flash('Permit deleted successfully', 'success')
    except Exception as e:
        flash('Error deleting permit', 'error')
    
    return redirect(url_for('permits.index'))
