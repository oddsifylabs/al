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

---

## 3. Deploy Jed Manager

Create a new service in Railway dashboard:
1. **New** → **Empty Service** → name it `jed-manager`
2. Source: Deploy from `al-manager/Dockerfile`
3. Set env vars:
   - `DASHBOARD_URL` = `http://al-dashboard.railway.internal:8080`
   - `POLL_INTERVAL` = `30`

---

## 4. Deploy Workers

Repeat for each worker. Example for Ruth:

1. **New** → **Empty Service** → name it `ruth-worker`
2. Source: Deploy from `al-workers/Dockerfile`
3. Set env vars:
   - `WORKER_ID` = `ruth`
   - `DASHBOARD_URL` = `http://al-dashboard.railway.internal:8080`
   - `POLL_INTERVAL` = `30`

Repeat with `WORKER_ID` set to:
- `ms-anderson`
- `octavia`
- `mitch`
- `malcom`

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
