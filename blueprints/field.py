from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from subscription_utils import require_pro

field_bp = Blueprint('field', __name__)

def get_db():
    """Get database connection"""
    from flask import current_app
    return current_app.get_db()

@field_bp.route('/')
@require_pro
def index():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    db = get_db()
    measurements = db.execute(
        'SELECT fm.*, p.name as project_name '
        'FROM field_measurements fm '
        'LEFT JOIN projects p ON fm.project_id = p.id '
        'ORDER BY fm.timestamp DESC LIMIT 100'
    ).fetchall()
    
    # Get measurement types for filtering
    measurement_types = db.execute(
        'SELECT DISTINCT measurement_type FROM field_measurements '
        'WHERE measurement_type IS NOT NULL ORDER BY measurement_type'
    ).fetchall()
    
    # Get recent statistics
    total_measurements = db.execute(
        'SELECT COUNT(*) as count FROM field_measurements'
    ).fetchone()['count']
    
    today_measurements = db.execute(
        'SELECT COUNT(*) as count FROM field_measurements '
        'WHERE date(timestamp) = date("now")'
    ).fetchone()['count']
    
    active_devices = db.execute(
        'SELECT COUNT(DISTINCT device_id) as count FROM field_measurements '
        'WHERE device_id IS NOT NULL'
    ).fetchone()['count']
    
    stats = {
        'total_measurements': total_measurements,
        'today_measurements': today_measurements,
        'active_devices': active_devices
    }
    
    return render_template('field/index.html', 
                         measurements=measurements,
                         measurement_types=measurement_types,
                         stats=stats)

@field_bp.route('/add', methods=['GET', 'POST'])
def add():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    db = get_db()
    projects = db.execute('SELECT id, name FROM projects ORDER BY name').fetchall()
    
    if request.method == 'POST':
        project_id = request.form.get('project_id')
        measurement_type = request.form.get('measurement_type')
        value = request.form.get('value')
        unit = request.form.get('unit')
        location = request.form.get('location')
        device_id = request.form.get('device_id')
        notes = request.form.get('notes')
        
        if not all([measurement_type, value]):
            flash('Measurement type and value are required', 'error')
            return render_template('field/form.html', projects=projects)
        
        try:
            value = float(value)
            
            db.execute(
                'INSERT INTO field_measurements (project_id, measurement_type, '
                'value, unit, location, device_id, notes) '
                'VALUES (?, ?, ?, ?, ?, ?, ?)',
                (project_id or None, measurement_type, value, unit,
                 location, device_id, notes)
            )
            db.commit()
            flash('Measurement recorded successfully', 'success')
            return redirect(url_for('field.index'))
        except ValueError:
            flash('Invalid measurement value', 'error')
        except Exception as e:
            flash('Error recording measurement', 'error')
    
    return render_template('field/form.html', projects=projects)

@field_bp.route('/api/record', methods=['POST'])
def api_record():
    """API endpoint for IoT devices and external systems to submit measurements"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        required_fields = ['measurement_type', 'value']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Validate value is numeric
        try:
            value = float(data['value'])
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid value - must be numeric'}), 400
        
        db = get_db()
        
        # Validate project_id if provided
        project_id = data.get('project_id')
        if project_id:
            project = db.execute('SELECT id FROM projects WHERE id = ?', (project_id,)).fetchone()
            if not project:
                return jsonify({'error': 'Invalid project_id'}), 400
        
        db.execute(
            'INSERT INTO field_measurements (project_id, measurement_type, '
            'value, unit, location, device_id, notes) '
            'VALUES (?, ?, ?, ?, ?, ?, ?)',
            (project_id, data['measurement_type'], value,
             data.get('unit'), data.get('location'),
             data.get('device_id'), data.get('notes'))
        )
        db.commit()
        
        return jsonify({'message': 'Measurement recorded successfully'}), 201
    
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@field_bp.route('/charts')
def charts():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    db = get_db()
    
    # Get measurement data for charts
    measurement_types = db.execute(
        'SELECT DISTINCT measurement_type FROM field_measurements '
        'WHERE measurement_type IS NOT NULL'
    ).fetchall()
    
    chart_data = {}
    for mt in measurement_types:
        measurements = db.execute(
            'SELECT value, timestamp FROM field_measurements '
            'WHERE measurement_type = ? '
            'ORDER BY timestamp DESC LIMIT 50',
            (mt['measurement_type'],)
        ).fetchall()
        
        chart_data[mt['measurement_type']] = [
            {'x': m['timestamp'], 'y': m['value']} for m in measurements
        ]
    
    return render_template('field/charts.html', chart_data=chart_data)

@field_bp.route('/api/data/<measurement_type>')
def api_data(measurement_type):
    """API endpoint to get measurement data for charts"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    db = get_db()
    
    # Get optional query parameters
    limit = request.args.get('limit', 100, type=int)
    project_id = request.args.get('project_id', type=int)
    
    # Build query
    query = '''
        SELECT value, timestamp, location, device_id 
        FROM field_measurements 
        WHERE measurement_type = ?
    '''
    params = [measurement_type]
    
    if project_id:
        query += ' AND project_id = ?'
        params.append(project_id)
    
    query += ' ORDER BY timestamp DESC LIMIT ?'
    params.append(limit)
    
    measurements = db.execute(query, params).fetchall()
    
    data = [
        {
            'value': m['value'],
            'timestamp': m['timestamp'],
            'location': m['location'],
            'device_id': m['device_id']
        }
        for m in measurements
    ]
    
    return jsonify(data)
