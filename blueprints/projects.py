from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from datetime import datetime
from utils import log_audit

projects_bp = Blueprint('projects', __name__)

def get_db():
    """Get database connection"""
    from flask import current_app
    return current_app.get_db()

@projects_bp.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    db = get_db()
    projects = db.execute(
        'SELECT * FROM projects ORDER BY created_at DESC'
    ).fetchall()
    
    return render_template('projects/index.html', projects=projects)

@projects_bp.route('/new', methods=['GET', 'POST'])
def new():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        budget = request.form.get('budget', 0)
        
        if not name:
            flash('Project name is required', 'error')
            return render_template('projects/form.html')
        
        try:
            db = get_db()
            cursor = db.execute(
                'INSERT INTO projects (name, description, start_date, end_date, budget, user_id) '
                'VALUES (?, ?, ?, ?, ?, ?)',
                (name, description, start_date or None, end_date or None, 
                 float(budget) if budget else 0, session['user_id'])
            )
            db.commit()
            
            # Log audit
            log_audit('projects', cursor.lastrowid, 'INSERT', {}, {
                'name': name, 'description': description, 
                'start_date': start_date, 'end_date': end_date, 'budget': budget
            }, session['user_id'])
            
            flash('Project created successfully', 'success')
            return redirect(url_for('projects.index'))
        except Exception as e:
            flash('Error creating project', 'error')
    
    return render_template('projects/form.html')

@projects_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
def edit(id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    db = get_db()
    project = db.execute('SELECT * FROM projects WHERE id = ?', (id,)).fetchone()
    
    if not project:
        flash('Project not found', 'error')
        return redirect(url_for('projects.index'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        budget = request.form.get('budget', 0)
        status = request.form.get('status')
        
        if not name:
            flash('Project name is required', 'error')
            return render_template('projects/form.html', project=project)
        
        try:
            old_values = dict(project)
            
            db.execute(
                'UPDATE projects SET name = ?, description = ?, start_date = ?, '
                'end_date = ?, budget = ?, status = ? WHERE id = ?',
                (name, description, start_date or None, end_date or None,
                 float(budget) if budget else 0, status, id)
            )
            db.commit()
            
            # Log audit
            new_values = {
                'name': name, 'description': description,
                'start_date': start_date, 'end_date': end_date,
                'budget': budget, 'status': status
            }
            log_audit('projects', id, 'UPDATE', old_values, new_values, session['user_id'])
            
            flash('Project updated successfully', 'success')
            return redirect(url_for('projects.index'))
        except Exception as e:
            flash('Error updating project', 'error')
    
    return render_template('projects/form.html', project=project)

@projects_bp.route('/<int:id>/delete', methods=['POST'])
def delete(id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    db = get_db()
    project = db.execute('SELECT * FROM projects WHERE id = ?', (id,)).fetchone()
    
    if not project:
        flash('Project not found', 'error')
        return redirect(url_for('projects.index'))
    
    try:
        # Log audit before deletion
        log_audit('projects', id, 'DELETE', dict(project), {}, session['user_id'])
        
        db.execute('DELETE FROM projects WHERE id = ?', (id,))
        db.commit()
        flash('Project deleted successfully', 'success')
    except Exception as e:
        flash('Error deleting project', 'error')
    
    return redirect(url_for('projects.index'))
