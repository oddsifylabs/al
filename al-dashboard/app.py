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
    """Get all Kanban tasks from Jed Kanban API"""
    import requests
    
    try:
        # Fetch tasks from Jed Kanban API via internal Railway network
        response = requests.get('http://jed-kanban-api.railway.internal:8080/api/tasks', timeout=3)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                return jsonify(data)
    except Exception as e:
        pass
    
    # Fallback: return empty list if API is unavailable
    return jsonify({'success': True, 'tasks': [], 'source': 'Jed Kanban API - Unavailable'})

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
    """Get list of AL workforce members"""
    # AL workforce deployed on Railway
    # All workers are assumed online since they're deployed as Railway services
    workers = [
        {'name': 'Jed', 'profile': 'jed-hermes', 'role': 'Manager/Orchestrator', 'status': 'online', 'service': 'jed---the-manager'},
        {'name': 'Ruth', 'profile': 'ruth-hermes', 'role': 'Coder', 'status': 'online', 'service': 'hermes-agent-edcb'},
        {'name': 'Ms. Anderson', 'profile': 'ms-anderson', 'role': 'Web Dev', 'status': 'online', 'service': 'hermes-agent-14cf'},
        {'name': 'Octavia', 'profile': 'octavia-hermes', 'role': 'Admin/Writer', 'status': 'online', 'service': 'hermes-agent'},
        {'name': 'Mitch', 'profile': 'mitch-hermes', 'role': 'Marketing/Sales', 'status': 'online', 'service': 'hermes-agent-7a4a'},
        {'name': 'Malcom', 'profile': 'malcom-hermes', 'role': 'Social Media', 'status': 'online', 'service': 'hermes-agent-3940'},
    ]
    return jsonify({'success': True, 'workers': workers})

@app.route('/api/chat', methods=['POST'])
def chat():
    """Chat with Al - creates tasks from user messages"""
    import requests
    
    data = request.json
    message = data.get('message', '')
    
    if not message:
        return jsonify({'success': False, 'error': 'No message provided'}), 400
    
    # Simple task creation from chat message
    # Create a task with the message as the title
    try:
        task_data = {
            'title': message[:100],  # Truncate long messages
            'assignee': None,  # Unassigned initially
            'status': 'todo',
            'body': f'Task created via dashboard chat',
        }
        
        # Send to Jed Kanban API
        response = requests.post(
            'http://jed-kanban-api.railway.internal:8080/api/tasks',
            json=task_data,
            timeout=5
        )
        
        if response.status_code == 201:
            result = response.json()
            return jsonify({
                'success': True,
                'message': f"Task created: {message[:50]}...",
                'task': result.get('task'),
                'response': '✅ Task created and added to Kanban board!'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to create task',
                'response': '❌ Failed to create task. Please try again.'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'response': '❌ Error connecting to Kanban API. Please try again.'
        })
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
    """Get dashboard statistics from Jed's Kanban API"""
    import requests
    
    # Try to get stats from Jed Kanban API via internal Railway network
    try:
        response = requests.get('http://jed-kanban-api.railway.internal:8080/api/stats', timeout=3)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                return jsonify({
                    'success': True,
                    'stats': data.get('stats', {'total': 0, 'todo': 0, 'in_progress': 0, 'done': 0}),
                    'source': 'Jed Kanban API - Live Data'
                })
    except Exception as e:
        pass
    
    # Fallback: return zeros if API is unavailable
    return jsonify({
        'success': True,
        'stats': {'total': 0, 'todo': 0, 'in_progress': 0, 'done': 0},
        'source': 'Jed Kanban API - Unavailable'
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    debug = os.environ.get('FLASK_ENV', 'production') != 'production'
    app.run(host='0.0.0.0', port=port, debug=debug)
