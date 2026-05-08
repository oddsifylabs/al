# Al Dashboard — Web GUI

The Al Dashboard is your command center for managing your digital workforce.

---

## Features

- **Chat Interface** — Talk to Al Manager directly
- **Kanban Board** — Visual task tracking
- **Worker Status** — See who's online and what they're working on
- **Activity Feed** — Real-time updates from all workers
- **Analytics** — Task completion rates, worker performance

---

## Quick Start

### Development

```bash
cd al-dashboard
pip install -r requirements.txt
python app.py
open http://localhost:8080
```

### Production (Docker)

```bash
cd ../al-deploy/docker
docker-compose up -d al-dashboard
```

### Production (Railway)

```bash
cd ../al-deploy/railway
railway up
```

---

## Architecture

```
┌─────────────────────────────────────────┐
│  React Frontend                         │
│  - Chat UI                              │
│  - Kanban Board                         │
│  - Worker Status Panel                  │
└─────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│  Flask Backend                          │
│  - REST API                             │
│  - WebSocket (real-time updates)        │
│  - Hermes integration                   │
└─────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│  Al Manager (Hermes Profile)            │
│  - Kanban board (SQLite)                │
│  - Worker coordination                  │
└─────────────────────────────────────────┘
```

---

## API Endpoints

```
GET  /api/tasks           - List all tasks
POST /api/tasks           - Create new task
GET  /api/tasks/{id}      - Get task details
PUT  /api/tasks/{id}      - Update task
DELETE /api/tasks/{id}    - Delete task

GET  /api/workers         - List workers
GET  /api/workers/{id}    - Get worker status
POST /api/workers/{id}/action - Send command to worker

GET  /api/dashboard       - Full dashboard data
POST /api/chat            - Chat with Al Manager
```

---

## Environment Variables

```bash
# Required
AL_MANAGER_PROFILE=al-manager
HERMES_HOME=/home/user/.hermes

# Optional
FLASK_ENV=production
SECRET_KEY=your-secret-key
WEBSOCKET_ENABLED=true

# Telegram (for notifications)
TELEGRAM_BOT_TOKEN=your-token
TELEGRAM_CHAT_ID=your-chat-id
```

---

## Screenshots (Coming Soon)

- Dashboard overview
- Kanban board view
- Chat interface
- Worker management
- Analytics panel

---

## Customization

### Themes

Edit `static/css/theme.css` to customize colors, fonts, and layout.

### Branding

Replace logo in `static/img/al-logo.svg`.

### Custom Widgets

Add widgets to `templates/dashboard/widgets/`.

---

## Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run development server
python app.py --debug

# Run tests
pytest tests/

# Build frontend (if using React)
cd frontend
npm install
npm run build
```

---

## Deployment Checklist

- [ ] Set `FLASK_ENV=production`
- [ ] Configure `SECRET_KEY`
- [ ] Enable HTTPS (Railway handles this)
- [ ] Set up database migrations
- [ ] Configure WebSocket for real-time updates
- [ ] Test all API endpoints
- [ ] Enable error logging
- [ ] Set up monitoring (Sentry, etc.)

---

**Next:** [Deployment Guide](../al-deploy/README.md)
