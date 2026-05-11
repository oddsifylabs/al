# Al Configuration — Your Digital Workforce

## Agent Profiles

### Manager
| Profile | Role | Host | Status |
|---------|------|------|--------|
| `jed-hermes` | Manager (Jed) | Local PC | ✅ Configured |

### Workers
| Profile | Role | Host | Status |
|---------|------|------|--------|
| `ruth-hermes` | Coder (Ruth) | Local PC | ✅ Configured |
| `ms-anderson` | Web Dev (Ms. Anderson) | Local PC | ✅ Configured |
| `octavia-hermes` | Writer/Admin (Octavia) | Local PC | ✅ Configured |
| `mitch-hermes` | Marketing (Mitch) | Local PC | ✅ Configured |
| `markus` (separate) | Social Media (Markus) | Local PC | ✅ Running |

## Model Configuration

All agents use: `qwen3.5:cloud` (Ollama)

## Telegram Setup

Each agent needs its own bot token:

```bash
# For each profile, set the bot token
hermes --profile jed-hermes config set telegram.bot_token YOUR_JED_BOT_TOKEN
hermes --profile ruth-hermes config set telegram.bot_token YOUR_RUTH_BOT_TOKEN
hermes --profile ms-anderson config set telegram.bot_token YOUR_MS_ANDERSON_BOT_TOKEN
hermes --profile octavia-hermes config set telegram.bot_token YOUR_OCTAVIA_BOT_TOKEN
hermes --profile mitch-hermes config set telegram.bot_token YOUR_MITCH_BOT_TOKEN
```

## Starting Agents

```bash
# Start all gateways
hermes --profile jed-hermes gateway start
hermes --profile ruth-hermes gateway start
hermes --profile ms-anderson gateway start
hermes --profile octavia-hermes gateway start
hermes --profile mitch-hermes gateway start
```

## Testing the System

1. Message Jed on Telegram: `/start`
2. Give Jed a task: "Create a landing page for our new product"
3. Watch Kanban board: `hermes --profile jed-hermes kanban list`
4. Check dashboard: `http://localhost:8080`
