# Al Workers — Specialist Agent Templates

Pre-configured specialist workers for common roles. Each worker is a Hermes Agent profile optimized for specific tasks.

---

## Available Workers

| Worker | Profile | Best For |
|--------|---------|----------|
| `coder` | al-coder | Software development, code review, debugging |
| `writer` | al-writer | Content creation, editing, research |
| `webdev` | al-webdev | Web development, deployment, frontend/backend |
| `marketing` | al-marketing | Social media, campaigns, analytics |
| `support` | al-support | Customer service, documentation, helpdesk |
| `analyst` | al-analyst | Data analysis, research synthesis, reports |

---

## Quick Setup

### Add a Worker

```bash
# Navigate to workers directory
cd al-workers

# Add a worker (interactive)
./add-worker.sh coder

# Or specify all options
./add-worker.sh --name al-coder --role coder --skills github,code-review,testing
```

### Manual Setup

```bash
# Create worker profile
hermes profile create al-coder

# Set personality
hermes --profile al-coder config set agent.personality "You are a specialist coder worker in the Al digital workforce. You write clean, tested code. You follow best practices. You document your work. You report progress to the Al Manager."

# Enable tools
hermes --profile al-coder tools enable terminal
hermes --profile al-coder tools enable file
hermes --profile al-coder tools enable code_execution
hermes --profile al-coder tools enable github

# Set model
hermes --profile al-coder config set model.default qwen3.5:cloud

# Start gateway (if using Telegram)
hermes --profile al-coder gateway start
```

---

## Worker Templates

### Coder (`coder/`)

```yaml
profile: al-coder
personality: "Specialist coder worker"
tools:
  - terminal
  - file
  - code_execution
  - github
skills:
  - claude-code (optional)
  - github-pr-workflow
  - test-driven-development
  - systematic-debugging
```

### Writer (`writer/`)

```yaml
profile: al-writer
personality: "Specialist writer worker"
tools:
  - web
  - file
  - search
  - memory
skills:
  - oddsify-content-bank
  - obsidian
  - humanizer
  - youtube-content
```

### Web Dev (`webdev/`)

```yaml
profile: al-webdev
personality: "Specialist web developer worker"
tools:
  - terminal
  - file
  - browser
  - code_execution
skills:
  - github-pr-workflow
  - node-inspect-debugger
  - test-driven-development
  - claude-design
```

### Marketing (`marketing/`)

```yaml
profile: al-marketing
personality: "Specialist marketing worker"
tools:
  - web
  - messaging
  - file
  - cronjob
skills:
  - oddsify-social-media
  - oddsify-follower-growth
  - oddsify-content-bank
  - xurl
```

---

## Custom Workers

Build your own specialist worker:

```bash
# Use the SDK
cd ../al-sdk
./create-worker.sh my-specialist

# Edit the profile
nano ~/.hermes/profiles/al-my-specialist/config.yaml

# Test
hermes --profile al-my-specialist chat
```

See [al-sdk/README.md](../al-sdk/README.md) for full documentation.

---

## Worker Communication

Workers communicate with the Manager via:

1. **Kanban Board** — Task status updates
2. **Telegram Group** — All workers + Manager in one group
3. **Direct Messages** — Manager ↔ Worker for sensitive info

### Telegram Group Setup

```bash
# Add all workers to group
# Group ID: telegram:-1003936982744 (example)

# Each worker bot joins the group
# Manager coordinates via mentions or direct assignment
```

---

## Scaling Workers

Run multiple instances of the same worker type:

```bash
# Worker pool for high-volume tasks
hermes profile create al-coder-1
hermes profile create al-coder-2
hermes profile create al-coder-3

# Manager distributes tasks across pool
# Kanban handles load balancing automatically
```

---

## Monitoring

```bash
# Check worker status
hermes profile list | grep al-

# View active tasks
hermes --profile al-manager kanban list

# Check worker logs
tail -f ~/.hermes/logs/gateway.log | grep al-coder
```

---

## Best Practices

1. **One Profile Per Worker** — Each specialist gets its own Hermes profile
2. **Shared Kanban Board** — All workers use the same board (via Manager)
3. **Unique Bot Tokens** — Each worker needs its own Telegram bot
4. **Consistent Naming** — Use `al-{role}` convention
5. **Document Custom Workers** — Add to `examples/` directory

---

## Next Steps

1. ✅ Choose workers you need
2. ⏳ Run `./add-worker.sh` for each
3. ⏳ Configure Telegram bots
4. ⏳ Test with sample tasks

---

**Documentation:** [docs/worker-sdk.md](../docs/worker-sdk.md)
