# Hermes Kanban API - Railway Deployment Guide

## 🚀 Deploy to Railway

### Step 1: Push Code to GitHub

```bash
cd ~/al
git add al-kanban-api/
git commit -m "Add Kanban API for Railway deployment"
git push
```

### Step 2: Add New Service in Railway

1. Go to your Railway project (same one with `al-dashboard` and `jed-kanban-api`)
2. Click **New** → **Empty Service**
3. Name it: `hermes-kanban-api`

### Step 3: Configure Build

In Railway dashboard for the new service:

**Root Directory:**
```
al-kanban-api
```

**Dockerfile:**
```
Dockerfile.railway
```

### Step 4: Add Environment Variables

In Railway → Variables tab:

```bash
PORT=8080
RAILWAY_SHARED_VOLUME=/data
KANBAN_DB_PATH=/data/kanban.db
```

### Step 5: Add Persistent Volume (IMPORTANT!)

**Without this, the database resets on every deploy!**

1. Go to **hermes-kanban-api** service in Railway
2. Click **Volumes** tab
3. Click **New Volume**
4. Configure:
   - **Mount Path:** `/data`
   - **Size:** 1 GB (enough for thousands of tasks)
5. Click **Add Volume**

### Step 6: Deploy

Railway will automatically build and deploy!

---

## 📊 After Deployment

**You'll get a URL like:**
```
https://hermes-kanban-api-production.up.railway.app
```

### Test the API:

```powershell
# Health check
curl https://hermes-kanban-api-production.up.railway.app/health

# Get stats
curl https://hermes-kanban-api-production.up.railway.app/api/stats

# Get tasks
curl https://hermes-kanban-api-production.up.railway.app/api/tasks

# Create task
$body = @{title="Test task"; assignee="Ruth"; status="todo"} | ConvertTo-Json
Invoke-RestMethod -Uri "https://hermes-kanban-api-production.up.railway.app/api/tasks" -Method POST -ContentType "application/json" -Body $body
```

---

## 🔧 Then Update Dashboard

Once the Kanban API is live, update the Railway dashboard to use it:

1. Go to **al-dashboard** service in Railway
2. Add environment variable:
   ```
   KANBAN_API_URL=https://hermes-kanban-api-production.up.railway.app
   ```
3. Redeploy the dashboard

---

## 🎯 Then Update Jed

Jed (on Railway) needs to write to the Kanban API instead of local DB.

See: `JED_KANBAN_INTEGRATION.md` for instructions.

---

## 📋 Architecture

```
┌─────────────────────────────────────────────────┐
│              Railway Project                     │
│                                                  │
│  ┌──────────────┐                                │
│  │  Dashboard   │                                │
│  │  (al)        │                                │
│  └──────┬───────┘                                │
│         │                                         │
│         │ GET /api/stats                         │
│         │ GET /api/tasks                         │
│         ▼                                         │
│  ┌──────────────┐                                │
│  │ Hermes       │ ← Shared Volume                │
│  │  Kanban API  │   /data/kanban.db             │
│  └──────┬───────┘                                │
│         ▲                                         │
│         │                                         │
│         │ POST /api/tasks                        │
│         │                                         │
│  ┌──────────────┐                                │
│  │     Jed      │                                │
│  │  (Manager)   │                                │
│  └──────────────┘                                │
└─────────────────────────────────────────────────┘
```

All three services share the same database via the Kanban API!
