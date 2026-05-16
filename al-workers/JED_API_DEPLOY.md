# Jed Kanban API - Railway Deployment Guide

## 🚀 Deploy to Railway

### Step 1: Add New Service

In Railway Dashboard:
1. Click **New** → **Empty Service**
2. Select your existing project (same as dashboard + workers)
3. Service name: `jed-kanban-api`

### Step 2: Configure Build

**Root Directory:** `al-workers`

**Dockerfile:** `Dockerfile.jed-api`

### Step 3: Add Environment Variables

```bash
# Required
FLASK_ENV=production
PORT=8080
HERMES_HOME=/hermes

# For shared database access (if using volume mount)
KANBAN_DB_PATH=/hermes/profiles/jed-hermes/kanban.db
```

### Step 4: Deploy

Railway will build and deploy automatically.

---

## 🔧 Alternative: Add to Existing Jed Service

If you want to run the Kanban API alongside the Telegram bot in the same service:

### Option A: Multi-Process (Recommended)

Run both the Telegram gateway AND the Kanban API in the same container:

```bash
# Start command for Jed service
hermes --profile jed-hermes gateway start & \
python jed-kanban-api.py
```

### Option B: Separate Services

Keep them separate:
- `jed-the-manager` — Telegram bot (existing)
- `jed-kanban-api` — REST API (new)

Dashboard calls `jed-kanban-api` for data.

---

## 📊 API Endpoints

Once deployed, test the API:

### Health Check
```bash
curl https://jed-kanban-api-production.up.railway.app/health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "jed-hermes"
}
```

### Get Stats
```bash
curl https://jed-kanban-api-production.up.railway.app/api/stats
```

**Response:**
```json
{
  "success": true,
  "stats": {
    "total": 5,
    "todo": 2,
    "in_progress": 1,
    "done": 2
  },
  "source": "Jed (Manager) - Live Kanban DB"
}
```

### Get All Tasks
```bash
curl https://jed-kanban-api-production.up.railway.app/api/tasks
```

**Response:**
```json
{
  "success": true,
  "tasks": [
    {
      "id": "task_20260515_231645",
      "title": "Dashboard integration test",
      "assignee": "Ruth",
      "status": "todo",
      "body": "Test the dashboard integration",
      "created_at": "2026-05-15T23:16:45"
    }
  ]
}
```

### Create Task
```bash
curl -X POST https://jed-kanban-api-production.up.railway.app/api/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "New task", "assignee": "Ms. Anderson", "status": "todo"}'
```

**Response:**
```json
{
  "success": true,
  "message": "Task created",
  "task": {
    "id": "task_20260515_231700",
    "title": "New task",
    "assignee": "Ms. Anderson",
    "status": "todo",
    "created_at": "2026-05-15T23:17:00"
  }
}
```

---

## 🗄️ Database Location

**Challenge:** The Kanban DB needs to be accessible by both:
1. **Jed's Telegram bot** (writes tasks via Telegram)
2. **Kanban API** (reads tasks for dashboard)

### Solution 1: Shared Railway Volume

Mount a persistent volume that both services can access:

```yaml
# In Railway dashboard
Volume: /hermes/profiles/jed-hermes
```

### Solution 2: External Database

Use a shared PostgreSQL/SQLite database on Railway.

### Solution 3: Single Service (Recommended)

Run both the Telegram bot AND Kanban API in the **same service** so they share the same filesystem.

---

## 🎯 Integration with Dashboard

Once deployed, update the dashboard to call the new API:

```python
# Dashboard calls Jed's Kanban API
JED_KANBAN_API = "https://jed-kanban-api-production.up.railway.app"

# Get stats
response = requests.get(f"{JED_KANBAN_API}/api/stats")

# Get tasks
response = requests.get(f"{JED_KANBAN_API}/api/tasks")

# Create task
response = requests.post(f"{JED_KANBAN_API}/api/tasks", json={...})
```

---

## 📈 Next Steps

1. **Deploy Kanban API** to Railway
2. **Test endpoints** (health, stats, tasks)
3. **Update dashboard** to call new API
4. **Integrate with Jed's Telegram bot** (optional — bot writes to same DB)
