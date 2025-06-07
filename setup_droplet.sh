#!/bin/bash

# DigitalOcean Droplet Setup Script for News Summary App
# Run this script on your Ubuntu 22.04 droplet as root

set -e

echo "🚀 Starting DigitalOcean Droplet Setup for News Summary App"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
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

# Update system
print_status "Updating system packages..."
apt update && apt upgrade -y

# Install required packages
print_status "Installing required packages..."
apt install -y python3.11 python3.11-venv python3-pip git nginx certbot python3-certbot-nginx curl software-properties-common

# Install Node.js (optional, for any frontend builds)
print_status "Installing Node.js..."
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
apt-get install -y nodejs

# Create deployer user
print_status "Creating deployer user..."
if ! id "deployer" &>/dev/null; then
    adduser --disabled-password --gecos "" deployer
    usermod -aG sudo deployer
    print_status "User 'deployer' created successfully"
else
    print_warning "User 'deployer' already exists"
fi

# Setup SSH keys for deployer (copy from root)
if [ -d "/root/.ssh" ]; then
    print_status "Copying SSH keys to deployer user..."
    mkdir -p /home/deployer/.ssh
    cp /root/.ssh/authorized_keys /home/deployer/.ssh/ 2>/dev/null || true
    chown -R deployer:deployer /home/deployer/.ssh
    chmod 700 /home/deployer/.ssh
    chmod 600 /home/deployer/.ssh/authorized_keys 2>/dev/null || true
fi

# Create application directory
print_status "Creating application directory..."
mkdir -p /var/www/news_summary
chown deployer:deployer /var/www/news_summary

# Create systemd service file
print_status "Creating systemd service file..."
cat > /etc/systemd/system/news-summary.service << 'EOF'
[Unit]
Description=News Summary FastAPI Application
After=network.target

[Service]
Type=notify
User=deployer
Group=www-data
WorkingDirectory=/var/www/news_summary
Environment="PATH=/var/www/news_summary/venv/bin"
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

# Create nginx configuration
print_status "Creating nginx configuration..."
cat > /etc/nginx/sites-available/news-summary << 'EOF'
server {
    listen 80;
    server_name _;  # Accept all server names

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }

    # Serve static files directly
    location /static {
        alias /var/www/news_summary/app/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;

    client_max_body_size 10M;
}
EOF

# Enable nginx site
ln -sf /etc/nginx/sites-available/news-summary /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test nginx configuration
nginx -t

# Setup firewall
print_status "Configuring firewall..."
ufw --force enable
ufw allow OpenSSH
ufw allow 'Nginx Full'

# Create backup script
print_status "Creating backup script..."
cat > /var/www/news_summary/backup_db.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/var/www/news_summary/backups"
mkdir -p $BACKUP_DIR

# Backup SQLite database
if [ -f "/var/www/news_summary/news_aggregator.db" ]; then
    cp /var/www/news_summary/news_aggregator.db $BACKUP_DIR/news_aggregator_$DATE.db
    echo "Database backed up to $BACKUP_DIR/news_aggregator_$DATE.db"
else
    echo "Database file not found!"
fi

# Keep only last 7 days of backups
find $BACKUP_DIR -name "news_aggregator_*.db" -mtime +7 -delete
EOF

chown deployer:deployer /var/www/news_summary/backup_db.sh
chmod +x /var/www/news_summary/backup_db.sh

# Create deployment script
print_status "Creating deployment script..."
cat > /var/www/news_summary/deploy.sh << 'EOF'
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

# Restart the service
echo "🔄 Restarting service..."
sudo systemctl restart news-summary.service

echo "✅ Deployment completed!"
echo "🌐 Your app should be available at: http://$(curl -s ifconfig.me)"
EOF

chown deployer:deployer /var/www/news_summary/deploy.sh
chmod +x /var/www/news_summary/deploy.sh

# Create environment file template
print_status "Creating environment file..."
cat > /var/www/news_summary/.env << 'EOF'
DATABASE_URL=sqlite:///./news_aggregator.db
ENVIRONMENT=production
PORT=8000
EOF

chown deployer:deployer /var/www/news_summary/.env

# Enable services
systemctl enable nginx
systemctl restart nginx

print_status "✅ Basic setup completed!"

echo ""
echo "🎉 DigitalOcean Droplet Setup Complete!"
echo ""
echo "Next steps (run as deployer user):"
echo "1. Switch to deployer user: su - deployer"
echo "2. Go to app directory: cd /var/www/news_summary"
echo "3. Clone your repository: git clone <your-repo-url> ."
echo "4. Create virtual environment: python3.11 -m venv venv"
echo "5. Activate venv: source venv/bin/activate"
echo "6. Install dependencies: pip install -r requirements.txt"
echo "7. Initialize database: python -c \"from app.database import engine; from app.models import models; models.Base.metadata.create_all(bind=engine)\""
echo "8. Set database permissions: sudo chown deployer:www-data news_aggregator.db && chmod 664 news_aggregator.db"
echo "9. Start the service: sudo systemctl start news-summary.service"
echo ""
echo "Your app will be available at: http://$(curl -s ifconfig.me)"
echo ""
echo "To check logs: sudo journalctl -u news-summary.service -f"
echo "To check status: sudo systemctl status news-summary.service"
echo ""
print_status "Setup script completed successfully!" 