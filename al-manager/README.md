# Al Manager — Orchestrator Configuration

The Al Manager is the brain of your digital workforce. It receives tasks, decomposes them, assigns to workers, and reports results.

---

## Quick Setup

### Option 1: Railway (Recommended)

```bash
# Install Hermes Agent
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash

# Create Al Manager profile
hermes profile create al-manager

# Configure personality
hermes --profile al-manager config set agent.personality "You are Al, the Manager agent for a digital workforce. Your role is to receive project requests, decompose them into tasks, assign to specialist workers, track progress via Kanban, and report to the user. CRITICAL: Never execute work yourself — always delegate to workers."

# Enable required tools
hermes --profile al-manager tools enable kanban
hermes --profile al-manager tools enable messaging
hermes --profile al-manager tools enable delegation
hermes --profile al-manager tools enable web

# Set model (adjust for your hardware)
hermes --profile al-manager config set model.default qwen3.5:cloud

# Start gateway
hermes --profile al-manager gateway start
```

### Option 2: Docker

```bash
cd al-deploy/docker
docker-compose up -d al-manager
```

### Option 3: Local

```bash
hermes profile create al-manager
# ... (same config as above)
hermes --profile al-manager chat
```

---

## Configuration File

Location: `~/.hermes/profiles/al-manager/config.yaml`

```yaml
model:
  default: qwen3.5:cloud  # or qwen2.5:7b for low-RAM systems
  provider: ollama-launch

agent:
  personality: "You are Al, the Manager agent..."
  max_turns: 90

toolsets:
  - kanban
  - messaging
  - delegation
  - web
  - file
  - clarify

kanban:
  dispatch_in_gateway: true
  dispatch_interval_seconds: 30
```

---

## Telegram Bot Setup

1. Create bot via [@BotFather](https://t.me/BotFather)
2. Get bot token
3. Add to Hermes config:

```bash
hermes --profile al-manager config set telegram.bot_token YOUR_TOKEN_HERE
hermes --profile al-manager gateway restart
```

4. Start chat: `/start`

---

## Worker Roster

Default workers (customize as needed):

| Worker | Profile | Skills |
|--------|---------|--------|
| Coder | al-coder | github, code-review, testing |
| Writer | al-writer | content-bank, obsidian, research |
| Web Dev | al-webdev | node, react, deployment |
| Marketing | al-marketing | social-media, analytics, airtable |
| Support | al-support | helpdesk, documentation, CRM |

---

## Kanban Workflow

```
1. User → Al: "Build a landing page for our new product"
2. Al creates tasks:
   - T1: al-webdev → Design landing page HTML
   - T2: al-writer → Write landing page copy
   - T3: al-webdev → Integrate copy + deploy
3. Workers complete tasks
4. Al reports: "Landing page complete: https://..."
```

---

## API Endpoints (Future)

```
POST /api/v1/tasks
  - Create new task
  - Returns: task_id, assigned_worker, eta

GET /api/v1/tasks/{id}
  - Get task status
  - Returns: status, progress, output

GET /api/v1/workers
  - List active workers
  - Returns: worker_name, status, current_task

GET /api/v1/dashboard
  - Full Kanban board
  - Returns: all tasks, workers, metrics
```

---

## Troubleshooting

### Manager not responding
```bash
hermes --profile al-manager gateway status
hermes --profile al-manager gateway restart
```

### Workers not receiving tasks
```bash
# Check Kanban dispatch
hermes --profile al-manager kanban list
# Verify worker profiles exist
hermes profile list
```

### Telegram bot offline
```bash
# Check bot token
hermes --profile al-manager config show | grep telegram
# Restart gateway
hermes --profile al-manager gateway restart
```

---

## Next Steps

1. ✅ Manager configured
2. ⏳ Add workers (see `../al-workers/`)
3. ⏳ Deploy dashboard (see `../al-dashboard/`)
4. ⏳ Test workflow

---

**Documentation:** [docs/architecture.md](../docs/architecture.md)
