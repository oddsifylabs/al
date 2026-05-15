# AL Dashboard - Railway Deployment

## Quick Deploy

### Option 1: Railway CLI

```bash
cd ~/al/al-dashboard
railway init
railway up
```

### Option 2: Railway Web UI

1. Go to [railway.app](https://railway.app)
2. Click "New Project"
3. Select "Deploy from GitHub repo" OR "Empty Project"
4. Add your dashboard files
5. Railway auto-detects Flask and deploys

---

## Environment Variables (Set in Railway)

```bash
# Required
HERMES_HOME=/hermes
AL_MANAGER_PROFILE=jed-hermes
PORT=8080

# Optional
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
```

---

## Railway Dashboard URL

After deployment, you'll get a URL like:
```
https://al-dashboard-production.up.railway.app
```

---

## Features

- **Kanban Board** - View all tasks from Jed's kanban.db
- **Worker Status** - See all 6 agents online
- **Chat Interface** - Talk to Jed (Manager) directly
- **Stats Panel** - Task completion metrics

---

## Integration with Agents

The dashboard connects to:
- **Jed (Manager)** - Primary API endpoint
- **Kanban DB** - SQLite database for task tracking
- **All Workers** - Status monitoring via internal Railway network

### Internal API Calls

```python
# From dashboard to Jed (Manager)
JED_URL = "http://jed---the-manager.railway.internal:8080"

# Example: Get tasks from Jed's kanban
requests.get(f"{JED_URL}/api/kanban/tasks")
```

---

## Testing Locally First

```bash
cd ~/al/al-dashboard

# Install dependencies
pip install -r requirements.txt

# Run locally
python app.py

# Open in browser
open http://localhost:8080
```

---

## Production Checklist

- [ ] Set `SECRET_KEY` environment variable
- [ ] Enable HTTPS (Railway does this automatically)
- [ ] Configure `AL_MANAGER_PROFILE` to point to Jed
- [ ] Test Kanban DB connection
- [ ] Verify all 6 workers show as "online"
- [ ] Test chat integration with Jed
