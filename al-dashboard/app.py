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
    """Get all Kanban tasks from Jed (Manager)"""
    import requests
    
    try:
        # Fetch tasks from Jed via internal Railway network
        response = requests.get('http://jed---the-manager.railway.internal:8080/api/tasks', timeout=3)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                return jsonify(data)
    except Exception as e:
        pass
    
    # Fallback: return empty list if Jed is unavailable
    return jsonify({'success': True, 'tasks': [], 'source': 'Jed (Manager) - Unavailable'})

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
    """Get list of AL workforce members with real health status"""
    import requests
    
    # AL workforce with Railway internal URLs
    workers_config = [
        {'name': 'Jed', 'profile': 'jed-hermes', 'role': 'Manager/Orchestrator', 'internal_url': 'http://jed---the-manager.railway.internal:8080'},
        {'name': 'Ruth', 'profile': 'ruth-hermes', 'role': 'Coder', 'internal_url': 'http://hermes-agent-edcb.railway.internal:8080'},
        {'name': 'Ms. Anderson', 'profile': 'ms-anderson', 'role': 'Web Dev', 'internal_url': 'http://hermes-agent-14cf.railway.internal:8080'},
        {'name': 'Octavia', 'profile': 'octavia-hermes', 'role': 'Admin/Writer', 'internal_url': 'http://hermes-agent.railway.internal:8080'},
        {'name': 'Mitch', 'profile': 'mitch-hermes', 'role': 'Marketing/Sales', 'internal_url': 'http://hermes-agent-7a4a.railway.internal:8080'},
        {'name': 'Malcom', 'profile': 'malcom-hermes', 'role': 'Social Media', 'internal_url': 'http://hermes-agent-3940.railway.internal:8080'},
    ]
    
    workers = []
    for worker in workers_config:
        status = 'offline'
        try:
            # Health check with 2-second timeout
            response = requests.get(f"{worker['internal_url']}/health", timeout=2)
            if response.status_code == 200:
                status = 'online'
        except:
            status = 'offline'
        
        workers.append({
            'name': worker['name'],
            'profile': worker['profile'],
            'role': worker['role'],
            'status': status,
            'internal_url': worker['internal_url']
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
    """Get dashboard statistics from Jed's Kanban database"""
    import requests
    
    # Try to get stats from Jed (Manager) via internal Railway network
    try:
        response = requests.get('http://jed---the-manager.railway.internal:8080/api/stats', timeout=3)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                return jsonify({
                    'success': True,
                    'stats': data.get('stats', {'total': 0, 'todo': 0, 'in_progress': 0, 'done': 0}),
                    'source': 'Jed (Manager) - Live Data'
                })
    except Exception as e:
        pass
    
    # Fallback: return zeros if Jed is unavailable
    return jsonify({
        'success': True,
        'stats': {'total': 0, 'todo': 0, 'in_progress': 0, 'done': 0},
        'source': 'Jed (Manager) - Unavailable'
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    debug = os.environ.get('FLASK_ENV', 'production') != 'production'
    app.run(host='0.0.0.0', port=port, debug=debug)
