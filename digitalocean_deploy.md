# DigitalOcean Droplet Deployment Guide

## Prerequisites
1. DigitalOcean account
2. Domain name (optional but recommended)
3. Local SSH key pair

## Step 1: Create DigitalOcean Droplet

1. **Create Droplet:**
   - Choose Ubuntu 22.04 LTS
   - Choose size: Basic $12/month (2GB RAM, 1 vCPU, 50GB SSD) or higher
   - Choose datacenter region closest to your users
   - Add SSH key for authentication
   - Enable backups (recommended)

2. **Initial Server Setup:**
   ```bash
   ssh root@your_droplet_ip
   
   # Update system
   apt update && apt upgrade -y
   
   # Create new user
   adduser deployer
   usermod -aG sudo deployer
   
   # Copy SSH keys to new user
   rsync --archive --chown=deployer:deployer ~/.ssh /home/deployer
   ```

## Step 2: Install Required Software

```bash
# Switch to deployer user
su - deployer

# Install Python 3.11 and pip
sudo apt install -y python3.11 python3.11-venv python3-pip git nginx certbot python3-certbot-nginx

# Install Node.js (for any frontend build needs)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Create application directory
sudo mkdir -p /var/www/news_summary
sudo chown deployer:deployer /var/www/news_summary
```

## Step 3: Deploy Application

```bash
cd /var/www/news_summary

# Clone your repository (replace with your actual repo URL)
git clone https://github.com/yourusername/News_summary.git .

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Step 4: Environment Configuration

Create environment file:
```bash
nano .env
```

Add the following content:
```env
DATABASE_URL=sqlite:///./news_aggregator.db
ENVIRONMENT=production
PORT=8000
```

## Step 5: Database Setup

```bash
# Activate virtual environment
source venv/bin/activate

# Initialize database
python -c "
from app.database import engine
from app.models import models
models.Base.metadata.create_all(bind=engine)
print('✅ Database tables created successfully')
"

# Set proper permissions for database
chmod 664 news.db
sudo chown deployer:www-data news.db
```

## Step 6: Create Systemd Service

```bash
sudo nano /etc/systemd/system/news-summary.service
```

Add the following content:
```ini
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
```

## Step 7: Configure Nginx

```bash
sudo nano /etc/nginx/sites-available/news-summary
```

Add the following content:
```nginx
server {
    listen 80;
    server_name your_domain.com www.your_domain.com;  # Replace with your domain

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
```

Enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/news-summary /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## Step 8: SSL Certificate (Optional but Recommended)

If you have a domain name:
```bash
sudo certbot --nginx -d your_domain.com -d www.your_domain.com
```

## Step 9: Start Services

```bash
# Enable and start the application service
sudo systemctl enable news-summary.service
sudo systemctl start news-summary.service

# Check status
sudo systemctl status news-summary.service

# Enable nginx
sudo systemctl enable nginx
```

## Step 10: Setup Firewall

```bash
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

## Step 11: Database Backup Script

Create a backup script:
```bash
nano /var/www/news_summary/backup_db.sh
```

Add the following content:
```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/var/www/news_summary/backups"
mkdir -p $BACKUP_DIR

# Backup SQLite database
cp /var/www/news_summary/news_aggregator.db $BACKUP_DIR/news_aggregator_$DATE.db

# Keep only last 7 days of backups
find $BACKUP_DIR -name "news_aggregator_*.db" -mtime +7 -delete

echo "Database backed up to $BACKUP_DIR/news_aggregator_$DATE.db"
```

Make it executable and add to crontab:
```bash
chmod +x /var/www/news_summary/backup_db.sh

# Add to crontab (backup daily at 2 AM)
crontab -e
```

Add this line:
```
0 2 * * * /var/www/news_summary/backup_db.sh
```

## Step 12: Monitoring and Logs

```bash
# View application logs
sudo journalctl -u news-summary.service -f

# View nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Check application status
systemctl status news-summary.service
```

## Step 13: Setup Automated News Scraping

Create automated scraping to run at 6 AM and 6 PM daily:

```bash
# Create logs directory
mkdir -p /var/www/news_summary/logs
chmod 755 /var/www/news_summary/logs

# Make the scraper script executable
chmod +x /var/www/news_summary/automated_scraper.py

# Create a wrapper script for cron (needed for environment variables)
cat > /var/www/news_summary/cron_scraper.sh << 'EOF'
#!/bin/bash
# Cron wrapper for automated scraper

# Set environment variables
export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
export PYTHONPATH="/var/www/news_summary:/var/www/news_summary/app"

# Change to project directory
cd /var/www/news_summary

# Activate virtual environment
source venv/bin/activate

# Run the scraper
python3 automated_scraper.py

# Log completion
echo "$(date): Automated scraping job completed" >> /var/www/news_summary/logs/cron.log
EOF

# Make the cron wrapper executable
chmod +x /var/www/news_summary/cron_scraper.sh
```

Add cron jobs for automated scraping:
```bash
# Add cron jobs for 6 AM and 6 PM daily
(crontab -l 2>/dev/null; echo "# Automated News Scraping - 6 AM daily") | crontab -
(crontab -l 2>/dev/null; echo "0 6 * * * /var/www/news_summary/cron_scraper.sh >> /var/www/news_summary/logs/cron.log 2>&1") | crontab -

(crontab -l 2>/dev/null; echo "# Automated News Scraping - 6 PM daily") | crontab -
(crontab -l 2>/dev/null; echo "0 18 * * * /var/www/news_summary/cron_scraper.sh >> /var/www/news_summary/logs/cron.log 2>&1") | crontab -

# Verify cron jobs were added
crontab -l
```

Test the automated scraper manually:
```bash
cd /var/www/news_summary
./cron_scraper.sh
```

Monitor scraping logs:
```bash
# View scraper logs
tail -f /var/www/news_summary/logs/scraper.log

# View cron execution logs
tail -f /var/www/news_summary/logs/cron.log
```

## Step 14: Monitoring and Logs

```bash
# View application logs
sudo journalctl -u news-summary.service -f

# View nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Check application status
systemctl status news-summary.service
```

## Step 15: Deployment Script for Updates

Create an update script:
```bash
nano /var/www/news_summary/deploy.sh
```

Add the following content:
```bash
#!/bin/bash
cd /var/www/news_summary

# Backup current database
./backup_db.sh

# Pull latest changes
git pull origin main

# Activate virtual environment
source venv/bin/activate

# Update dependencies
pip install -r requirements.txt

# Restart the service
sudo systemctl restart news-summary.service

echo "Deployment completed!"
```

Make it executable:
```bash
chmod +x /var/www/news_summary/deploy.sh
```

## Step 16: Testing Your Deployment

1. **Basic Health Check:**
   ```bash
   curl http://your_domain.com/health
   ```

2. **API Test:**
   ```bash
   curl http://your_domain.com/api/debug/all
   ```

3. **Web Interface:**
   Visit `http://your_domain.com` in your browser

4. **Test Automated Scraping:**
   ```bash
   cd /var/www/news_summary
   ./cron_scraper.sh
   ```

## Step 17: Troubleshooting

1. **Check service status:**
   ```bash
   sudo systemctl status news-summary.service
   ```

2. **Check logs:**
   ```bash
   sudo journalctl -u news-summary.service -n 50
   ```

3. **Check nginx configuration:**
   ```bash
   sudo nginx -t
   ```

4. **Check database permissions:**
   ```bash
   ls -la news_aggregator.db
   ```

5. **Check cron jobs:**
   ```bash
   crontab -l
   ```

6. **Check scraping logs:**
   ```bash
   tail -f /var/www/news_summary/logs/scraper.log
   tail -f /var/www/news_summary/logs/cron.log
   ```

## Step 18: Security Considerations

1. **Regular Updates:**
   ```bash
   sudo apt update && sudo apt upgrade
   ```

2. **Monitor logs regularly**
3. **Use strong SSH keys**
4. **Consider fail2ban for SSH protection**
5. **Regular database backups**

## Step 19: Performance Optimization

1. **For high traffic, consider:**
   - Increasing gunicorn workers
   - Adding Redis for caching
   - Using a CDN for static files
   - Database connection pooling

2. **Monitor resource usage:**
   ```bash
   htop
   df -h
   free -h
   ```

Your application will be accessible at:
- HTTP: `http://your_domain.com` or `http://your_droplet_ip`
- HTTPS: `https://your_domain.com` (if SSL configured)

The SQLite database will persist on the droplet's filesystem, solving the persistence issue you had with GCP.

**Automated News Scraping:**
- Runs automatically at 6:00 AM and 6:00 PM daily (UTC)
- Scrapes from all 8 news sources (People's Daily, The Paper, State Council, NBS, Taiwan Affairs, MND, Guancha, Global Times)
- Automatically translates Chinese content to English
- Logs all activity to `/var/www/news_summary/logs/scraper.log`
- Prevents duplicate articles from being added to the database 