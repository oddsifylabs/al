#!/bin/bash
# Webhook Setup Script for AL Workforce
# Run this AFTER deploying each service to Railway

# Bot tokens
declare -A BOTS=(
    ["jed"]="8437636581:AAFPG81Y5LCR5cQ9ESdkvnhKYRZ9LDjbN3E"
    ["ruth"]="8637717794:AAHjVxKHGtZc8KI93kIvtwhjNIn_cHjX_y8"
    ["ms_anderson"]="8639260504:AAHjfCq65Yh7WE7cp7JV0LmhU-O0AXecP5A"
    ["octavia"]="8560490088:AAFeNyyXov_S8feA4QJd1wlT4cgf-KbvIjw"
    ["mitch"]="8639735401:AAEh0K_mdIjbfpEKyhrGom3EOUPafl7QWeQ"
    ["malcom"]="8697606189:AAGZhy35al39-ju3PQVWra_CEbQwsPleoWo"
)

# Railway URLs (UPDATE THESE after deployment)
declare -A URLS=(
    ["jed"]="https://al-jed-production.up.railway.app"
    ["ruth"]="https://al-ruth-production.up.railway.app"
    ["ms_anderson"]="https://al-anderson-production.up.railway.app"
    ["octavia"]="https://al-octavia-production.up.railway.app"
    ["mitch"]="https://al-mitch-production.up.railway.app"
    ["malcom"]="https://al-malcom-production.up.railway.app"
)

echo "🔧 Setting up Telegram webhooks for AL Workforce..."
echo ""

for agent in "${!BOTS[@]}"; do
    TOKEN="${BOTS[$agent]}"
    RAILWAY_URL="${URLS[$agent]}"
    WEBHOOK_URL="${RAILWAY_URL}/telegram"
    
    echo "📍 $agent → $WEBHOOK_URL"
    
    RESPONSE=$(curl -s -X POST "https://api.telegram.org/bot$TOKEN/setWebhook?url=$WEBHOOK_URL")
    
    if echo "$RESPONSE" | grep -q '"ok":true'; then
        echo "   ✅ Webhook set successfully"
    else
        echo "   ❌ Failed: $RESPONSE"
    fi
    echo ""
done

echo "🔍 Verifying all webhooks..."
echo ""

for agent in "${!BOTS[@]}"; do
    TOKEN="${BOTS[$agent]}"
    echo "📍 $agent:"
    curl -s "https://api.telegram.org/bot$TOKEN/getWebhookInfo" | grep -o '"url":"[^"]*"' || echo "   No webhook set"
    echo ""
done

echo "✅ Webhook setup complete!"
