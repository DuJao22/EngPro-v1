import os
import sqlite3
import logging
from flask import Flask, g, session, redirect, url_for, request
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.DEBUG)

def create_app():
    app = Flask(__name__)
    app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    
    # Database configuration
    DATABASE = 'civilsaas.db'
    
    def get_db():
        """Get database connection with row factory for dict-like access"""
        if 'db' not in g:
            g.db = sqlite3.connect(DATABASE)
            g.db.row_factory = sqlite3.Row
        return g.db
    
    def close_db(error):
        """Close database connection"""
        db = g.pop('db', None)
        if db is not None:
            db.close()
    
    def init_db():
        """Initialize database with schema"""
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.executescript(f.read())
        db.commit()
    
    # Register database functions
    app.teardown_appcontext(close_db)
    
    # Make get_db available to all modules
    app.get_db = get_db
    
    # Create uploads directory
    os.makedirs('uploads', exist_ok=True)
    
    # Initialize database on first run
    with app.app_context():
        init_db()
    
    # Import and register blueprints
    from blueprints.dashboard import dashboard_bp
    from blueprints.projects import projects_bp
    from blueprints.budget import budget_bp
    from blueprints.permits import permits_bp
    from blueprints.safety import safety_bp
    from blueprints.suppliers import suppliers_bp
    from blueprints.training import training_bp
    from blueprints.sustainability import sustainability_bp
    from blueprints.risks import risks_bp
    from blueprints.compliance import compliance_bp
    from blueprints.field import field_bp
    from blueprints.reports import reports_bp
    from blueprints.calculators import calculators_bp
    from auth import auth_bp
    from subscription import subscription_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(subscription_bp, url_prefix='/subscription')
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(projects_bp, url_prefix='/projects')
    app.register_blueprint(budget_bp, url_prefix='/budget')
    app.register_blueprint(permits_bp, url_prefix='/permits')
    app.register_blueprint(safety_bp, url_prefix='/safety')
    app.register_blueprint(suppliers_bp, url_prefix='/suppliers')
    app.register_blueprint(training_bp, url_prefix='/training')
    app.register_blueprint(sustainability_bp, url_prefix='/sustainability')
    app.register_blueprint(risks_bp, url_prefix='/risks')
    app.register_blueprint(compliance_bp, url_prefix='/compliance')
    app.register_blueprint(field_bp, url_prefix='/field')
    app.register_blueprint(reports_bp, url_prefix='/reports')
    app.register_blueprint(calculators_bp, url_prefix='/calculators')
    
    # Notes and credits routes
    from flask import render_template
    
    @app.route('/notes')
    def notes():
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        
        db = get_db()
        notes = db.execute(
            'SELECT * FROM notes ORDER BY created_at DESC'
        ).fetchall()
        
        return render_template('notes.html', notes=notes)
    
    @app.route('/notes', methods=['POST'])
    def add_note():
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        
        content = request.form.get('content')
        if content:
            db = get_db()
            db.execute(
                'INSERT INTO notes (content, user_id) VALUES (?, ?)',
                (content, session['user_id'])
            )
            db.commit()
        
        return redirect(url_for('notes'))
    
    @app.route('/credits')
    def credits():
        return render_template('credits.html')
    
    @app.route('/uploads/<filename>')
    def uploaded_file(filename):
        """Serve uploaded files"""
        from flask import send_from_directory
        return send_from_directory('uploads', filename)
    
    return app
