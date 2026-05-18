# AL — Autonomous Labor Workforce Hub

**Your AI-powered digital workforce orchestrator.**

AL is a Manager + Specialist agent system that lets you build, deploy, and scale autonomous AI workers. You task the Manager (Jed) through a web dashboard, he decomposes projects into subtasks, assigns them to specialist workers, and tracks progress via a live Kanban board — all hosted on Railway.

---

## 🎯 Architecture

```
You → Dashboard Chat → Kanban DB (PostgreSQL)
                          ↓
                   Jed polls every 30s
                          ↓
              Decomposes → Assigns subtasks
                          ↓
              Workers poll every 30s
                          ↓
              Execute → Report progress → Done
```

All services communicate over Railway's private internal network.

---

## 📚 Task Lifecycle

| Status | Meaning |
|--------|---------|
| `pending_review` | You submitted a task via chat. Jed hasn't seen it yet. |
| `todo` | Jed created/assigned a subtask. Waiting for worker. |
| `in_progress` | Worker picked up the task and is executing. |
| `blocked` | Worker hit an issue and needs help. |
| `review` | Worker finished. Waiting for Jed/your approval. |
| `done` | Approved and complete. |

---

## 📡 Railway Services

| Service | Role | Internal URL |
|---------|------|-------------|
| `al-dashboard` | Web UI + Kanban API + PostgreSQL | `al-dashboard.railway.internal` |
| `jed-manager` | Task decomposition & assignment | `jed---the-manager.railway.internal` |
| `ruth-worker` | Coder | `hermes-agent-edcb.railway.internal` |
| `ms-anderson-worker` | Web Dev | `hermes-agent-14cf.railway.internal` |
| `octavia-worker` | Writer/Admin/Research | `hermes-agent.railway.internal` |
| `mitch-worker` | Sales & Marketing | `hermes-agent-7a4a.railway.internal` |
| `malcom-worker` | Social Media | `hermes-agent-3940.railway.internal` |

---

## 🚀 Quick Start (Local)

```bash
# 1. Clone
git clone https://github.com/oddsifylabs/al
cd al

# 2. Start the stack
cd al-deploy/docker
docker-compose up -d

# 3. Open dashboard
open http://localhost:8080
```

---

## 🚀 Deploy to Railway

1. Add a **PostgreSQL** database in your Railway project
2. Deploy `al-dashboard` service (root `Dockerfile`)
3. Set `DATABASE_URL` env var from Railway PostgreSQL
4. Deploy `jed-manager` service from `al-manager/Dockerfile`
5. Deploy each worker from `al-workers/Dockerfile` with `WORKER_ID` set
6. All services auto-connect via Railway internal DNS

See [DEPLOY.md](DEPLOY.md) for detailed steps.

---

## 📁 Structure

```
al/
├── al-dashboard/          # Central hub (Flask + PostgreSQL + UI)
│   ├── app.py
│   ├── Dockerfile
│   ├── requirements.txt
│   └── templates/
│       └── dashboard.html
├── al-manager/            # Jed Hermes poller
│   ├── jed-poller.py
│   └── Dockerfile
├── al-workers/            # Worker poller template
│   ├── worker-poller.py
│   └── Dockerfile
├── al-deploy/
│   └── docker/
│       └── docker-compose.yml
├── railway.json
└── README.md
```

---

## 🔧 Environment Variables

### Dashboard
- `DATABASE_URL` — PostgreSQL connection string (required)
- `PORT` — defaults to `8080`

### Jed Manager
- `DASHBOARD_URL` — defaults to `http://al-dashboard:8080`
- `POLL_INTERVAL` — defaults to `30` (seconds)

### Workers
- `WORKER_ID` — `ruth`, `ms-anderson`, `octavia`, `mitch`, or `malcom` (required)
- `DASHBOARD_URL` — defaults to `http://al-dashboard:8080`
- `POLL_INTERVAL` — defaults to `30` (seconds)

---

## 📜 License

MIT — Oddsify Labs
