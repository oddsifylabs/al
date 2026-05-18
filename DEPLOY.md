# Deploy AL to Railway

## Prerequisites

- Railway CLI installed (`npm i -g @railway/cli`)
- Logged in: `railway login`
- Linked to project: `railway link` (project `aa760255-42bb-43f3-84aa-545b89060460`)

---

## 1. Add PostgreSQL

In the Railway dashboard:
1. Click **New** → **Database** → **Add PostgreSQL**
2. Copy the `DATABASE_URL` from the **Connect** tab

---

## 2. Deploy Dashboard

```bash
cd al-dashboard
railway up
```

Set env vars in Railway dashboard:
- `DATABASE_URL` = (from PostgreSQL)
- `FLASK_ENV` = `production`
- `PORT` = `8080`
- `RAILWAY_API_TOKEN` = (optional — get from Railway dashboard → Account Settings → Tokens)
- `RAILWAY_PROJECT_ID` = `aa760255-42bb-43f3-84aa-545b89060460`

With `RAILWAY_API_TOKEN` and `RAILWAY_PROJECT_ID` set, the dashboard exposes:
- `GET /api/railway/services` — list all services with health status
- `GET /api/railway/logs/<service_name>?lines=100` — fetch logs
- `POST /api/railway/restart/<service_name>` — restart without rebuild
- `POST /api/railway/redeploy/<service_name>` — trigger new deployment
- `GET /api/railway/status` — project health summary

---

## 3. Deploy Jed Manager

Create a new service in Railway dashboard:
1. **New** → **Empty Service** → name it `jed-manager`
2. Source: Deploy from `al-manager/Dockerfile`
3. Set env vars:
   - `DASHBOARD_URL` = `http://al-dashboard.railway.internal:8080`
   - `POLL_INTERVAL` = `30`
   - `OPENROUTER_API_KEY` = (your OpenRouter key — get one at openrouter.ai)
   - `OPENROUTER_MODEL` = `qwen/qwen3.5:cloud` (or any OpenRouter model)

Without `OPENROUTER_API_KEY`, Jed falls back to keyword-based assignment.

---

## 4. Deploy Workers

Repeat for each worker. Example for Ruth:

1. **New** → **Empty Service** → name it `ruth-worker`
2. Source: Deploy from `al-workers/Dockerfile`
3. Set env vars:
   - `WORKER_ID` = `ruth`
   - `DASHBOARD_URL` = `http://al-dashboard.railway.internal:8080`
   - `POLL_INTERVAL` = `30`
   - `HERMES_PROFILE` = `ruth-hermes` (optional, defaults to `{WORKER_ID}-hermes`)
   - `HERMES_CMD` = `hermes` (optional, path to Hermes CLI)
   - `HERMES_TIMEOUT` = `300` (optional, seconds per task)

Repeat with `WORKER_ID` set to:
- `ms-anderson`
- `octavia`
- `mitch`
- `malcom`

### Hermes Integration

For workers to actually execute tasks (not just simulate), Hermes must be installed in the container. Two options:

**Option A: Pre-install Hermes in the Dockerfile**
```dockerfile
# Add to al-workers/Dockerfile before CMD
RUN pip install hermes-agent  # or however Hermes is distributed
```

**Option B: Mount Hermes as a volume**
If Hermes is already installed on a Railway volume, set `HERMES_CMD` to the full path.

**Option C: Fallback mode**
If Hermes is not available, workers still run but use limited fallback execution (web search, basic analysis). The dashboard will show the result and note that Hermes was unavailable.

---

## 5. Verify

```bash
# Dashboard health
curl https://your-dashboard-url.railway.app/health

# Stats
curl https://your-dashboard-url.railway.app/api/stats

# Workers
curl https://your-dashboard-url.railway.app/api/workers
```

---

## Internal Network Reference

All services in the same Railway project can reach each other via:
```
http://<service-name>.railway.internal:<port>
```

Make sure your `DASHBOARD_URL` uses the internal URL so traffic stays within Railway's network.

---

## Task Flow Example

1. You send "Create a landing page for our new product" in dashboard chat
2. Dashboard creates task with `status: pending_review`
3. Jed polls, sees the task, calls OpenRouter LLM
4. LLM decomposes into:
   - "Design landing page mockup" → ms-anderson
   - "Write landing page copy" → octavia
   - "Build HTML/CSS landing page" → ms-anderson
   - "Set up conversion tracking" → mitch
5. Jed creates 4 subtasks with `status: todo`
6. Workers poll, pick up their tasks, invoke Hermes to execute
7. Results flow back to dashboard, tasks move to `done`
