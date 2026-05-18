#!/usr/bin/env python3
"""
Jed Hermes — Manager Poller
Polls AL Dashboard for pending_review tasks, decomposes, assigns to workers.
Runs as a sidecar inside the Jed Hermes Railway service.
"""

import os
import re
import time
import json
import requests

# ── Config ──────────────────────────────────────────────────────────
DASHBOARD_URL = os.environ.get("DASHBOARD_URL", "http://al-dashboard:8080")
POLL_INTERVAL = int(os.environ.get("POLL_INTERVAL", "30"))

WORKER_KEYWORDS = {
    "ruth": ["code", "bug", "fix", "python", "javascript", "js", "node", "api", "backend", "script", "function", "deploy", "docker", "git", "test", "debug", "refactor", "database", "sql"],
    "ms-anderson": ["website", "web", "html", "css", "ui", "design", "frontend", "page", "layout", "responsive", "figma", "component", "react", "vue", "angular"],
    "octavia": ["write", "blog", "article", "content", "copy", "admin", "research", "doc", "documentation", "email", "report", "summary", "note", "edit"],
    "mitch": ["sales", "marketing", "lead", "campaign", "outreach", "seo", "ads", "funnel", "conversion", "promotion", "brand", "newsletter", "prospect"],
    "malcom": ["social", "twitter", "x.com", "post", "instagram", "linkedin", "tiktok", "facebook", "thread", "engagement", "follower", "content calendar", "schedule"],
}

WORKER_NAMES = {
    "ruth": "Ruth Hermes",
    "ms-anderson": "Ms. Anderson",
    "octavia": "Octavia Hermes",
    "mitch": "Mitch Hermes",
    "malcom": "Malcom Hermes",
}


def classify_task(title: str, body: str) -> str:
    """Simple keyword-based worker assignment"""
    text = f"{title} {body}".lower()
    scores = {}
    for worker, keywords in WORKER_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in text)
        if score:
            scores[worker] = score
    if scores:
        return max(scores, key=scores.get)
    return "ruth"  # Default fallback


def decompose_task(task: dict) -> list:
    """
    Break a task into subtasks. For MVP: single subtask per worker.
    In future: call LLM to decompose into multiple steps.
    """
    assignee = classify_task(task["title"], task.get("body", ""))
    subtasks = [{
        "title": task["title"],
        "body": task.get("body", ""),
        "assignee": assignee,
        "status": "todo",
        "priority": task.get("priority", 0),
        "parent_id": task["id"],
        "created_by": "jed"
    }]
    return subtasks


def poll():
    try:
        r = requests.get(f"{DASHBOARD_URL}/api/tasks/pending-review", timeout=10)
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        print(f"[{now()}] ❌ Dashboard unreachable: {e}")
        return

    if not data.get("success"):
        print(f"[{now()}] ⚠️ API error: {data}")
        return

    tasks = data.get("tasks", [])
    if not tasks:
        return

    print(f"[{now()}] 📋 Found {len(tasks)} pending task(s)")

    for task in tasks:
        task_id = task["id"]
        print(f"[{now()}] 🧠 Decomposing: {task['title'][:60]}")

        subtasks = decompose_task(task)

        for st in subtasks:
            try:
                r = requests.post(
                    f"{DASHBOARD_URL}/api/tasks",
                    json=st,
                    timeout=10
                )
                r.raise_for_status()
                result = r.json()
                wid = st["assignee"]
                print(f"[{now()}] ✅ Assigned to {WORKER_NAMES.get(wid, wid)}: {result['task']['id']}")
            except Exception as e:
                print(f"[{now()}] ❌ Failed to create subtask: {e}")

        # Mark parent as reviewed (Jed has processed it)
        try:
            requests.post(
                f"{DASHBOARD_URL}/api/tasks/{task_id}/update",
                json={"status": "review", "actor": "jed", "progress_notes": "Jed decomposed and assigned subtasks"},
                timeout=10
            )
            print(f"[{now()}] 📋 Parent {task_id} moved to review")
        except Exception as e:
            print(f"[{now()}] ❌ Failed to update parent: {e}")


def now():
    from datetime import datetime
    return datetime.now().strftime("%H:%M:%S")


def main():
    print(f"[{now()}] 🤖 Jed Hermes Manager Poller started")
    print(f"[{now()}] 🔗 Dashboard: {DASHBOARD_URL}")
    print(f"[{now()}] ⏰ Poll interval: {POLL_INTERVAL}s")

    while True:
        poll()
        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()
