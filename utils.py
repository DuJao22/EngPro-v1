import json
from datetime import datetime

def get_db():
    """Get database connection"""
    from flask import current_app
    return current_app.get_db()

def log_audit(table_name, record_id, action, old_values, new_values, user_id):
    """Log audit trail for database changes"""
    try:
        db = get_db()
        db.execute(
            'INSERT INTO audit_log (table_name, record_id, action, old_values, new_values, user_id) '
            'VALUES (?, ?, ?, ?, ?, ?)',
            (table_name, record_id, action, 
             json.dumps(old_values, default=str) if old_values else None,
             json.dumps(new_values, default=str) if new_values else None,
             user_id)
        )
        db.commit()
    except Exception as e:
        # Log audit failures should not break the main operation
        print(f"Audit log failed: {e}")

def format_currency(amount):
    """Format currency for Brazilian Real"""
    if amount is None:
        return "R$ 0,00"
    return f"R$ {amount:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

def format_date(date_str):
    """Format date for Brazilian format"""
    if not date_str:
        return ""
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        return date_obj.strftime('%d/%m/%Y')
    except:
        return date_str

def calculate_risk_level(probability, impact):
    """Calculate risk level based on probability and impact"""
    score = probability * impact
    if score >= 15:
        return 'high'
    elif score >= 6:
        return 'medium'
    else:
        return 'low'

def get_risk_color(risk_level):
    """Get color class for risk level"""
    colors = {
        'high': 'danger',
        'medium': 'warning', 
        'low': 'success'
    }
    return colors.get(risk_level, 'secondary')

def validate_file_extension(filename, allowed_extensions):
    """Validate file extension"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def get_file_size_mb(file_path):
    """Get file size in MB"""
    try:
        import os
        size_bytes = os.path.getsize(file_path)
        return size_bytes / (1024 * 1024)
    except:
        return 0
