#!/usr/bin/env python3
"""
AL Worker Poller Template with Hermes Integration
Each worker deploys this script. It polls the AL Dashboard for assigned tasks,
invokes the Hermes agent for real execution, and reports progress back.

Set WORKER_ID env var to one of: ruth, ms-anderson, octavia, mitch, malcom
"""

import os
import sys
import time
import json
import requests
import subprocess
import shutil

# ── Config ──────────────────────────────────────────────────────────
DASHBOARD_URL = os.environ.get("DASHBOARD_URL", "http://al-dashboard:8080")
WORKER_ID = os.environ.get("WORKER_ID")
POLL_INTERVAL = int(os.environ.get("POLL_INTERVAL", "30"))

# Hermes integration config
HERMES_PROFILE = os.environ.get("HERMES_PROFILE", f"{WORKER_ID}-hermes" if WORKER_ID else "")
HERMES_CMD = os.environ.get("HERMES_CMD", "hermes")
HERMES_TIMEOUT = int(os.environ.get("HERMES_TIMEOUT", "300"))  # 5 min default

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


def hermes_available() -> bool:
    """Check if Hermes CLI is installed"""
    return shutil.which(HERMES_CMD) is not None


def invoke_hermes(task_title: str, task_body: str) -> dict:
    """
    Invoke Hermes agent to execute a task.
    Returns {"success": bool, "output": str, "error": str}
    """
    if not hermes_available():
        return {
            "success": False,
            "output": "",
            "error": f"Hermes CLI not found: {HERMES_CMD}. Install Hermes or set HERMES_CMD env var."
        }

    # Build the task prompt for Hermes
    prompt = f"""You are {WORKER_ID}, a specialist worker in the Autonomous Labor workforce.

TASK TITLE: {task_title}

TASK DETAILS:
{task_body}

Execute this task to the best of your ability. Use your available tools if needed.
Provide a clear summary of what you did and the final result."""

    # Try different Hermes invocation patterns
    # Pattern 1: hermes chat --profile <profile> "<message>"
    # Pattern 2: hermes --profile <profile> chat "<message>"
    # Pattern 3: hermes run --profile <profile> --message "<message>"

    commands_to_try = [
        [HERMES_CMD, "--profile", HERMES_PROFILE, "chat", prompt],
        [HERMES_CMD, "chat", "--profile", HERMES_PROFILE, prompt],
    ]

    last_error = ""
    for cmd in commands_to_try:
        try:
            print(f"[{now()}] 🚀 Spawning Hermes: {' '.join(cmd[:4])}...")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=HERMES_TIMEOUT,
                env={**os.environ, "HERMES_NONINTERACTIVE": "1"}
            )

            if result.returncode == 0:
                return {
                    "success": True,
                    "output": result.stdout.strip() or "(no output)",
                    "error": ""
                }
            else:
                last_error = result.stderr.strip() or f"Exit code {result.returncode}"
                print(f"[{now()}] ⚠️  Hermes command failed: {last_error[:100]}")
                continue

        except subprocess.TimeoutExpired:
            last_error = f"Hermes timed out after {HERMES_TIMEOUT}s"
            print(f"[{now()}] ⏰ Hermes timed out")
            break
        except Exception as e:
            last_error = str(e)
            print(f"[{now()}] ❌ Hermes spawn error: {e}")
            continue

    return {
        "success": False,
        "output": "",
        "error": f"All Hermes invocation patterns failed. Last error: {last_error[:500]}"
    }


def fallback_execute(task_title: str, task_body: str) -> dict:
    """
    Fallback execution when Hermes is not available.
    Uses Python to perform basic task types based on keywords.
    """
    text = f"{task_title} {task_body}".lower()
    result_parts = [f"# Task Execution by {WORKER_ID}", f"Task: {task_title}", ""]

    # Basic web search capability
    if any(kw in text for kw in ["search", "find", "look up", "research"]):
        try:
            # Simple DuckDuckGo search via requests
            from urllib.parse import quote
            query = quote(task_title)
            r = requests.get(
                f"https://html.duckduckgo.com/html/?q={query}",
                headers={"User-Agent": "AL-Worker/1.0"},
                timeout=15
            )
            if r.status_code == 200:
                # Extract first few result titles
                import re
                titles = re.findall(r'<a[^>]+class="result__a"[^>]*>(.*?)</a>', r.text)
                result_parts.append("## Search Results")
                for t in titles[:5]:
                    clean = re.sub(r'<[^>]+>', '', t)
                    result_parts.append(f"- {clean}")
                result_parts.append("")
        except Exception as e:
            result_parts.append(f"Search failed: {e}")

    # Basic file operations
    if any(kw in text for kw in ["write", "create file", "save", "generate"]):
        result_parts.append("## File Generation")
        result_parts.append("(File generation requires Hermes for safe execution)")
        result_parts.append("")

    # Basic code execution
    if any(kw in text for kw in ["code", "script", "function", "program"]):
        result_parts.append("## Code Execution")
        result_parts.append("(Code execution requires Hermes for safe sandboxed execution)")
        result_parts.append("")

    result_parts.append("---")
    result_parts.append("**Note:** This is fallback execution. Hermes CLI was not available for full tool access.")
    result_parts.append("Install Hermes in this container or set HERMES_CMD to enable full capabilities.")

    return {
        "success": True,
        "output": "\n".join(result_parts),
        "error": ""
    }


def execute_task(task: dict) -> dict:
    """
    Execute a task. Tries Hermes first, falls back to direct execution.
    """
    task_id = task["id"]
    title = task.get("title", "")
    body = task.get("body", "")

    print(f"[{now()}] 🚀 Executing task {task_id}: {title[:60]}")

    # Report that we're starting
    report_progress(task_id, "in_progress", f"{WORKER_ID} started work on: {title[:80]}")

    # Try Hermes first
    if hermes_available():
        result = invoke_hermes(title, body)
    else:
        print(f"[{now()}] ⚠️  Hermes not available, using fallback execution")
        result = fallback_execute(title, body)

    # Report completion
    if result["success"]:
        report_progress(
            task_id,
            "done",
            f"{WORKER_ID} completed the task",
            result=result["output"]
        )
    else:
        report_progress(
            task_id,
            "blocked",
            f"{WORKER_ID} encountered an error",
            result=result["error"]
        )

    return result


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
    print(f"[{now()}] 🧠 Hermes profile: {HERMES_PROFILE}")
    print(f"[{now()}] 📋 Hermes available: {hermes_available()}")
    print(f"[{now()}] ⏰ Poll interval: {POLL_INTERVAL}s")

    while True:
        send_heartbeat()
        poll()
        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()
