# AL Workforce - Railway Deployment Configuration

## Overview
This deploys the 6-agent AL workforce to Railway with webhook mode for Telegram.

## Agents - Deployment Information

| Agent | Role | Bot Username | External URL | Internal URL |
|-------|------|--------------|--------------|--------------|
| **Jed** | Manager/Orchestrator | @JedHermesOLBOT | `jed-the-manager-production.up.railway.app` | `jed---the-manager.railway.internal` |
| **Ruth** | Coder/Web Dev/Automation | @RuthHermesBot | `hermes-agent-production-4fd7.up.railway.app` | `hermes-agent-edcb.railway.internal` |
| **Ms. Anderson** | Editor | @MsAndersonBOT | `hermes-agent-production-6fc9.up.railway.app` | `hermes-agent-14cf.railway.internal` |
| **Octavia** | Admin | @OctaviaHermesBot | `hermes-agent-production-8b69.up.railway.app` | `hermes-agent.railway.internal` |
| **Mitch** | Sales/Marketing | @MitchHermesBot | `hermes-agent-production-51e6.up.railway.app` | `hermes-agent-7a4a.railway.internal` |
| **Malcom** | Social Media | @MalcomSMMBot | `hermes-agent-production-5b79.up.railway.app` | `hermes-agent-3940.railway.internal` |

## Bot Tokens Reference

| Agent | Token |
|-------|-------|
| Jed | `8437636581:AAFPG81Y5LCR5cQ9ESdkvnhKYRZ9LDjbN3E` |
| Ruth | `8637717794:AAHjVxKHGtZc8KI93kIvtwhjNIn_cHjX_y8` |
| Ms. Anderson | `8639260504:AAHjfCq65Yh7WE7cp7JV0LmhU-O0AXecP5A` |
| Octavia | `8560490088:AAFeNyyXov_S8feA4QJd1wlT4cgf-KbvIjw` |
| Mitch | `8639735401:AAEh0K_mdIjbfpEKyhrGom3EOUPafl7QWeQ` |
| Malcom | `8697606189:AAGZhy35al39-ju3PQVWra_CEbQwsPleoWo` |

## Webhook Setup Commands

Run these to configure Telegram webhooks for all agents:

```bash
# Jed (Manager)
curl -X POST "https://api.telegram.org/bot8437636581:AAFPG81Y5LCR5cQ9ESdkvnhKYRZ9LDjbN3E/setWebhook?url=https://jed-the-manager-production.up.railway.app/telegram"

# Ruth (Coder)
curl -X POST "https://api.telegram.org/bot8637717794:AAHjVxKHGtZc8KI93kIvtwhjNIn_cHjX_y8/setWebhook?url=https://hermes-agent-production-4fd7.up.railway.app/telegram"

# Ms. Anderson (Editor)
curl -X POST "https://api.telegram.org/bot8639260504:AAHjfCq65Yh7WE7cp7JV0LmhU-O0AXecP5A/setWebhook?url=https://hermes-agent-production-6fc9.up.railway.app/telegram"

# Octavia (Admin)
curl -X POST "https://api.telegram.org/bot8560490088:AAFeNyyXov_S8feA4QJd1wlT4cgf-KbvIjw/setWebhook?url=https://hermes-agent-production-8b69.up.railway.app/telegram"

# Mitch (Sales/Marketing)
curl -X POST "https://api.telegram.org/bot8639735401:AAEh0K_mdIjbfpEKyhrGom3EOUPafl7QWeQ/setWebhook?url=https://hermes-agent-production-51e6.up.railway.app/telegram"

# Malcom (Social Media)
curl -X POST "https://api.telegram.org/bot8697606189:AAGZhy35al39-ju3PQVWra_CEbQwsPleoWo/setWebhook?url=https://hermes-agent-production-5b79.up.railway.app/telegram"
```

## Verify Webhooks

```bash
# Check all webhook statuses
echo "=== Jed ===" && curl -s "https://api.telegram.org/bot8437636581:AAFPG81Y5LCR5cQ9ESdkvnhKYRZ9LDjbN3E/getWebhookInfo" | grep -o '"url":"[^"]*"'
echo "=== Ruth ===" && curl -s "https://api.telegram.org/bot8637717794:AAHjVxKHGtZc8KI93kIvtwhjNIn_cHjX_y8/getWebhookInfo" | grep -o '"url":"[^"]*"'
echo "=== Ms. Anderson ===" && curl -s "https://api.telegram.org/bot8639260504:AAHjfCq65Yh7WE7cp7JV0LmhU-O0AXecP5A/getWebhookInfo" | grep -o '"url":"[^"]*"'
echo "=== Octavia ===" && curl -s "https://api.telegram.org/bot8560490088:AAFeNyyXov_S8feA4QJd1wlT4cgf-KbvIjw/getWebhookInfo" | grep -o '"url":"[^"]*"'
echo "=== Mitch ===" && curl -s "https://api.telegram.org/bot8639735401:AAEh0K_mdIjbfpEKyhrGom3EOUPafl7QWeQ/getWebhookInfo" | grep -o '"url":"[^"]*"'
echo "=== Malcom ===" && curl -s "https://api.telegram.org/bot8697606189:AAGZhy35al39-ju3PQVWra_CEbQwsPleoWo/getWebhookInfo" | grep -o '"url":"[^"]*"'
```

## Internal Network Communication

All agents can communicate with each other using internal Railway URLs:

```python
# Example: Dashboard calling Jed (Manager)
JED_INTERNAL = "http://jed---the-manager.railway.internal:8080"

# Example: Ruth calling Ms. Anderson for content review
MS_ANDERSON_INTERNAL = "http://hermes-agent-14cf.railway.internal:8080"

# Example: Any agent calling Mitch for marketing coordination
MITCH_INTERNAL = "http://hermes-agent-7a4a.railway.internal:8080"
```

## Environment Variables (Per Service)

```bash
# Common for ALL agents
HERMES_HOME=/hermes
PYTHONUNBUFFERED=1
OLLAMA_API_KEY=<your-ollama-key>
TELEGRAM_WEBHOOK_PORT=8080
TELEGRAM_ALLOWED_USERS=8502906149
TELEGRAM_ALLOWED_CHATS=-1003936982744
TELEGRAM_HOME_CHANNEL=-1003936982744

# Agent-specific (set per service)
TELEGRAM_BOT_TOKEN=<token-for-this-agent>
TELEGRAM_WEBHOOK_URL=https://<external-url>/telegram
```

## Agent Communication Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Railway Internal Network                  │
│                                                              │
│  ┌──────────────┐                                           │
│  │    Jed       │ ◄── Manager/Orchestrator                  │
│  │  (Manager)   │     Receives tasks, delegates to workers  │
│  └──────┬───────┘                                           │
│         │                                                    │
│         ├─────────────────────────────────────────┐          │
│         │                   │                     │          │
│         ▼                   ▼                     ▼          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │    Ruth      │  │ Ms. Anderson │  │   Octavia    │       │
│  │   (Coder)    │  │   (Editor)   │  │   (Admin)    │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐                         │
│  │    Mitch     │  │   Malcom     │                         │
│  │ (Marketing)  │  │(Social Media)│                         │
│  └──────────────┘  └──────────────┘                         │
│                                                              │
│  ┌──────────────────────────────────────────────┐           │
│  │           Flask Dashboard                    │           │
│  │  (Kanban board, chat, agent status)          │           │
│  └──────────────────────────────────────────────┘           │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │   Telegram      │
                    │   (Webhooks)    │
                    └─────────────────┘
```

## Troubleshooting

**Webhook not working:**
```bash
# Check webhook is set correctly
curl "https://api.telegram.org/bot<TOKEN>/getWebhookInfo"
# Should show: "url": "https://<your-railway-url>/telegram"
```

**Gateway not starting:**
- Check Railway logs for errors
- Verify TELEGRAM_BOT_TOKEN is correct
- Ensure OLLAMA_API_KEY is set
- Check TELEGRAM_WEBHOOK_URL matches Railway's assigned URL

**Agents can't communicate internally:**
- Verify internal URLs are correct (check Railway dashboard)
- Ensure all services are in the same Railway project
- Test connectivity: `curl http://<internal-url>:8080/health`

**Polling conflicts (should not happen with webhooks):**
- Make sure TELEGRAM_WEBHOOK_URL is set in environment
- Delete old webhook: `curl -X POST "https://api.telegram.org/bot<TOKEN>/deleteWebhook"`
- Re-set webhook with correct Railway URL
