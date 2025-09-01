from flask import Blueprint, render_template, session, redirect, url_for
from datetime import datetime, timedelta

dashboard_bp = Blueprint('dashboard', __name__)

def get_db():
    """Get database connection"""
    from flask import current_app
    return current_app.get_db()

@dashboard_bp.route('/dashboard')
def index():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    db = get_db()
    
    # Get KPIs
    total_projects = db.execute('SELECT COUNT(*) as count FROM projects').fetchone()['count']
    active_projects = db.execute(
        'SELECT COUNT(*) as count FROM projects WHERE status = ?', ('active',)
    ).fetchone()['count']
    
    total_budget = db.execute(
        'SELECT SUM(total_cost) as total FROM budget_items'
    ).fetchone()['total'] or 0
    
    pending_tasks = db.execute(
        'SELECT COUNT(*) as count FROM tasks WHERE status = ?', ('pending',)
    ).fetchone()['count']
    
    overdue_tasks = db.execute(
        'SELECT COUNT(*) as count FROM tasks WHERE due_date < ? AND status = ?',
        (datetime.now().date(), 'pending')
    ).fetchone()['count']
    
    open_incidents = db.execute(
        'SELECT COUNT(*) as count FROM incidents WHERE status = ?', ('open',)
    ).fetchone()['count']
    
    # Get recent activities
    recent_projects = db.execute(
        'SELECT * FROM projects ORDER BY created_at DESC LIMIT 5'
    ).fetchall()
    
    recent_tasks = db.execute(
        'SELECT t.*, p.name as project_name FROM tasks t '
        'LEFT JOIN projects p ON t.project_id = p.id '
        'ORDER BY t.created_at DESC LIMIT 5'
    ).fetchall()
    
    # Upcoming deadlines
    upcoming_deadlines = db.execute(
        'SELECT t.title, t.due_date, p.name as project_name '
        'FROM tasks t '
        'LEFT JOIN projects p ON t.project_id = p.id '
        'WHERE t.due_date >= ? AND t.due_date <= ? AND t.status = ? '
        'ORDER BY t.due_date ASC LIMIT 10',
        (datetime.now().date(), (datetime.now() + timedelta(days=30)).date(), 'pending')
    ).fetchall()
    
    # Expiring permits
    expiring_permits = db.execute(
        'SELECT pr.name as permit_name, pr.expiry_date, p.name as project_name '
        'FROM permits pr '
        'LEFT JOIN projects p ON pr.project_id = p.id '
        'WHERE pr.expiry_date >= ? AND pr.expiry_date <= ? '
        'ORDER BY pr.expiry_date ASC LIMIT 5',
        (datetime.now().date(), (datetime.now() + timedelta(days=30)).date())
    ).fetchall()
    
    kpis = {
        'total_projects': total_projects,
        'active_projects': active_projects,
        'total_budget': total_budget,
        'pending_tasks': pending_tasks,
        'overdue_tasks': overdue_tasks,
        'open_incidents': open_incidents
    }
    
    return render_template('dashboard.html', 
                         kpis=kpis,
                         recent_projects=recent_projects,
                         recent_tasks=recent_tasks,
                         upcoming_deadlines=upcoming_deadlines,
                         expiring_permits=expiring_permits)
