import hashlib
import sqlite3
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, g
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint('auth', __name__)

def get_db():
    """Get database connection"""
    from flask import current_app
    return current_app.get_db()

@auth_bp.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard.index'))
    return redirect(url_for('auth.login'))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Username and password are required', 'error')
            return render_template('login.html')
        
        db = get_db()
        user = db.execute(
            'SELECT * FROM users WHERE username = ?', (username,)
        ).fetchone()
        
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['subscription_plan'] = user['subscription_plan']
            session['subscription_status'] = user['subscription_status']
            session['trial_end_date'] = user['trial_end_date']
            flash(f'Welcome, {username}!', 'success')
            return redirect(url_for('dashboard.index'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Basic validation
        if not all([username, email, password, confirm_password]):
            flash('All fields are required', 'error')
            return render_template('login.html')
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('login.html')
        
        if password and len(password) < 6:
            flash('Password must be at least 6 characters long', 'error')
            return render_template('login.html')
        
        db = get_db()
        
        # Check if user already exists
        existing_user = db.execute(
            'SELECT id FROM users WHERE username = ? OR email = ?',
            (username, email)
        ).fetchone()
        
        if existing_user:
            flash('Username or email already exists', 'error')
            return render_template('login.html')
        
        # Create new user with 7-day free trial
        if not password:
            flash('Password is required', 'error')
            return render_template('login.html')
        password_hash = generate_password_hash(password)
        from datetime import datetime, timedelta
        trial_end_date = datetime.now() + timedelta(days=7)
        try:
            db.execute(
                'INSERT INTO users (username, email, password_hash, subscription_plan, trial_end_date, subscription_status) VALUES (?, ?, ?, ?, ?, ?)',
                (username, email, password_hash, 'free_trial', trial_end_date, 'trial')
            )
            db.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('auth.login'))
        except sqlite3.Error as e:
            flash('Registration failed. Please try again.', 'error')
    
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('auth.login'))
