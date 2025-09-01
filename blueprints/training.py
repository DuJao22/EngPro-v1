from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from datetime import datetime, timedelta
import os
from werkzeug.utils import secure_filename

training_bp = Blueprint('training', __name__)

def get_db():
    """Get database connection"""
    from flask import current_app
    return current_app.get_db()

ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@training_bp.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    db = get_db()
    trainings = db.execute(
        'SELECT * FROM trainings ORDER BY title'
    ).fetchall()
    
    # Get training statistics
    for training in trainings:
        completed_count = db.execute(
            'SELECT COUNT(*) as count FROM worker_trainings WHERE training_id = ?',
            (training['id'],)
        ).fetchone()['count']
        
        training = dict(training)
        training['completed_count'] = completed_count
    
    return render_template('training/index.html', trainings=trainings)

@training_bp.route('/workers')
def workers():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    db = get_db()
    workers = db.execute(
        'SELECT * FROM workers ORDER BY name'
    ).fetchall()
    
    # Get worker training status
    for worker in workers:
        total_trainings = db.execute(
            'SELECT COUNT(*) as count FROM worker_trainings WHERE worker_id = ?',
            (worker['id'],)
        ).fetchone()['count']
        
        expiring_soon = db.execute(
            'SELECT COUNT(*) as count FROM worker_trainings '
            'WHERE worker_id = ? AND expiry_date <= date("now", "+30 days") '
            'AND expiry_date >= date("now")',
            (worker['id'],)
        ).fetchone()['count']
        
        worker = dict(worker)
        worker['total_trainings'] = total_trainings
        worker['expiring_soon'] = expiring_soon
    
    return render_template('training/workers.html', workers=workers)

@training_bp.route('/new', methods=['GET', 'POST'])
def new():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        category = request.form.get('category')
        duration_hours = request.form.get('duration_hours', 0)
        validity_months = request.form.get('validity_months', 12)
        
        if not title:
            flash('Training title is required', 'error')
            return render_template('training/form.html')
        
        try:
            db = get_db()
            db.execute(
                'INSERT INTO trainings (title, description, category, '
                'duration_hours, validity_months) '
                'VALUES (?, ?, ?, ?, ?)',
                (title, description, category,
                 int(duration_hours) if duration_hours else 0,
                 int(validity_months) if validity_months else 12)
            )
            db.commit()
            flash('Training added successfully', 'success')
            return redirect(url_for('training.index'))
        except Exception as e:
            flash('Error adding training', 'error')
    
    return render_template('training/form.html')

@training_bp.route('/workers/new', methods=['GET', 'POST'])
def new_worker():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        role = request.form.get('role')
        email = request.form.get('email')
        phone = request.form.get('phone')
        hire_date = request.form.get('hire_date')
        
        if not name:
            flash('Worker name is required', 'error')
            return render_template('training/worker_form.html')
        
        try:
            db = get_db()
            db.execute(
                'INSERT INTO workers (name, role, email, phone, hire_date) '
                'VALUES (?, ?, ?, ?, ?)',
                (name, role, email, phone, hire_date or None)
            )
            db.commit()
            flash('Worker added successfully', 'success')
            return redirect(url_for('training.workers'))
        except Exception as e:
            flash('Error adding worker', 'error')
    
    return render_template('training/worker_form.html')

@training_bp.route('/workers/<int:worker_id>/edit', methods=['GET', 'POST'])
def edit_worker(worker_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    db = get_db()
    worker = db.execute('SELECT * FROM workers WHERE id = ?', (worker_id,)).fetchone()
    
    if not worker:
        flash('Trabalhador não encontrado', 'error')
        return redirect(url_for('training.workers'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        role = request.form.get('role')
        email = request.form.get('email')
        phone = request.form.get('phone')
        hire_date = request.form.get('hire_date')
        status = request.form.get('status')
        
        if not name:
            flash('Nome do trabalhador é obrigatório', 'error')
            return render_template('training/worker_form.html', worker=worker)
        
        try:
            db.execute(
                'UPDATE workers SET name = ?, role = ?, email = ?, phone = ?, hire_date = ?, status = ? '
                'WHERE id = ?',
                (name, role, email, phone, hire_date or None, status, worker_id)
            )
            db.commit()
            flash('Trabalhador atualizado com sucesso', 'success')
            return redirect(url_for('training.workers'))
        except Exception as e:
            flash('Erro ao atualizar trabalhador', 'error')
    
    return render_template('training/worker_form.html', worker=worker)

@training_bp.route('/workers/<int:worker_id>')
def worker_details(worker_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    db = get_db()
    worker = db.execute('SELECT * FROM workers WHERE id = ?', (worker_id,)).fetchone()
    
    if not worker:
        flash('Trabalhador não encontrado', 'error')
        return redirect(url_for('training.workers'))
    
    # Get worker trainings
    trainings = db.execute(
        'SELECT wt.*, t.title as training_title, t.validity_months '
        'FROM worker_trainings wt '
        'JOIN trainings t ON wt.training_id = t.id '
        'WHERE wt.worker_id = ? '
        'ORDER BY wt.completion_date DESC',
        (worker_id,)
    ).fetchall()
    
    return render_template('training/worker_details.html', worker=worker, trainings=trainings)

@training_bp.route('/assign', methods=['GET', 'POST'])
def assign():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    db = get_db()
    workers = db.execute('SELECT id, name FROM workers ORDER BY name').fetchall()
    trainings = db.execute('SELECT id, title, validity_months FROM trainings ORDER BY title').fetchall()
    
    if request.method == 'POST':
        worker_id = request.form.get('worker_id')
        training_id = request.form.get('training_id')
        completion_date = request.form.get('completion_date')
        
        if not all([worker_id, training_id, completion_date]):
            flash('All fields are required', 'error')
            return render_template('training/assign_form.html', 
                                 workers=workers, trainings=trainings)
        
        # Calculate expiry date
        training = db.execute(
            'SELECT validity_months FROM trainings WHERE id = ?',
            (training_id,)
        ).fetchone()
        
        completion_dt = datetime.strptime(completion_date, '%Y-%m-%d')
        expiry_dt = completion_dt + timedelta(days=training['validity_months'] * 30)
        expiry_date = expiry_dt.strftime('%Y-%m-%d')
        
        # Handle certificate upload
        certificate_path = None
        if 'certificate' in request.files:
            file = request.files['certificate']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
                filename = timestamp + filename
                file_path = os.path.join('uploads', filename)
                file.save(file_path)
                certificate_path = file_path
        
        try:
            db.execute(
                'INSERT INTO worker_trainings (worker_id, training_id, '
                'completion_date, expiry_date, certificate_path) '
                'VALUES (?, ?, ?, ?, ?)',
                (worker_id, training_id, completion_date, expiry_date, certificate_path)
            )
            db.commit()
            flash('Training assigned successfully', 'success')
            return redirect(url_for('training.workers'))
        except Exception as e:
            flash('Error assigning training', 'error')
    
    return render_template('training/assign_form.html', 
                         workers=workers, trainings=trainings)

@training_bp.route('/expiring')
def expiring():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    db = get_db()
    expiring_trainings = db.execute(
        'SELECT wt.*, w.name as worker_name, t.title as training_title '
        'FROM worker_trainings wt '
        'JOIN workers w ON wt.worker_id = w.id '
        'JOIN trainings t ON wt.training_id = t.id '
        'WHERE wt.expiry_date <= date("now", "+30 days") AND wt.expiry_date >= date("now") '
        'ORDER BY wt.expiry_date ASC'
    ).fetchall()
    
    return render_template('training/expiring.html', expiring_trainings=expiring_trainings)
