#!/bin/bash
# Setup Automated News Scraping on DigitalOcean Server
# This script sets up cron jobs to run news scraping at 6 AM and 6 PM daily

echo "🤖 Setting up automated news scraping..."
echo "=============================================="

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

# Add cron jobs for 6 AM and 6 PM daily
echo "📅 Setting up cron jobs..."

# Create cron entries
(crontab -l 2>/dev/null; echo "# Automated News Scraping - 6 AM daily") | crontab -
(crontab -l 2>/dev/null; echo "0 6 * * * /var/www/news_summary/cron_scraper.sh >> /var/www/news_summary/logs/cron.log 2>&1") | crontab -

(crontab -l 2>/dev/null; echo "# Automated News Scraping - 6 PM daily") | crontab -
(crontab -l 2>/dev/null; echo "0 18 * * * /var/www/news_summary/cron_scraper.sh >> /var/www/news_summary/logs/cron.log 2>&1") | crontab -

echo "✅ Cron jobs added successfully!"
echo ""
echo "📋 Current cron jobs:"
crontab -l

echo ""
echo "📊 Automation Setup Complete!"
echo "=============================================="
echo "🕕 Morning scraping: 6:00 AM daily (UTC)"
echo "🕕 Evening scraping: 6:00 PM daily (UTC)"
echo "📝 Logs location: /var/www/news_summary/logs/"
echo "🗂  Scraper log: /var/www/news_summary/logs/scraper.log"
echo "🗂  Cron log: /var/www/news_summary/logs/cron.log"
echo ""
echo "🧪 To test manually, run:"
echo "   cd /var/www/news_summary && ./cron_scraper.sh"
echo ""
echo "🔍 To check cron jobs:"
echo "   crontab -l"
echo ""
echo "📋 To view logs:"
echo "   tail -f /var/www/news_summary/logs/scraper.log"
echo "   tail -f /var/www/news_summary/logs/cron.log" 