#!/bin/bash
# Al Worker Setup Script
# Usage: ./add-worker.sh <worker-type>

set -e

WORKER_TYPE=$1
HERMES_HOME="${HERMES_HOME:-~/.hermes}"

if [ -z "$WORKER_TYPE" ]; then
    echo "Usage: ./add-worker.sh <worker-type>"
    echo ""
    echo "Available workers:"
    echo "  coder      - Software development"
    echo "  writer     - Content creation"
    echo "  webdev     - Web development"
    echo "  marketing  - Social media & campaigns"
    echo "  support    - Customer service"
    echo "  analyst    - Data analysis"
    echo ""
    exit 1
fi

echo "🔧 Setting up Al worker: $WORKER_TYPE"
echo ""

# Create profile
echo "📦 Creating Hermes profile..."
hermes profile create al-$WORKER_TYPE

# Set personality based on worker type
case $WORKER_TYPE in
    coder)
        PERSONALITY="You are a specialist coder worker in the Al digital workforce. You write clean, tested, well-documented code. You follow best practices and security guidelines. You report progress to the Al Manager."
        TOOLS="terminal,file,code_execution,delegation"
        ;;
    writer)
        PERSONALITY="You are a specialist writer worker in the Al digital workforce. You create clear, engaging content. You research thoroughly and cite sources. You report progress to the Al Manager."
        TOOLS="web,file,search,memory"
        ;;
    webdev)
        PERSONALITY="You are a specialist web developer worker in the Al digital workforce. You build responsive, accessible web applications. You test across browsers and devices. You report progress to the Al Manager."
        TOOLS="terminal,file,browser,code_execution"
        ;;
    marketing)
        PERSONALITY="You are a specialist marketing worker in the Al digital workforce. You create campaigns, manage social media, and analyze performance. You report progress to the Al Manager."
        TOOLS="web,messaging,file,cronjob"
        ;;
    support)
        PERSONALITY="You are a specialist support worker in the Al digital workforce. You help customers, write documentation, and resolve issues. You report progress to the Al Manager."
        TOOLS="web,file,messaging,search"
        ;;
    analyst)
        PERSONALITY="You are a specialist analyst worker in the Al digital workforce. You analyze data, synthesize research, and create reports. You report progress to the Al Manager."
        TOOLS="web,file,search,memory"
        ;;
    *)
        PERSONALITY="You are a specialist worker in the Al digital workforce. You complete tasks efficiently and report progress to the Al Manager."
        TOOLS="terminal,file,web"
        ;;
esac

# Configure personality
echo "⚙️  Setting personality..."
hermes --profile al-$WORKER_TYPE config set agent.personality "$PERSONALITY"

# Enable tools
echo "🛠  Enabling tools..."
for tool in $(echo $TOOLS | tr ',' ' '); do
    hermes --profile al-$WORKER_TYPE tools enable $tool 2>/dev/null || true
done

# Set default model
echo "🤖 Configuring model..."
hermes --profile al-$WORKER_TYPE config set model.default qwen3.5:cloud

# Create Telegram bot placeholder
echo "💬 Creating Telegram bot config..."
cat > $HERMES_HOME/profiles/al-$WORKER_TYPE/telegram-bot.txt << EOF
Telegram Bot Setup for al-$WORKER_TYPE
========================================

1. Open Telegram and search for @BotFather
2. Send: /newbot
3. Name: Al $WORKER_TYPE Worker
4. Username: al_${WORKER_TYPE}_bot (or similar)
5. Copy the bot token
6. Run: hermes --profile al-$WORKER_TYPE config set telegram.bot_token YOUR_TOKEN_HERE
7. Restart: hermes --profile al-$WORKER_TYPE gateway restart

Bot Token: [PASTE HERE]
EOF

echo ""
echo "✅ Worker 'al-$WORKER_TYPE' setup complete!"
echo ""
echo "Next steps:"
echo "  1. Create Telegram bot (see telegram-bot.txt in profile dir)"
echo "  2. Add bot token: hermes --profile al-$WORKER_TYPE config set telegram.bot_token TOKEN"
echo "  3. Start gateway: hermes --profile al-$WORKER_TYPE gateway start"
echo "  4. Test: hermes --profile al-$WORKER_TYPE chat"
echo ""
