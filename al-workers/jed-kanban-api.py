#!/usr/bin/env python3
"""
Jed Hermes - Kanban API Server
Exposes REST API endpoints for dashboard integration
"""

from flask import Flask, jsonify, request
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)

# Configuration
HERMES_HOME = os.environ.get('HERMES_HOME', '/tmp')
KANBAN_DB = os.path.join(HERMES_HOME, 'kanban.db')

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(KANBAN_DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize Kanban database if it doesn't exist"""
    if not os.path.exists(KANBAN_DB):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                assignee TEXT,
                status TEXT DEFAULT 'todo',
                body TEXT,
                parents TEXT,
                created_at TEXT,
                updated_at TEXT
            )
        ''')
        conn.commit()
        conn.close()

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'jed-hermes'}), 200

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get Kanban task statistics"""
    try:
        init_db()
        conn = get_db_connection()
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
            'source': 'Jed (Manager) - Live Kanban DB'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'stats': {'total': 0, 'todo': 0, 'in_progress': 0, 'done': 0}
        }), 500

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    """Get all Kanban tasks"""
    try:
        init_db()
        conn = get_db_connection()
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
        return jsonify({'success': False, 'error': str(e), 'tasks': []}), 500

@app.route('/api/tasks', methods=['POST'])
def create_task():
    """Create a new Kanban task"""
    try:
        init_db()
        data = request.json
        task_id = data.get('id', f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        title = data.get('title', 'Untitled Task')
        assignee = data.get('assignee', None)
        status = data.get('status', 'todo')
        body = data.get('body', '')
        parents = data.get('parents', '')
        
        conn = get_db_connection()
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
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
