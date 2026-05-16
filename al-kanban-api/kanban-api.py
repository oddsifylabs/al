#!/usr/bin/env python3
"""
Hermes Kanban API Server
Exposes native Hermes Kanban database via REST API for Railway dashboard integration
"""

from flask import Flask, jsonify, request
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)

# Configuration - Use Hermes native Kanban DB
# On Railway: uses shared volume at /data/kanban.db
# Locally: uses ~/.hermes/kanban.db
RAILWAY_VOLUME = os.environ.get('RAILWAY_SHARED_VOLUME', '/data')
KANBAN_DB_PATH = os.environ.get('KANBAN_DB_PATH', os.path.join(RAILWAY_VOLUME, 'kanban.db'))

# Fallback to local Hermes home if Railway volume doesn't exist
if not os.path.exists(RAILWAY_VOLUME):
    HERMES_HOME = os.path.expanduser('~/.hermes')
    KANBAN_DB = os.path.join(HERMES_HOME, 'kanban.db')
else:
    KANBAN_DB = KANBAN_DB_PATH

def get_db_connection():
    """Get database connection"""
    if not os.path.exists(KANBAN_DB):
        return None
    conn = sqlite3.connect(KANBAN_DB)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/health')
def health():
    """Health check endpoint"""
    if os.path.exists(KANBAN_DB):
        return jsonify({'status': 'healthy', 'service': 'hermes-kanban-api', 'db': KANBAN_DB}), 200
    else:
        return jsonify({'status': 'unhealthy', 'service': 'hermes-kanban-api', 'error': 'Database not found'}), 503

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get Kanban task statistics from Hermes native DB"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({
                'success': False,
                'error': 'Kanban database not found',
                'stats': {'total': 0, 'todo': 0, 'in_progress': 0, 'done': 0}
            }), 404
        
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
            },
            'source': 'Hermes Native Kanban - Live Data',
            'database': KANBAN_DB
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'stats': {'total': 0, 'todo': 0, 'in_progress': 0, 'done': 0}
        }), 500

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    """Get all Kanban tasks from Hermes native DB"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({
                'success': False,
                'error': 'Kanban database not found',
                'tasks': []
            }), 404
        
        cursor = conn.cursor()
        # Use actual Hermes Kanban schema columns
        cursor.execute("""
            SELECT id, title, assignee, status, body, created_at, completed_at, priority, result
            FROM tasks
            ORDER BY created_at DESC
        """)
        tasks = []
        for row in cursor.fetchall():
            task = {
                'id': row[0],
                'title': row[1],
                'assignee': row[2],
                'status': row[3],
                'body': row[4],
                'created_at': row[5],
                'completed_at': row[6],
                'priority': row[7],
                'result': row[8]
            }
            tasks.append(task)
        conn.close()
        
        return jsonify({
            'success': True,
            'tasks': tasks,
            'source': 'Hermes Native Kanban - Live Data',
            'count': len(tasks)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'tasks': []
        }), 500

@app.route('/api/tasks', methods=['POST'])
def create_task():
    """Create a new Kanban task in Hermes native DB"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({
                'success': False,
                'error': 'Kanban database not found'
            }), 404
        
        data = request.json
        task_id = data.get('id', f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        title = data.get('title', 'Untitled Task')
        assignee = data.get('assignee', None)
        status = data.get('status', 'todo')
        body = data.get('body', '')
        parents = data.get('parents', '')
        
        cursor = conn.cursor()
        now = datetime.now().isoformat()
        
        cursor.execute('''
            INSERT INTO tasks (id, title, assignee, status, body, parents, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (task_id, title, assignee, status, body, parents, now, now))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Task created',
            'task': {
                'id': task_id,
                'title': title,
                'assignee': assignee,
                'status': status,
                'body': body,
                'created_at': now
            }
        }), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting Hermes Kanban API on port {port}")
    print(f"Database: {KANBAN_DB}")
    app.run(host='0.0.0.0', port=port, debug=False)
