import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
from datetime import datetime

compliance_bp = Blueprint('compliance', __name__)

def get_db():
    """Get database connection"""
    from flask import current_app
    return current_app.get_db()

ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@compliance_bp.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    db = get_db()
    documents = db.execute(
        'SELECT cd.*, p.name as project_name '
        'FROM compliance_docs cd '
        'LEFT JOIN projects p ON cd.project_id = p.id '
        'ORDER BY cd.created_at DESC'
    ).fetchall()
    
    # Check for expiring documents
    expiring_soon = db.execute(
        'SELECT cd.*, p.name as project_name '
        'FROM compliance_docs cd '
        'LEFT JOIN projects p ON cd.project_id = p.id '
        'WHERE cd.expiry_date <= date("now", "+30 days") AND cd.expiry_date >= date("now") '
        'ORDER BY cd.expiry_date ASC'
    ).fetchall()
    
    # Get statistics
    total_docs = len(documents)
    pending_docs = len([d for d in documents if d['status'] == 'pending'])
    approved_docs = len([d for d in documents if d['status'] == 'approved'])
    expired_docs = len([d for d in documents if d['expiry_date'] and d['expiry_date'] < datetime.now().date().isoformat()])
    
    stats = {
        'total_docs': total_docs,
        'pending_docs': pending_docs,
        'approved_docs': approved_docs,
        'expired_docs': expired_docs
    }
    
    return render_template('compliance/index.html', 
                         documents=documents,
                         expiring_soon=expiring_soon,
                         stats=stats)

@compliance_bp.route('/new', methods=['GET', 'POST'])
def new():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    db = get_db()
    projects = db.execute('SELECT id, name FROM projects ORDER BY name').fetchall()
    
    if request.method == 'POST':
        project_id = request.form.get('project_id')
        title = request.form.get('title')
        document_type = request.form.get('document_type')
        status = request.form.get('status', 'pending')
        issue_date = request.form.get('issue_date')
        expiry_date = request.form.get('expiry_date')
        responsible_authority = request.form.get('responsible_authority')
        notes = request.form.get('notes')
        
        if not title:
            flash('Document title is required', 'error')
            return render_template('compliance/form.html', projects=projects)
        
        # Handle file upload
        file_path = None
        if 'document_file' in request.files:
            file = request.files['document_file']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
                filename = timestamp + filename
                file_path = os.path.join('uploads', filename)
                file.save(file_path)
        
        try:
            db.execute(
                'INSERT INTO compliance_docs (project_id, title, document_type, '
                'file_path, status, issue_date, expiry_date, responsible_authority, notes) '
                'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                (project_id or None, title, document_type, file_path, status,
                 issue_date or None, expiry_date or None, responsible_authority, notes)
            )
            db.commit()
            flash('Compliance document added successfully', 'success')
            return redirect(url_for('compliance.index'))
        except Exception as e:
            flash('Error adding document', 'error')
    
    return render_template('compliance/form.html', projects=projects)

@compliance_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
def edit(id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    db = get_db()
    document = db.execute('SELECT * FROM compliance_docs WHERE id = ?', (id,)).fetchone()
    projects = db.execute('SELECT id, name FROM projects ORDER BY name').fetchall()
    
    if not document:
        flash('Document not found', 'error')
        return redirect(url_for('compliance.index'))
    
    if request.method == 'POST':
        project_id = request.form.get('project_id')
        title = request.form.get('title')
        document_type = request.form.get('document_type')
        status = request.form.get('status')
        issue_date = request.form.get('issue_date')
        expiry_date = request.form.get('expiry_date')
        responsible_authority = request.form.get('responsible_authority')
        notes = request.form.get('notes')
        
        if not title:
            flash('Document title is required', 'error')
            return render_template('compliance/form.html', document=document, projects=projects)
        
        # Handle file upload
        file_path = document['file_path']  # Keep existing path
        if 'document_file' in request.files:
            file = request.files['document_file']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
                filename = timestamp + filename
                file_path = os.path.join('uploads', filename)
                file.save(file_path)
        
        try:
            db.execute(
                'UPDATE compliance_docs SET project_id = ?, title = ?, '
                'document_type = ?, file_path = ?, status = ?, issue_date = ?, '
                'expiry_date = ?, responsible_authority = ?, notes = ? '
                'WHERE id = ?',
                (project_id or None, title, document_type, file_path, status,
                 issue_date or None, expiry_date or None, responsible_authority, notes, id)
            )
            db.commit()
            flash('Document updated successfully', 'success')
            return redirect(url_for('compliance.index'))
        except Exception as e:
            flash('Error updating document', 'error')
    
    return render_template('compliance/form.html', document=document, projects=projects)

@compliance_bp.route('/<int:id>/delete', methods=['POST'])
def delete(id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    db = get_db()
    document = db.execute('SELECT * FROM compliance_docs WHERE id = ?', (id,)).fetchone()
    
    if not document:
        flash('Document not found', 'error')
        return redirect(url_for('compliance.index'))
    
    try:
        # Delete associated file if exists
        if document['file_path'] and os.path.exists(document['file_path']):
            os.remove(document['file_path'])
        
        db.execute('DELETE FROM compliance_docs WHERE id = ?', (id,))
        db.commit()
        flash('Document deleted successfully', 'success')
    except Exception as e:
        flash('Error deleting document', 'error')
    
    return redirect(url_for('compliance.index'))
