#!/usr/bin/env python3
"""
Jed Hermes — Manager Poller with LLM Decomposition
Polls AL Dashboard for pending_review tasks, uses LLM to decompose and assign.
Runs as a sidecar inside the Jed Hermes Railway service.
"""

import os
import re
import json
import time
import requests

# ── Config ──────────────────────────────────────────────────────────
DASHBOARD_URL = os.environ.get("DASHBOARD_URL", "http://al-dashboard:8080")
POLL_INTERVAL = int(os.environ.get("POLL_INTERVAL", "30"))

# LLM Config — OpenRouter recommended for Railway
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
OPENROUTER_MODEL = os.environ.get("OPENROUTER_MODEL", "qwen/qwen3.5:cloud")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

WORKER_NAMES = {
    "ruth": "Ruth Hermes (Coder)",
    "ms-anderson": "Ms. Anderson (Web Dev)",
    "octavia": "Octavia Hermes (Writer/Admin/Research)",
    "mitch": "Mitch Hermes (Sales & Marketing)",
    "malcom": "Malcom Hermes (Social Media)",
}

WORKER_KEYWORDS = {
    "ruth": ["code", "bug", "fix", "python", "javascript", "js", "node", "api", "backend", "script", "function", "deploy", "docker", "git", "test", "debug", "refactor", "database", "sql", "programming", "software", "development", "app", "integration"],
    "ms-anderson": ["website", "web", "html", "css", "ui", "design", "frontend", "page", "layout", "responsive", "figma", "component", "react", "vue", "angular", "wordpress", "shopify", "theme", "styling", "tailwind"],
    "octavia": ["write", "blog", "article", "content", "copy", "admin", "research", "doc", "documentation", "email", "report", "summary", "note", "edit", "proofread", "draft", "press release", "newsletter", "analysis"],
    "mitch": ["sales", "marketing", "lead", "campaign", "outreach", "seo", "ads", "funnel", "conversion", "promotion", "brand", "newsletter", "prospect", "crm", "hubspot", "landing page", "copywriting", "strategy"],
    "malcom": ["social", "twitter", "x.com", "post", "instagram", "linkedin", "tiktok", "facebook", "thread", "engagement", "follower", "content calendar", "schedule", "hashtag", "viral", "community", "reply", "comment"],
}

SYSTEM_PROMPT = """You are Jed Hermes, the Manager of the Autonomous Labor workforce at Oddsify Labs.

Your team:
- ruth → Ruth Hermes (Coder): writes code, fixes bugs, builds APIs, handles deployments
- ms-anderson → Ms. Anderson (Web Dev): builds websites, frontend, UI/UX, responsive design
- octavia → Octavia Hermes (Writer/Admin/Research): writes content, docs, research, admin tasks
- mitch → Mitch Hermes (Sales & Marketing): sales, campaigns, SEO, lead generation, branding
- malcom → Malcom Hermes (Social Media): social media posts, engagement, content calendars

When given a task, decompose it into 1-5 subtasks. Each subtask should be:
- Clear and actionable
- Assigned to exactly one worker
- Sized to complete in one work session

Respond ONLY with valid JSON in this format:
{
  "reasoning": "brief explanation of your assignment strategy",
  "subtasks": [
    {
      "title": "short task title",
      "body": "detailed instructions for the worker",
      "assignee": "worker_id",
      "priority": 0
    }
  ]
}

Worker IDs must be one of: ruth, ms-anderson, octavia, mitch, malcom.
Priority is 0 (normal), 1 (high), 2 (urgent)."""


def now():
    from datetime import datetime
    return datetime.now().strftime("%H:%M:%S")


def llm_decompose(task: dict) -> dict:
    """Call OpenRouter to decompose a task into subtasks"""
    if not OPENROUTER_API_KEY:
        print(f"[{now()}] ⚠️  No OPENROUTER_API_KEY, falling back to keyword matching")
        return keyword_decompose(task)

    user_prompt = f"Task from Director:\nTitle: {task['title']}\nBody: {task.get('body', '')}\n\nDecompose this into subtasks and assign to workers."

    try:
        r = requests.post(
            OPENROUTER_URL,
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://oddsifylabs.com",
                "X-Title": "AL Worker Hub"
            },
            json={
                "model": OPENROUTER_MODEL,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": 0.3,
                "response_format": {"type": "json_object"}
            },
            timeout=60
        )
        r.raise_for_status()
        data = r.json()
        content = data["choices"][0]["message"]["content"]
        parsed = json.loads(content)
        return parsed
    except Exception as e:
        print(f"[{now()}] ❌ LLM decomposition failed: {e}")
        return keyword_decompose(task)


def keyword_decompose(task: dict) -> dict:
    """Fallback keyword-based decomposition"""
    text = f"{task['title']} {task.get('body', '')}".lower()
    scores = {}
    for worker, keywords in WORKER_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in text)
        if score:
            scores[worker] = score

    if scores:
        assignee = max(scores, key=scores.get)
    else:
        assignee = "ruth"

    return {
        "reasoning": "Keyword-based fallback assignment",
        "subtasks": [{
            "title": task["title"],
            "body": task.get("body", ""),
            "assignee": assignee,
            "priority": 0
        }]
    }


def process_task(task: dict):
    """Decompose a task and create subtasks on the dashboard"""
    task_id = task["id"]
    print(f"[{now()}] 🧠 Decomposing: {task['title'][:60]}")

    decomposition = llm_decompose(task)
    subtasks = decomposition.get("subtasks", [])

    if not subtasks:
        print(f"[{now()}] ⚠️  No subtasks generated, creating single assignment")
        subtasks = keyword_decompose(task)["subtasks"]

    print(f"[{now()}] 📝 {len(subtasks)} subtask(s) — {decomposition.get('reasoning', '')[:80]}")

    for st in subtasks:
        assignee = st.get("assignee", "ruth")
        if assignee not in WORKER_NAMES:
            assignee = "ruth"

        payload = {
            "title": st.get("title", task["title"]),
            "body": st.get("body", ""),
            "assignee": assignee,
            "status": "todo",
            "priority": st.get("priority", 0),
            "parent_id": task_id,
            "created_by": "jed"
        }

        try:
            r = requests.post(f"{DASHBOARD_URL}/api/tasks", json=payload, timeout=10)
            r.raise_for_status()
            result = r.json()
            print(f"[{now()}] ✅ Assigned to {WORKER_NAMES.get(assignee, assignee)}: {result['task']['id']}")
        except Exception as e:
            print(f"[{now()}] ❌ Failed to create subtask: {e}")

    # Mark parent as reviewed (Jed has processed it)
    try:
        requests.post(
            f"{DASHBOARD_URL}/api/tasks/{task_id}/update",
            json={
                "status": "review",
                "actor": "jed",
                "progress_notes": f"Jed decomposed into {len(subtasks)} subtask(s). Reasoning: {decomposition.get('reasoning', 'N/A')[:200]}"
            },
            timeout=10
        )
        print(f"[{now()}] 📋 Parent {task_id} moved to review")
    except Exception as e:
        print(f"[{now()}] ❌ Failed to update parent: {e}")


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
        process_task(task)


def main():
    print(f"[{now()}] 🤖 Jed Hermes Manager Poller started")
    print(f"[{now()}] 🔗 Dashboard: {DASHBOARD_URL}")
    print(f"[{now()}] 🧠 LLM: {OPENROUTER_MODEL if OPENROUTER_API_KEY else 'KEYWORD FALLBACK'}")
    print(f"[{now()}] ⏰ Poll interval: {POLL_INTERVAL}s")

    while True:
        poll()
        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()
