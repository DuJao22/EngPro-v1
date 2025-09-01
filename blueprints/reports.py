from flask import Blueprint, render_template, request, redirect, url_for, flash, session, make_response
from datetime import datetime, timedelta
import json

reports_bp = Blueprint('reports', __name__)

def get_db():
    """Get database connection"""
    from flask import current_app
    return current_app.get_db()

@reports_bp.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    return render_template('reports/index.html')

@reports_bp.route('/projects')
def projects():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    db = get_db()
    
    # Get filter parameters
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    status = request.args.get('status')
    
    # Build query
    query = 'SELECT * FROM projects WHERE 1=1'
    params = []
    
    if start_date:
        query += ' AND start_date >= ?'
        params.append(start_date)
    
    if end_date:
        query += ' AND start_date <= ?'
        params.append(end_date)
    
    if status:
        query += ' AND status = ?'
        params.append(status)
    
    query += ' ORDER BY created_at DESC'
    
    projects_data = db.execute(query, params).fetchall()
    
    # Get project statistics and convert to list of dicts
    projects = []
    for project in projects_data:
        # Get task count
        task_count = db.execute(
            'SELECT COUNT(*) as count FROM tasks WHERE project_id = ?',
            (project['id'],)
        ).fetchone()['count']
        
        # Get budget total
        budget_total = db.execute(
            'SELECT SUM(total_cost) as total FROM budget_items WHERE project_id = ?',
            (project['id'],)
        ).fetchone()['total'] or 0
        
        # Get incident count
        incident_count = db.execute(
            'SELECT COUNT(*) as count FROM incidents WHERE project_id = ?',
            (project['id'],)
        ).fetchone()['count']
        
        project_dict = dict(project)
        project_dict['task_count'] = task_count
        project_dict['budget_total'] = budget_total
        project_dict['incident_count'] = incident_count
        projects.append(project_dict)
    
    return render_template('reports/projects.html', 
                         projects=projects,
                         filters={'start_date': start_date, 'end_date': end_date, 'status': status})

@reports_bp.route('/budget')
def budget():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    db = get_db()
    
    # Get filter parameters
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    category = request.args.get('category')
    project_id = request.args.get('project_id')
    
    # Build query
    query = '''
        SELECT b.*, p.name as project_name, s.name as supplier_name
        FROM budget_items b
        LEFT JOIN projects p ON b.project_id = p.id
        LEFT JOIN suppliers s ON b.supplier_id = s.id
        WHERE 1=1
    '''
    params = []
    
    if start_date:
        query += ' AND b.created_at >= ?'
        params.append(start_date)
    
    if end_date:
        query += ' AND b.created_at <= ?'
        params.append(end_date + ' 23:59:59')
    
    if category:
        query += ' AND b.category = ?'
        params.append(category)
    
    if project_id:
        query += ' AND b.project_id = ?'
        params.append(project_id)
    
    query += ' ORDER BY b.created_at DESC'
    
    budget_items = db.execute(query, params).fetchall()
    
    # Calculate totals by category
    category_totals = db.execute(
        'SELECT category, SUM(total_cost) as total, COUNT(*) as count '
        'FROM budget_items GROUP BY category ORDER BY total DESC'
    ).fetchall()
    
    # Get total budget
    total_budget = sum(item['total_cost'] for item in budget_items)
    
    # Get projects for filter
    projects = db.execute('SELECT id, name FROM projects ORDER BY name').fetchall()
    
    # Get categories for filter
    categories = db.execute(
        'SELECT DISTINCT category FROM budget_items WHERE category IS NOT NULL ORDER BY category'
    ).fetchall()
    
    return render_template('reports/budget.html',
                         budget_items=budget_items,
                         category_totals=category_totals,
                         total_budget=total_budget,
                         projects=projects,
                         categories=categories,
                         filters={
                             'start_date': start_date,
                             'end_date': end_date,
                             'category': category,
                             'project_id': project_id
                         })

@reports_bp.route('/safety')
def safety():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    db = get_db()
    
    # Get filter parameters
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    severity = request.args.get('severity')
    status = request.args.get('status')
    
    # Build query
    query = '''
        SELECT i.*, p.name as project_name
        FROM incidents i
        LEFT JOIN projects p ON i.project_id = p.id
        WHERE 1=1
    '''
    params = []
    
    if start_date:
        query += ' AND i.date_occurred >= ?'
        params.append(start_date)
    
    if end_date:
        query += ' AND i.date_occurred <= ?'
        params.append(end_date)
    
    if severity:
        query += ' AND i.severity = ?'
        params.append(severity)
    
    if status:
        query += ' AND i.status = ?'
        params.append(status)
    
    query += ' ORDER BY i.date_occurred DESC'
    
    incidents = db.execute(query, params).fetchall()
    
    # Get statistics
    severity_stats = db.execute(
        'SELECT severity, COUNT(*) as count FROM incidents GROUP BY severity'
    ).fetchall()
    
    status_stats = db.execute(
        'SELECT status, COUNT(*) as count FROM incidents GROUP BY status'
    ).fetchall()
    
    monthly_stats = db.execute(
        'SELECT strftime("%Y-%m", date_occurred) as month, COUNT(*) as count '
        'FROM incidents WHERE date_occurred IS NOT NULL '
        'GROUP BY month ORDER BY month DESC LIMIT 12'
    ).fetchall()
    
    return render_template('reports/safety.html',
                         incidents=incidents,
                         severity_stats=severity_stats,
                         status_stats=status_stats,
                         monthly_stats=monthly_stats,
                         filters={
                             'start_date': start_date,
                             'end_date': end_date,
                             'severity': severity,
                             'status': status
                         })

@reports_bp.route('/permits')
def permits():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    db = get_db()
    
    # Get filter parameters
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    status = request.args.get('status')
    permit_type = request.args.get('type')
    
    # Build query
    query = '''
        SELECT pr.*, p.name as project_name
        FROM permits pr
        LEFT JOIN projects p ON pr.project_id = p.id
        WHERE 1=1
    '''
    params = []
    
    if start_date:
        query += ' AND pr.issue_date >= ?'
        params.append(start_date)
    
    if end_date:
        query += ' AND pr.issue_date <= ?'
        params.append(end_date)
    
    if status:
        query += ' AND pr.status = ?'
        params.append(status)
    
    if permit_type:
        query += ' AND pr.type = ?'
        params.append(permit_type)
    
    query += ' ORDER BY pr.issue_date DESC'
    
    permits = db.execute(query, params).fetchall()
    
    # Get expiring permits
    expiring_permits = db.execute(
        'SELECT pr.*, p.name as project_name FROM permits pr '
        'LEFT JOIN projects p ON pr.project_id = p.id '
        'WHERE pr.expiry_date <= date("now", "+30 days") AND pr.expiry_date >= date("now") '
        'ORDER BY pr.expiry_date ASC'
    ).fetchall()
    
    # Get statistics
    status_stats = db.execute(
        'SELECT status, COUNT(*) as count FROM permits GROUP BY status'
    ).fetchall()
    
    type_stats = db.execute(
        'SELECT type, COUNT(*) as count FROM permits WHERE type IS NOT NULL GROUP BY type'
    ).fetchall()
    
    return render_template('reports/permits.html',
                         permits=permits,
                         expiring_permits=expiring_permits,
                         status_stats=status_stats,
                         type_stats=type_stats,
                         filters={
                             'start_date': start_date,
                             'end_date': end_date,
                             'status': status,
                             'type': permit_type
                         })

@reports_bp.route('/export/<report_type>')
def export(report_type):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    # This is a simplified export - in a real application you might use libraries like pandas or reportlab
    db = get_db()
    
    if report_type == 'projects':
        data = db.execute('SELECT * FROM projects ORDER BY created_at DESC').fetchall()
        headers = ['ID', 'Name', 'Description', 'Status', 'Start Date', 'End Date', 'Budget', 'Created At']
        
    elif report_type == 'budget':
        data = db.execute(
            'SELECT b.*, p.name as project_name FROM budget_items b '
            'LEFT JOIN projects p ON b.project_id = p.id '
            'ORDER BY b.created_at DESC'
        ).fetchall()
        headers = ['ID', 'Project', 'Category', 'Description', 'Quantity', 'Unit Cost', 'Total Cost', 'Created At']
        
    elif report_type == 'incidents':
        data = db.execute(
            'SELECT i.*, p.name as project_name FROM incidents i '
            'LEFT JOIN projects p ON i.project_id = p.id '
            'ORDER BY i.date_occurred DESC'
        ).fetchall()
        headers = ['ID', 'Project', 'Title', 'Severity', 'Date Occurred', 'Status', 'Reported By']
        
    else:
        flash('Invalid report type', 'error')
        return redirect(url_for('reports.index'))
    
    # Generate HTML for export (you could also generate CSV or PDF here)
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{report_type.title()} Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            table {{ border-collapse: collapse; width: 100%; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
            .header {{ margin-bottom: 20px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>CivilSaaS - {report_type.title()} Report</h1>
            <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>Todos os créditos do sistema a João Layon</p>
        </div>
        <table>
            <thead>
                <tr>
                    {"".join(f"<th>{header}</th>" for header in headers)}
                </tr>
            </thead>
            <tbody>
    """
    
    for row in data:
        html_content += "<tr>"
        for key in row.keys():
            html_content += f"<td>{row[key] or ''}</td>"
        html_content += "</tr>"
    
    html_content += """
            </tbody>
        </table>
    </body>
    </html>
    """
    
    response = make_response(html_content)
    response.headers['Content-Type'] = 'text/html'
    response.headers['Content-Disposition'] = f'attachment; filename={report_type}_report.html'
    
    return response
