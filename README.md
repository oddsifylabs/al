# Al — Autonomous Labor Command Hub

**Your AI-powered digital workforce orchestrator.**

Al is a Manager + Specialist agent system that lets you build, deploy, and scale autonomous AI workers for any task. Decompose complex projects, assign to specialist agents, track progress via Kanban, and get results — all through a unified web dashboard or Telegram.

---

## 🚀 Quick Start

```bash
# Deploy Manager agent
git clone https://github.com/oddsifylabs/al
cd al/al-manager
docker-compose up -d

# Add your first worker
cd ../al-workers
./add-worker.sh coder

# Access dashboard
open http://localhost:8080
```

---

## ✨ Features

### For Managers
- **Natural Language Tasking** — Tell Al what you need in plain English
- **Auto-Decomposition** — Al breaks projects into tasks automatically
- **Kanban Board** — Visual task tracking with dependencies
- **Multi-Agent Orchestration** — Coordinate 10+ workers simultaneously
- **Telegram Integration** — Command your workforce from anywhere

### For Workers
- **Specialist Templates** — Pre-built workers for coding, writing, marketing, etc.
- **Custom Worker SDK** — Build your own specialist agents
- **Auto-Scaling** — Workers run on Railway, Docker, or local machines
- **Memory & Context** — Workers remember past tasks and learn from experience

### For Teams
- **Web Dashboard** — Real-time view of all active tasks
- **Role-Based Access** — Different permissions for different team members
- **Audit Trail** — Full history of all worker actions
- **API Access** — Integrate Al into your existing tools

---

## 🏗 Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Web Dashboard                        │
│  Chat with Al | Kanban Board | Worker Status           │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│              Al Manager (Orchestrator)                  │
│  • Receives tasks                                       │
│  • Decomposes into subtasks                             │
│  • Assigns to workers                                   │
│  • Tracks progress                                      │
│  • Reports results                                      │
└─────────────────────────────────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
        ▼                 ▼                 ▼
   ┌──────────┐     ┌──────────┐     ┌──────────┐
   │  Coder   │     │  Writer  │     │ Marketing│
   │  Worker  │     │  Worker  │     │  Worker  │
   └──────────┘     └──────────┘     └──────────┘
```

---

## 📦 Components

| Component | Description |
|-----------|-------------|
| `al-manager` | The orchestrator agent (Hermes profile) |
| `al-workers` | Specialist worker templates |
| `al-dashboard` | Web GUI (Flask + React) |
| `al-sdk` | Build custom workers |
| `al-deploy` | Deployment configs (Railway, Docker, K8s) |

---

## 🛠 Tech Stack

- **Agent Framework:** Hermes Agent (open-source)
- **LLM Backend:** Ollama (local) or OpenRouter (cloud)
- **Task Queue:** SQLite Kanban (built-in)
- **Web Dashboard:** Flask + React
- **Messaging:** Telegram Bot API
- **Deployment:** Railway, Docker, Kubernetes-ready

---

## 💡 Use Cases

| Use Case | Workers Needed | Example |
|----------|----------------|---------|
| **Content Marketing** | Writer + Social + SEO | Blog → Twitter → LinkedIn pipeline |
| **Software Development** | Coder + Reviewer + Tester | Feature development sprint |
| **E-commerce Ops** | Support + Marketing + Analytics | Customer service + promotions |
| **Research & Analysis** | Researcher + Analyst + Writer | Market research reports |
| **Social Media Management** | Social + Designer + Scheduler | Daily posting across platforms |

---

## 🚀 Deployment

### Railway (Recommended)
```bash
cd al-deploy/railway
railway up
```

### Docker (Local)
```bash
cd al-deploy/docker
docker-compose up -d
```

### Kubernetes (Enterprise)
```bash
kubectl apply -f al-deploy/k8s/
```

---

## 📖 Documentation

- [Architecture Guide](docs/architecture.md)
- [Deployment Guide](docs/deployment.md)
- [Worker SDK](docs/worker-sdk.md)
- [API Reference](docs/api.md)
- [Telegram Setup](docs/telegram.md)

---

## 💰 Pricing (Coming Soon)

| Tier | Workers | Features | Price |
|------|---------|----------|-------|
| **Free** | 3 | Basic Kanban, Telegram only | $0/mo |
| **Pro** | 10 | Web Dashboard, Custom Workers | $29/mo |
| **Team** | 50 | API Access, Priority Support | $99/mo |
| **Enterprise** | Unlimited | White-label, On-prem | Custom |

---

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

## 🌟 Roadmap

- [ ] Multi-tenant support
- [ ] Worker marketplace (buy/sell custom workers)
- [ ] Advanced analytics dashboard
- [ ] Slack/Discord integrations
- [ ] Voice commands (STT/TTS)
- [ ] Mobile app (iOS/Android)

---

**Built with ❤️ by Oddsify Labs**

[Website](https://oddsifylabs.com) | [Twitter](https://twitter.com/OddsifyLabs) | [Discord](https://discord.gg/oddsify)
