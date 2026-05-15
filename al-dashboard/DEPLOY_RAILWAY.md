# AL Dashboard - Railway Deployment Guide

## Quick Deploy Steps

### Step 1: Login to Railway

**Option A: Browser Login (Recommended)**
```bash
cd C:\Windows\System32\al\al-dashboard
railway login
```
This will open your browser — click "Authorize" when prompted.

**Option B: API Token**
1. Go to https://railway.app/dashboard
2. Click your profile → **Settings** → **API Tokens**
3. Generate a new token
4. Set environment variable:
   ```powershell
   $env:RAILWAY_TOKEN="your-token-here"
   ```

---

### Step 2: Initialize Railway Project

```bash
cd C:\Windows\System32\al\al-dashboard
railway init
```

**When prompted:**
- **Create new project?** → Yes
- **Project name:** `al-dashboard`
- **Region:** Choose closest to you (e.g., `us-east`)

---

### Step 3: Deploy

```bash
railway up
```

Railway will:
1. Detect Flask (`requirements.txt`)
2. Build the Docker image
3. Deploy to a public URL

---

### Step 4: Set Environment Variables

In Railway Dashboard (https://railway.app):

1. Go to your `al-dashboard` project
2. Click **Variables** tab
3. Add these:

```bash
HERMES_HOME=/hermes
AL_MANAGER_PROFILE=jed-hermes
FLASK_ENV=production
SECRET_KEY=<generate-random-string>
PORT=8080
```

---

### Step 5: Get Your Dashboard URL

After deployment, Railway gives you a URL like:
```
https://al-dashboard-production.up.railway.app
```

**To find it:**
```bash
railway open
```
Or check the Railway dashboard → Your project → **Settings** → **Domains**

---

### Step 6: Test the Dashboard

Open in browser:
```
https://<your-railway-url>.up.railway.app
```

You should see:
- ✅ 6 Workers listed (Jed, Ruth, Ms. Anderson, Octavia, Mitch, Markus)
- ✅ Stats panel (0 tasks initially)
- ✅ Kanban board (empty until tasks are created)
- ✅ Chat interface (placeholder)

---

## Troubleshooting

### Build Fails
```bash
# Check logs
railway logs

# Re-deploy
railway up --force-create
```

### Wrong Python Version
Railway auto-detects Python 3.11. If needed, add `runtime.txt`:
```bash
echo "python-3.11" > runtime.txt
git add runtime.txt
git commit -m "Add Python runtime"
railway up
```

### Port Issues
Railway auto-sets the `PORT` env var. The dashboard already reads it:
```python
port = int(os.environ.get('PORT', 8080))
```

---

## Alternative: Deploy via GitHub

1. **Push to GitHub:**
   ```bash
   cd C:\Windows\System32\al\al-dashboard
   git init
   git add .
   git commit -m "AL Dashboard ready for Railway"
   git remote add origin https://github.com/oddsifylabs/al-dashboard.git
   git push -u origin main
   ```

2. **Deploy from Railway UI:**
   - Go to https://railway.app
   - Click **New Project** → **Deploy from GitHub repo**
   - Select `oddsifylabs/al-dashboard`
   - Railway auto-deploys on every push

---

## Post-Deployment: Connect to Jed (Manager)

The dashboard needs to know Jed's internal Railway URL. Add this env var:

```bash
JED_INTERNAL_URL=http://jed---the-manager.railway.internal:8080
```

This allows the dashboard to:
- Pull real-time Kanban tasks
- Send chat messages to Jed
- Get worker status from actual gateways

---

## Current Status

| Component | Status |
|-----------|--------|
| Dashboard Code | ✅ Ready (`~/al/al-dashboard/`) |
| Requirements | ✅ Flask, gunicorn, requests installed |
| Railway CLI | ✅ Installed (v4.57.0) |
| Authentication | ⏳ Needs login |
| Deployment | ⏳ Pending |

---

**Next:** Run the commands above on your Windows machine to deploy! 🚀
