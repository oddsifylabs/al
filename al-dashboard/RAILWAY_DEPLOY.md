# AL Dashboard - Railway Deployment Guide

## 🚀 Quick Deploy

### Option 1: Railway CLI (Recommended)

```powershell
# Navigate to dashboard folder
cd "C:\claude projects\al\al-dashboard"

# Login to Railway
railway login

# Initialize (first time only) - select existing project
railway init

# Deploy
railway up
```

### Option 2: Railway Dashboard (GitHub)

1. Go to https://railway.app
2. Click **New Project**
3. Select **Deploy from GitHub repo**
4. Choose `oddsifylabs/al`
5. Select **al-dashboard** as the root directory
6. Add environment variables (see below)
7. Click **Deploy**

---

## 🔧 Environment Variables

Add these in Railway dashboard → Variables:

```bash
# Required
FLASK_ENV=production
PORT=8080
HERMES_HOME=/hermes

# Optional (for future Telegram integration)
AL_MANAGER_PROFILE=jed-hermes
TELEGRAM_BOT_TOKEN=<your-bot-token>
```

---

## 🌐 Internal Railway Network

Once deployed, the dashboard can communicate with workers via internal URLs:

| Service | Internal URL | External URL |
|---------|--------------|--------------|
| **Dashboard** | `al-dashboard.railway.internal` | `https://al-dashboard-production.up.railway.app` |
| **Jed (Manager)** | `jed---the-manager.railway.internal` | `https://jed-the-manager-production.up.railway.app` |
| **Ruth** | `hermes-agent-edcb.railway.internal` | `https://hermes-agent-production-4fd7.up.railway.app` |
| **Ms. Anderson** | `hermes-agent-14cf.railway.internal` | `https://hermes-agent-production-6fc9.up.railway.app` |
| **Octavia** | `hermes-agent.railway.internal` | `https://hermes-agent-production-8b69.up.railway.app` |
| **Mitch** | `hermes-agent-7a4a.railway.internal` | `https://hermes-agent-production-51e6.up.railway.app` |
| **Malcom** | `hermes-agent-3940.railway.internal` | `https://hermes-agent-production-5b79.up.railway.app` |

### Example: Dashboard → Jed API Call

```python
# Internal Railway network (fast, no public internet)
JED_URL = "http://jed---the-manager.railway.internal:8080"
response = requests.get(f"{JED_URL}/api/tasks")
```

---

## 📊 Dashboard Features

Once deployed, you'll have:

- ✅ **Public URL** — Access from anywhere
- ✅ **Workers List** — 6 agents with status
- ✅ **Kanban Board** — Tasks from Jed's database
- ✅ **Stats Panel** — Real-time metrics
- ✅ **Chat Interface** — Message Jed directly

---

## 🔍 Verify Deployment

```bash
# Check service status
railway status

# View logs
railway logs

# Open in browser
railway open
```

---

## 🛠️ Troubleshooting

**Dashboard won't start:**
```bash
# Check logs
railway logs

# Common issues:
# - Missing environment variables
# - Port not set to 8080
# - Dockerfile path wrong
```

**Can't access internal services:**
- Ensure all services are in the **same Railway project**
- Use internal URLs (not external) for service-to-service calls
- Internal URLs don't need authentication

**Workers show offline:**
- Dashboard currently shows static list (all online)
- Future: Integrate with Railway API for real status

---

## 📈 Next Steps

1. **Deploy dashboard** to Railway
2. **Test public URL** from your phone/browser
3. **Integrate with Jed** for real Kanban data
4. **Add chat** → forward messages to Jed's Telegram bot
