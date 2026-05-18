#!/usr/bin/env python3
"""
AL Dashboard — Central Worker Hub for Oddsify Labs
PostgreSQL-backed task router, Kanban API, and web UI
"""

import os
import json
import uuid
import requests
import psycopg2
import psycopg2.extras
from datetime import datetime, timezone, timedelta
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

# ── Config ──────────────────────────────────────────────────────────
DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL env var required")

RAILWAY_API_TOKEN = os.environ.get("RAILWAY_API_TOKEN")
RAILWAY_PROJECT_ID = os.environ.get("RAILWAY_PROJECT_ID")
RAILWAY_GQL_URL = "https://backboard.railway.com/graphql/v2"

# Railway internal URLs for workers
# Optional: add "railway_service_id" once you know it for tighter integration
WORKERS = {
    "jed": {"name": "Jed Hermes", "role": "Manager", "tg": "@jedhermesbot", "url": "http://jed---the-manager.railway.internal"},
    "ruth": {"name": "Ruth Hermes", "role": "Coder", "tg": "", "url": "http://hermes-agent-edcb.railway.internal"},
    "ms-anderson": {"name": "Ms. Anderson", "role": "Web Dev", "tg": "@MsAndersonBOT", "url": "http://hermes-agent-14cf.railway.internal"},
    "octavia": {"name": "Octavia Hermes", "role": "Writer/Admin/Research", "tg": "@OctaviaHermesBot", "url": "http://hermes-agent.railway.internal"},
    "mitch": {"name": "Mitch Hermes", "role": "Sales & Marketing", "tg": "@MitchHermes_Bot", "url": "http://hermes-agent-7a4a.railway.internal"},
    "malcom": {"name": "Malcom Hermes", "role": "Social Media", "tg": "@MalcomSMMBot", "url": "http://hermes-agent-3940.railway.internal"},
}


# ── Railway GraphQL Helper ──────────────────────────────────────────

def railway_gql(query: str, variables: dict = None):
    """Execute a Railway GraphQL query/mutation. Returns (data, error)."""
    if not RAILWAY_API_TOKEN:
        return None, "RAILWAY_API_TOKEN not configured"
    headers = {
        "Authorization": f"Bearer {RAILWAY_API_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {"query": query}
    if variables:
        payload["variables"] = variables
    try:
        r = requests.post(RAILWAY_GQL_URL, json=payload, headers=headers, timeout=15)
        r.raise_for_status()
        data = r.json()
        if "errors" in data:
            return None, data["errors"][0].get("message", str(data["errors"]))
        return data.get("data"), None
    except requests.exceptions.RequestException as e:
        return None, str(e)


def _service_id_from_name(name: str):
    """Look up a Railway service ID by its display name."""
    if not RAILWAY_PROJECT_ID:
        return None
    q = """
    query Project($id: String!) {
      project(id: $id) {
        services {
          edges {
            node {
              id
              name
            }
          }
        }
      }
    }
    """
    data, err = railway_gql(q, {"id": RAILWAY_PROJECT_ID})
    if err or not data:
        return None
    for edge in data.get("project", {}).get("services", {}).get("edges", []):
        node = edge.get("node", {})
        if node.get("name") == name:
            return node.get("id")
    return None

# ── DB Helpers ──────────────────────────────────────────────────────
def get_db():
    return psycopg2.connect(DATABASE_URL, cursor_factory=psycopg2.extras.RealDictCursor)


def init_db():
    """Create tables if they don't exist"""
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id              TEXT PRIMARY KEY,
            title           TEXT NOT NULL,
            body            TEXT,
            assignee        TEXT,
            status          TEXT NOT NULL DEFAULT 'pending_review',
            priority        INTEGER DEFAULT 0,
            created_by      TEXT DEFAULT 'dashboard',
            created_at      TIMESTAMP DEFAULT NOW(),
            started_at      TIMESTAMP,
            completed_at    TIMESTAMP,
            parent_id       TEXT,
            result          TEXT,
            progress_notes  TEXT,
            worker_url      TEXT,
            FOREIGN KEY (parent_id) REFERENCES tasks(id) ON DELETE CASCADE
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS task_events (
            id          SERIAL PRIMARY KEY,
            task_id     TEXT NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
            actor       TEXT NOT NULL,
            event       TEXT NOT NULL,
            note        TEXT,
            created_at  TIMESTAMP DEFAULT NOW()
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS worker_heartbeat (
            worker_id   TEXT PRIMARY KEY,
            status      TEXT DEFAULT 'unknown',
            last_seen   TIMESTAMP DEFAULT NOW(),
            task_count  INTEGER DEFAULT 0
        )
    """)

    conn.commit()
    cur.close()
    conn.close()
    print("[DB] Initialized")


# ── Routes ──────────────────────────────────────────────────────────

@app.route("/")
def dashboard():
    return render_template("dashboard.html")


@app.route("/health")
def health():
    try:
        conn = get_db()
        conn.close()
        return jsonify({"status": "healthy", "service": "al-dashboard"}), 200
    except Exception as e:
        return jsonify({"status": "unhealthy", "error": str(e)}), 503


# ── Tasks ───────────────────────────────────────────────────────────

@app.route("/api/tasks", methods=["GET"])
def list_tasks():
    """Get all tasks, optionally filtered by status or assignee"""
    status = request.args.get("status")
    assignee = request.args.get("assignee")
    parent_only = request.args.get("parent_only", "false").lower() == "true"

    conn = get_db()
    cur = conn.cursor()

    query = "SELECT * FROM tasks WHERE 1=1"
    params = []

    if status:
        query += " AND status = %s"
        params.append(status)
    if assignee:
        query += " AND assignee = %s"
        params.append(assignee)
    if parent_only:
        query += " AND parent_id IS NULL"

    query += " ORDER BY created_at DESC"

    cur.execute(query, params)
    tasks = cur.fetchall()

    # Convert to dict and fetch children for each
    result = []
    for t in tasks:
        task = dict(t)
        cur.execute("SELECT * FROM tasks WHERE parent_id = %s ORDER BY created_at", [task["id"]])
        task["subtasks"] = [dict(row) for row in cur.fetchall()]
        result.append(task)

    cur.close()
    conn.close()
    return jsonify({"success": True, "tasks": result})


@app.route("/api/tasks", methods=["POST"])
def create_task():
    """Create a new task (from chat or external)"""
    data = request.json or {}
    task_id = data.get("id") or f"task_{uuid.uuid4().hex[:8]}"

    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO tasks (id, title, body, assignee, status, priority, created_by, parent_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        task_id,
        data.get("title", "Untitled"),
        data.get("body", ""),
        data.get("assignee"),
        data.get("status", "pending_review"),
        data.get("priority", 0),
        data.get("created_by", "dashboard"),
        data.get("parent_id")
    ))

    cur.execute("""
        INSERT INTO task_events (task_id, actor, event, note)
        VALUES (%s, %s, %s, %s)
    """, (task_id, data.get("created_by", "dashboard"), "created", data.get("body", "")))

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"success": True, "task": {"id": task_id, "status": "pending_review"}}), 201


@app.route("/api/tasks/<task_id>", methods=["GET"])
def get_task(task_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM tasks WHERE id = %s", [task_id])
    task = cur.fetchone()
    if not task:
        return jsonify({"success": False, "error": "Not found"}), 404

    cur.execute("SELECT * FROM task_events WHERE task_id = %s ORDER BY created_at", [task_id])
    events = [dict(row) for row in cur.fetchall()]

    cur.execute("SELECT * FROM tasks WHERE parent_id = %s ORDER BY created_at", [task_id])
    subtasks = [dict(row) for row in cur.fetchall()]

    cur.close()
    conn.close()

    t = dict(task)
    t["events"] = events
    t["subtasks"] = subtasks
    return jsonify({"success": True, "task": t})


@app.route("/api/tasks/<task_id>/update", methods=["POST"])
def update_task(task_id):
    """Workers call this to report progress/status changes"""
    data = request.json or {}
    new_status = data.get("status")
    progress = data.get("progress_notes")
    result = data.get("result")
    actor = data.get("actor", "worker")

    conn = get_db()
    cur = conn.cursor()

    # Build dynamic update
    fields = []
    params = []
    if new_status:
        fields.append("status = %s")
        params.append(new_status)
        if new_status == "in_progress":
            fields.append("started_at = NOW()")
        if new_status in ("done", "review"):
            fields.append("completed_at = NOW()")
    if progress:
        fields.append("progress_notes = COALESCE(progress_notes, '') || %s")
        params.append(f"\n[{datetime.now().isoformat()}] {progress}")
    if result:
        fields.append("result = %s")
        params.append(result)

    if not fields:
        return jsonify({"success": False, "error": "No fields to update"}), 400

    params.append(task_id)
    cur.execute(f"UPDATE tasks SET {', '.join(fields)} WHERE id = %s", params)

    if cur.rowcount == 0:
        return jsonify({"success": False, "error": "Task not found"}), 404

    # Log event
    event_note = progress or result or f"Status changed to {new_status}"
    cur.execute("""
        INSERT INTO task_events (task_id, actor, event, note)
        VALUES (%s, %s, %s, %s)
    """, (task_id, actor, new_status or "update", event_note))

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"success": True, "task_id": task_id})


@app.route("/api/tasks/assigned/<worker_id>", methods=["GET"])
def get_assigned_tasks(worker_id):
    """Worker pollers call this to get their queue"""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM tasks
        WHERE assignee = %s AND status IN ('todo', 'in_progress', 'blocked')
        ORDER BY priority DESC, created_at ASC
    """, [worker_id])
    tasks = [dict(row) for row in cur.fetchall()]
    cur.close()
    conn.close()
    return jsonify({"success": True, "worker": worker_id, "tasks": tasks})


@app.route("/api/tasks/pending-review", methods=["GET"])
def get_pending_review():
    """Jed calls this to see new tasks from you"""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM tasks
        WHERE status = 'pending_review' AND parent_id IS NULL
        ORDER BY created_at ASC
    """)
    tasks = [dict(row) for row in cur.fetchall()]
    cur.close()
    conn.close()
    return jsonify({"success": True, "tasks": tasks})


# ── Chat / Inbox ────────────────────────────────────────────────────

@app.route("/api/chat", methods=["POST"])
def chat():
    """Your messages from the dashboard create pending_review tasks"""
    data = request.json or {}
    message = data.get("message", "").strip()
    if not message:
        return jsonify({"success": False, "error": "No message"}), 400

    task_id = f"task_{uuid.uuid4().hex[:8]}"

    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO tasks (id, title, body, status, created_by)
        VALUES (%s, %s, %s, %s, %s)
    """, (task_id, message[:120], message, "pending_review", "director"))

    cur.execute("""
        INSERT INTO task_events (task_id, actor, event, note)
        VALUES (%s, %s, %s, %s)
    """, (task_id, "director", "chat_created", message))

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({
        "success": True,
        "task_id": task_id,
        "message": "Task created and sent to Jed for review",
        "response": "📋 Task logged. Jed will decompose and assign shortly."
    })


# ── Stats ───────────────────────────────────────────────────────────

@app.route("/api/stats", methods=["GET"])
def get_stats():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM tasks WHERE status = 'pending_review'")
    pending = cur.fetchone()["count"]

    cur.execute("SELECT COUNT(*) FROM tasks WHERE status = 'todo'")
    todo = cur.fetchone()["count"]

    cur.execute("SELECT COUNT(*) FROM tasks WHERE status = 'in_progress'")
    in_progress = cur.fetchone()["count"]

    cur.execute("SELECT COUNT(*) FROM tasks WHERE status = 'blocked'")
    blocked = cur.fetchone()["count"]

    cur.execute("SELECT COUNT(*) FROM tasks WHERE status = 'review'")
    review = cur.fetchone()["count"]

    cur.execute("SELECT COUNT(*) FROM tasks WHERE status = 'done'")
    done = cur.fetchone()["count"]

    cur.execute("SELECT COUNT(*) FROM tasks")
    total = cur.fetchone()["count"]

    cur.close()
    conn.close()

    return jsonify({
        "success": True,
        "stats": {
            "total": total,
            "pending_review": pending,
            "todo": todo,
            "in_progress": in_progress,
            "blocked": blocked,
            "review": review,
            "done": done
        }
    })


# ── Workers ─────────────────────────────────────────────────────────

@app.route("/api/workers", methods=["GET"])
def list_workers():
    """Return worker roster with status from heartbeat table"""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT worker_id, status, last_seen, task_count FROM worker_heartbeat")
    rows = {row["worker_id"]: dict(row) for row in cur.fetchall()}
    cur.close()
    conn.close()

    workers = []
    for wid, info in WORKERS.items():
        hb = rows.get(wid, {})
        # If heartbeat is older than 2 minutes, mark offline
        status = hb.get("status", "unknown")
        last_seen = hb.get("last_seen")
        if last_seen:
            from datetime import datetime, timezone, timedelta
            # last_seen may be naive or aware
            if last_seen.tzinfo is None:
                last_seen = last_seen.replace(tzinfo=timezone.utc)
            if datetime.now(timezone.utc) - last_seen > timedelta(minutes=2):
                status = "offline"

        workers.append({
            "id": wid,
            "name": info["name"],
            "role": info["role"],
            "telegram": info["tg"],
            "status": status,
            "url": info["url"],
            "last_seen": last_seen.isoformat() if last_seen else None,
            "task_count": hb.get("task_count", 0)
        })

    return jsonify({"success": True, "workers": workers })


@app.route("/api/workers/<worker_id>/heartbeat", methods=["POST"])
def worker_heartbeat(worker_id):
    """Workers call this to register they're alive"""
    data = request.json or {}
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO worker_heartbeat (worker_id, status, last_seen, task_count)
        VALUES (%s, %s, NOW(), %s)
        ON CONFLICT (worker_id) DO UPDATE SET
            status = EXCLUDED.status,
            last_seen = EXCLUDED.last_seen,
            task_count = EXCLUDED.task_count
    """, (worker_id, data.get("status", "online"), data.get("task_count", 0)))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"success": True})


# ── Railway Ops ──────────────────────────────────────────────────────────

def _service_instance_id(service_name: str):
    """Get the first service instance ID for a given service name."""
    if not RAILWAY_PROJECT_ID:
        return None, "RAILWAY_PROJECT_ID not configured"
    q = """
    query Project($id: String!) {
      project(id: $id) {
        services {
          edges {
            node {
              id
              name
              serviceInstances {
                edges {
                  node {
                    id
                    environmentId
                  }
                }
              }
            }
          }
        }
      }
    }
    """
    data, err = railway_gql(q, {"id": RAILWAY_PROJECT_ID})
    if err:
        return None, err
    for edge in data.get("project", {}).get("services", {}).get("edges", []):
        node = edge.get("node", {})
        if node.get("name") == service_name:
            instances = node.get("serviceInstances", {}).get("edges", [])
            if instances:
                return instances[0]["node"]["id"], None
            return None, f"No instances found for service {service_name}"
    return None, f"Service {service_name} not found"


@app.route("/api/railway/services", methods=["GET"])
def railway_services():
    """List all services in the Railway project with status"""
    if not RAILWAY_PROJECT_ID:
        return jsonify({"success": False, "error": "RAILWAY_PROJECT_ID not configured"}), 400
    q = """
    query Project($id: String!) {
      project(id: $id) {
        id
        name
        services {
          edges {
            node {
              id
              name
              serviceInstances {
                edges {
                  node {
                    id
                    state
                    healthcheckStatus
                    latestDeployment {
                      id
                      status
                      createdAt
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
    """
    data, err = railway_gql(q, {"id": RAILWAY_PROJECT_ID})
    if err:
        return jsonify({"success": False, "error": err}), 502
    services = []
    for edge in data.get("project", {}).get("services", {}).get("edges", []):
        node = edge.get("node", {})
        inst = node.get("serviceInstances", {}).get("edges", [{}])[0].get("node", {})
        services.append({
            "id": node.get("id"),
            "name": node.get("name"),
            "state": inst.get("state"),
            "health": inst.get("healthcheckStatus"),
            "latest_deployment": inst.get("latestDeployment")
        })
    return jsonify({"success": True, "services": services})


@app.route("/api/railway/logs/<service_name>", methods=["GET"])
def railway_logs(service_name):
    """Fetch recent logs for a service by name"""
    lines = min(int(request.args.get("lines", 100)), 500)
    service_id, err = _service_id_from_name(service_name)
    if err:
        return jsonify({"success": False, "error": err}), 400
    q = """
    query ServiceLogs($serviceId: String!, $limit: Int!) {
      serviceLogs(serviceId: $serviceId, limit: $limit) {
        messages {
          message
          timestamp
          severity
        }
      }
    }
    """
    data, err = railway_gql(q, {"serviceId": service_id, "limit": lines})
    if err:
        return jsonify({"success": False, "error": err}), 502
    messages = data.get("serviceLogs", {}).get("messages", []) if data else []
    return jsonify({"success": True, "service": service_name, "logs": messages})


@app.route("/api/railway/restart/<service_name>", methods=["POST"])
def railway_restart(service_name):
    """Restart a service without rebuilding"""
    instance_id, err = _service_instance_id(service_name)
    if err:
        return jsonify({"success": False, "error": err}), 400
    q = """
    mutation ServiceInstanceRestart($id: String!) {
      serviceInstanceRestart(id: $id)
    }
    """
    data, err = railway_gql(q, {"id": instance_id})
    if err:
        return jsonify({"success": False, "error": err}), 502
    return jsonify({"success": True, "service": service_name, "action": "restart"})


@app.route("/api/railway/redeploy/<service_name>", methods=["POST"])
def railway_redeploy(service_name):
    """Redeploy a service (triggers a new build)"""
    instance_id, err = _service_instance_id(service_name)
    if err:
        return jsonify({"success": False, "error": err}), 400
    q = """
    mutation ServiceInstanceDeploy($id: String!) {
      serviceInstanceDeploy(id: $id)
    }
    """
    data, err = railway_gql(q, {"id": instance_id})
    if err:
        return jsonify({"success": False, "error": err}), 502
    return jsonify({"success": True, "service": service_name, "action": "redeploy"})


@app.route("/api/railway/status", methods=["GET"])
def railway_status():
    """Project-level health summary"""
    if not RAILWAY_PROJECT_ID:
        return jsonify({"success": False, "error": "RAILWAY_PROJECT_ID not configured"}), 400
    q = """
    query Project($id: String!) {
      project(id: $id) {
        id
        name
        services {
          edges {
            node {
              id
              name
              serviceInstances {
                edges {
                  node {
                    id
                    state
                    healthcheckStatus
                  }
                }
              }
            }
          }
        }
      }
    }
    """
    data, err = railway_gql(q, {"id": RAILWAY_PROJECT_ID})
    if err:
        return jsonify({"success": False, "error": err}), 502
    services = []
    for edge in data.get("project", {}).get("services", {}).get("edges", []):
        node = edge.get("node", {})
        inst = node.get("serviceInstances", {}).get("edges", [{}])[0].get("node", {})
        services.append({
            "name": node.get("name"),
            "state": inst.get("state"),
            "health": inst.get("healthcheckStatus")
        })
    total = len(services)
    healthy = sum(1 for s in services if s.get("health") == "HEALTHY")
    return jsonify({"success": True, "total": total, "healthy": healthy, "services": services})


# ── Init ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 8080))
    debug = os.environ.get("FLASK_ENV", "production") != "production"
    app.run(host="0.0.0.0", port=port, debug=debug)
