#!/usr/bin/env python3
"""
AL Worker Poller Template
Each worker deploys this script. It polls the AL Dashboard for assigned tasks,
reports progress, and marks completion.

Set WORKER_ID env var to one of: ruth, ms-anderson, octavia, mitch, malcom
"""

import os
import time
import json
import requests
import subprocess

# ── Config ──────────────────────────────────────────────────────────
DASHBOARD_URL = os.environ.get("DASHBOARD_URL", "http://al-dashboard:8080")
WORKER_ID = os.environ.get("WORKER_ID")
POLL_INTERVAL = int(os.environ.get("POLL_INTERVAL", "30"))

if not WORKER_ID:
    raise RuntimeError("WORKER_ID env var required (e.g. ruth, ms-anderson, octavia, mitch, malcom)")


def now():
    from datetime import datetime
    return datetime.now().strftime("%H:%M:%S")


def report_progress(task_id: str, status: str, note: str = "", result: str = ""):
    """Send status update back to dashboard"""
    try:
        r = requests.post(
            f"{DASHBOARD_URL}/api/tasks/{task_id}/update",
            json={
                "status": status,
                "actor": WORKER_ID,
                "progress_notes": note,
                "result": result
            },
            timeout=10
        )
        r.raise_for_status()
        print(f"[{now()}] 📤 Reported {status} for {task_id}")
    except Exception as e:
        print(f"[{now()}] ❌ Failed to report progress: {e}")


def execute_task(task: dict) -> dict:
    """
    Execute the task. This is where worker-specific logic goes.
    For the MVP, we simulate execution. In production:
    - Spawn Hermes CLI with task context
    - Or call worker's internal API
    - Or run a Python script from the task body
    """
    task_id = task["id"]
    title = task.get("title", "")
    body = task.get("body", "")

    print(f"[{now()}] 🚀 Executing task {task_id}: {title[:60]}")

    # ── Simulated execution (replace with real work) ──
    # Example: you could call Hermes here:
    # subprocess.run(["hermes", "--profile", f"{WORKER_ID}-hermes", "task", body])
    # Or invoke a local script, API, etc.

    # For now, mark as in_progress, "work" for a moment, then done
    report_progress(task_id, "in_progress", f"{WORKER_ID} started work")

    # Simulate work duration (replace with actual execution)
    time.sleep(2)

    # Construct a result
    result_text = f"Task completed by {WORKER_ID}.\n\nOriginal request:\n{body}"

    report_progress(task_id, "done", f"{WORKER_ID} finished work", result=result_text)

    return {"success": True, "task_id": task_id}


def send_heartbeat():
    """Let dashboard know we're alive"""
    try:
        requests.post(
            f"{DASHBOARD_URL}/api/workers/{WORKER_ID}/heartbeat",
            json={"status": "online", "task_count": 0},
            timeout=5
        )
    except Exception:
        pass


def poll():
    try:
        r = requests.get(
            f"{DASHBOARD_URL}/api/tasks/assigned/{WORKER_ID}",
            timeout=10
        )
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        print(f"[{now()}] ❌ Dashboard unreachable: {e}")
        return

    if not data.get("success"):
        return

    tasks = data.get("tasks", [])
    if not tasks:
        return

    print(f"[{now()}] 📥 {len(tasks)} task(s) assigned to {WORKER_ID}")

    for task in tasks:
        # Skip if already in_progress (another instance picked it up)
        if task.get("status") == "in_progress":
            continue
        execute_task(task)


def main():
    print(f"[{now()}] 🤖 Worker Poller started: {WORKER_ID}")
    print(f"[{now()}] 🔗 Dashboard: {DASHBOARD_URL}")
    print(f"[{now()}] ⏰ Poll interval: {POLL_INTERVAL}s")

    while True:
        send_heartbeat()
        poll()
        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()
