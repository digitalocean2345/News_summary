#!/bin/bash

# Fix DigitalOcean Database Persistence Issue
# Run this script on your DigitalOcean droplet to resolve database persistence

set -e

echo "🔧 Fixing DigitalOcean Database Persistence Issue..."

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

# Check if running as deployer user
if [ "$USER" != "deployer" ]; then
    print_error "Please run this script as the 'deployer' user"
    print_status "Switch to deployer user: sudo su - deployer"
    exit 1
fi

# Navigate to application directory
cd /var/www/news_summary

print_status "Stopping the news-summary service..."
sudo systemctl stop news-summary.service

# Create backup of current database if it exists
if [ -f "./news_aggregator.db" ]; then
    print_status "Creating backup of current database..."
    cp news_aggregator.db "news_aggregator_backup_$(date +%Y%m%d_%H%M%S).db"
fi

# Update systemd service configuration
print_status "Updating systemd service configuration..."
sudo tee /etc/systemd/system/news-summary.service > /dev/null << 'EOF'
[Unit]
Description=News Summary FastAPI Application
After=network.target

[Service]
Type=notify
User=deployer
Group=www-data
WorkingDirectory=/var/www/news_summary
Environment="PATH=/var/www/news_summary/venv/bin"
Environment="ENVIRONMENT=production"
Environment="PYTHONPATH=/var/www/news_summary"
ExecStartPre=/bin/bash -c 'mkdir -p /var/www/news_summary && chown deployer:www-data /var/www/news_summary'
ExecStart=/var/www/news_summary/venv/bin/gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 127.0.0.1:8000
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=false
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd configuration
print_status "Reloading systemd configuration..."
sudo systemctl daemon-reload

# Setup database directory with proper permissions
print_status "Setting up database directory and permissions..."
sudo mkdir -p /var/www/news_summary
sudo chown -R deployer:www-data /var/www/news_summary
sudo chmod -R 775 /var/www/news_summary

# Activate virtual environment and setup database
print_status "Activating virtual environment..."
source venv/bin/activate

# Install/upgrade dependencies
print_status "Installing dependencies..."
pip install -r requirements.txt

# Run database setup script
print_status "Setting up production database..."
python setup_production_db.py

# Set final database permissions
if [ -f "/var/www/news_summary/news_aggregator.db" ]; then
    print_status "Setting final database permissions..."
    sudo chown deployer:www-data /var/www/news_summary/news_aggregator.db
    sudo chmod 664 /var/www/news_summary/news_aggregator.db
fi

# Create enhanced deployment script
print_status "Creating enhanced deployment script..."
cat > /var/www/news_summary/deploy.sh << 'DEPLOY_EOF'
#!/bin/bash
cd /var/www/news_summary

echo "🚀 Starting deployment..."

# Backup current database
if [ -f "./backup_db.sh" ]; then
    ./backup_db.sh
fi

# Pull latest changes  
echo "📥 Pulling latest changes..."
git pull origin main

# Activate virtual environment
source venv/bin/activate

# Update dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Ensure database setup
echo "🔧 Ensuring database setup..."
python setup_production_db.py

# Set proper permissions
sudo chown -R deployer:www-data /var/www/news_summary
sudo chmod 664 /var/www/news_summary/news_aggregator.db 2>/dev/null || true

# Restart the service
echo "🔄 Restarting service..."
sudo systemctl restart news-summary.service

# Check service status
echo "📊 Checking service status..."
sudo systemctl status news-summary.service --no-pager -l

echo "✅ Deployment completed!"
DEPLOY_EOF

chmod +x /var/www/news_summary/deploy.sh

# Create database health check script
print_status "Creating database health check script..."
cat > /var/www/news_summary/check_db_health.sh << 'HEALTH_EOF'
#!/bin/bash

echo "🔍 Database Health Check"
echo "======================"

DB_PATH="/var/www/news_summary/news_aggregator.db"

if [ -f "$DB_PATH" ]; then
    echo "✅ Database file exists: $DB_PATH"
    echo "📊 File size: $(du -h $DB_PATH | cut -f1)"
    echo "🕒 Last modified: $(stat -c %y $DB_PATH)"
    echo "👤 Owner: $(stat -c %U:%G $DB_PATH)"
    echo "🔒 Permissions: $(stat -c %a $DB_PATH)"
    
    # Test database connection
    cd /var/www/news_summary
    source venv/bin/activate
    python -c "
import os
os.environ['ENVIRONMENT'] = 'production'
from app.database import SessionLocal
try:
    db = SessionLocal()
    result = db.execute('SELECT COUNT(*) FROM articles').scalar()
    print(f'📈 Articles count: {result}')
    db.close()
    print('✅ Database connection successful')
except Exception as e:
    print(f'❌ Database connection failed: {e}')
"
else
    echo "❌ Database file not found: $DB_PATH"
fi

echo ""
echo "🔧 Service Status:"
sudo systemctl status news-summary.service --no-pager -l
HEALTH_EOF

chmod +x /var/www/news_summary/check_db_health.sh

# Start the service
print_status "Starting the news-summary service..."
sudo systemctl start news-summary.service
sudo systemctl enable news-summary.service

# Wait a moment for service to start
sleep 3

# Check service status
print_status "Checking service status..."
sudo systemctl status news-summary.service --no-pager -l

# Run health check
print_status "Running database health check..."
./check_db_health.sh

print_status "✅ Database persistence fix completed!"
print_status ""
print_status "🎯 Summary of changes:"
print_status "  • Updated database path to persistent location: /var/www/news_summary/news_aggregator.db"
print_status "  • Fixed systemd service configuration with proper environment variables"
print_status "  • Set correct file permissions for database access"
print_status "  • Created enhanced deployment and health check scripts"
print_status ""
print_status "💡 Your database will now persist across service restarts!"
print_status "🔧 Use './check_db_health.sh' to monitor database status"
print_status "🚀 Use './deploy.sh' for future deployments" 