#!/usr/bin/env python3
"""
Al Dashboard — Web GUI for Autonomous Labor Command Hub
"""

from flask import Flask, render_template, jsonify, request
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)

# Configuration
HERMES_HOME = os.environ.get('HERMES_HOME', os.path.expanduser('~/.hermes'))
AL_MANAGER_PROFILE = os.environ.get('AL_MANAGER_PROFILE', 'al-manager')
KANBAN_DB = os.path.join(HERMES_HOME, 'profiles', AL_MANAGER_PROFILE, 'kanban.db')

@app.route('/')
def dashboard():
    """Main dashboard view"""
    return render_template('dashboard.html')

@app.route('/health')
def health():
    """Health check endpoint for Docker"""
    return jsonify({'status': 'healthy', 'service': 'al-dashboard'}), 200

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    """Get all Kanban tasks"""
    try:
        conn = sqlite3.connect(KANBAN_DB)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, title, assignee, status, body, parents, created_at, updated_at
            FROM tasks
            ORDER BY created_at DESC
        """)
        tasks = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return jsonify({'success': True, 'tasks': tasks})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/tasks', methods=['POST'])
def create_task():
    """Create new task via Al Manager"""
    data = request.json
    # This would integrate with Hermes to create task via kanban_create
    # For now, return placeholder
    return jsonify({
        'success': True,
        'message': 'Task creation requires Hermes integration',
        'task': data
    })

@app.route('/api/workers', methods=['GET'])
def get_workers():
    """Get list of workers with real status from Hermes profiles"""
    import subprocess
    import os
    
    # Actual AL workforce profiles
    profiles = [
        {'name': 'Jed', 'profile': 'jed-hermes', 'role': 'Manager/Orchestrator'},
        {'name': 'Ruth', 'profile': 'ruth-hermes', 'role': 'Coder'},
        {'name': 'Ms. Anderson', 'profile': 'ms-anderson', 'role': 'Web Dev'},
        {'name': 'Octavia', 'profile': 'octavia-hermes', 'role': 'Admin/Writer'},
        {'name': 'Mitch', 'profile': 'mitch-hermes', 'role': 'Marketing/Sales'},
        {'name': 'Malcom', 'profile': 'malcom-hermes', 'role': 'Social Media'},
    ]
    
    # Check gateway status for each profile
    workers = []
    hermes_home = os.environ.get('HERMES_HOME', os.path.expanduser('~/.hermes'))
    
    for worker in profiles:
        # Check if profile exists
        profile_path = os.path.join(hermes_home, 'profiles', worker['profile'])
        exists = os.path.exists(profile_path)
        
        # Check if gateway is running (simplified - assumes running if profile exists)
        status = 'online' if exists else 'offline'
        
        workers.append({
            'name': worker['name'],
            'profile': worker['profile'],
            'role': worker['role'],
            'status': status
        })
    
    return jsonify({'success': True, 'workers': workers})

@app.route('/api/chat', methods=['POST'])
def chat_with_al():
    """Chat with Al Manager"""
    data = request.json
    message = data.get('message', '')
    # This would integrate with Hermes to send message to Al Manager
    # For now, return placeholder
    return jsonify({
        'success': True,
        'response': f'Al received: "{message}". Hermes integration pending.',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get dashboard statistics"""
    try:
        conn = sqlite3.connect(KANBAN_DB)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM tasks WHERE status = 'todo'")
        todo_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM tasks WHERE status = 'in_progress'")
        in_progress_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM tasks WHERE status = 'done'")
        done_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM tasks")
        total_count = cursor.fetchone()[0]
        
        conn.close()
        
        return jsonify({
            'success': True,
            'stats': {
                'total': total_count,
                'todo': todo_count,
                'in_progress': in_progress_count,
                'done': done_count
            }
        })
    except Exception as e:
        # Return zeros if DB doesn't exist yet
        return jsonify({
            'success': True,
            'stats': {
                'total': 0,
                'todo': 0,
                'in_progress': 0,
                'done': 0
            },
            'note': 'Kanban board not initialized yet - tasks will appear here once created'
        })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    debug = os.environ.get('FLASK_ENV', 'production') != 'production'
    app.run(host='0.0.0.0', port=port, debug=debug)
