#!/bin/bash

# Script to add Microsoft Translator API key to DigitalOcean droplet
# Run this script on your DigitalOcean droplet as root

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    print_error "Please run this script as root (sudo)"
    exit 1
fi

# Get API key from user input
echo "🔑 Microsoft Translator API Key Setup"
echo "====================================="
echo ""
echo "You need a Microsoft Translator API key for translation functionality."
echo "Get your API key from: https://portal.azure.com/"
echo "Navigate to: Cognitive Services > Translator > Keys and Endpoint"
echo ""
echo -n "Enter your Microsoft Translator API Key: "
read -s MS_TRANSLATOR_KEY
echo ""

if [ -z "$MS_TRANSLATOR_KEY" ]; then
    print_error "API key cannot be empty!"
    exit 1
fi

# Optional: Get the region/location
echo ""
echo -n "Enter your Microsoft Translator Location/Region (default: global): "
read MS_TRANSLATOR_LOCATION
MS_TRANSLATOR_LOCATION=${MS_TRANSLATOR_LOCATION:-global}

print_status "Setting up Microsoft Translator API key..."

# Update the systemd service file to include environment variables
print_status "Updating systemd service configuration..."
cat > /etc/systemd/system/news-summary.service << EOF
[Unit]
Description=News Summary FastAPI Application
After=network.target

[Service]
Type=notify
User=deployer
Group=www-data
WorkingDirectory=/var/www/news_summary
Environment="PATH=/var/www/news_summary/venv/bin"
Environment="MS_TRANSLATOR_KEY=$MS_TRANSLATOR_KEY"
Environment="MS_TRANSLATOR_LOCATION=$MS_TRANSLATOR_LOCATION"
Environment="DATABASE_URL=sqlite:///./news_aggregator.db"
Environment="ENVIRONMENT=production"
Environment="PORT=8000"
ExecStart=/var/www/news_summary/venv/bin/gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 127.0.0.1:8000
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Update the .env file
print_status "Updating .env file..."
cat > /var/www/news_summary/.env << EOF
DATABASE_URL=sqlite:///./news_aggregator.db
ENVIRONMENT=production
PORT=8000
MS_TRANSLATOR_KEY=$MS_TRANSLATOR_KEY
MS_TRANSLATOR_LOCATION=$MS_TRANSLATOR_LOCATION
EOF

# Set proper permissions on .env file
chown deployer:deployer /var/www/news_summary/.env
chmod 600 /var/www/news_summary/.env

# Reload systemd and restart the service
print_status "Reloading systemd configuration..."
systemctl daemon-reload

print_status "Restarting news-summary service..."
systemctl restart news-summary.service

# Wait a moment for the service to start
sleep 3

# Check service status
print_status "Checking service status..."
if systemctl is-active --quiet news-summary.service; then
    print_status "✅ Service is running successfully!"
else
    print_warning "⚠️ Service may have issues. Checking logs..."
    journalctl -u news-summary.service --no-pager -n 10
fi

echo ""
echo "🎉 Microsoft Translator API Key Setup Complete!"
echo ""
echo "📊 To verify translation is working:"
echo "   curl http://localhost:8000/api/test-translation"
echo ""
echo "📋 Useful commands:"
echo "   - Check service status: systemctl status news-summary.service"
echo "   - View logs: journalctl -u news-summary.service -f"
echo "   - Restart service: systemctl restart news-summary.service"
echo ""
print_status "Translation functionality should now be active!" 