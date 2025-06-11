#!/bin/bash
# Update Automated News Scraping Cron Timings
# This script changes the cron jobs from 6 AM/6 PM to 1 AM/1 PM daily

echo "🕐 Updating automated news scraping cron timings..."
echo "=============================================="
echo "Changing from: 6 AM and 6 PM"
echo "Changing to: 1 AM and 1 PM"
echo ""

# Show current cron jobs
echo "📋 Current cron jobs:"
crontab -l | grep -A1 -B1 "Automated News Scraping" || echo "No existing automated scraping cron jobs found"
echo ""

# Remove existing automated scraping cron jobs
echo "🗑  Removing existing automated scraping cron jobs..."
crontab -l | grep -v "Automated News Scraping" | grep -v "/var/www/news_summary/cron_scraper.sh" | crontab -

# Verify the wrapper script exists and is executable
if [ ! -f "/var/www/news_summary/cron_scraper.sh" ]; then
    echo "⚠️  Wrapper script not found. Creating it..."
    
    # Create logs directory if it doesn't exist
    mkdir -p /var/www/news_summary/logs
    chmod 755 /var/www/news_summary/logs
    
    # Create the wrapper script
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
    echo "✅ Wrapper script created and made executable"
fi

# Add new cron jobs for 1 AM and 1 PM daily
echo "📅 Adding new cron jobs for 1 AM and 1 PM..."

# Add 1 AM job
(crontab -l 2>/dev/null; echo "# Automated News Scraping - 1 AM daily") | crontab -
(crontab -l 2>/dev/null; echo "0 1 * * * /var/www/news_summary/cron_scraper.sh >> /var/www/news_summary/logs/cron.log 2>&1") | crontab -

# Add 1 PM job
(crontab -l 2>/dev/null; echo "# Automated News Scraping - 1 PM daily") | crontab -
(crontab -l 2>/dev/null; echo "0 13 * * * /var/www/news_summary/cron_scraper.sh >> /var/www/news_summary/logs/cron.log 2>&1") | crontab -

echo "✅ New cron jobs added successfully!"
echo ""
echo "📋 Updated cron jobs:"
crontab -l
echo ""
echo "📊 Cron Timing Update Complete!"
echo "=============================================="
echo "🕐 Morning scraping: 1:00 AM daily (UTC)"
echo "🕐 Afternoon scraping: 1:00 PM daily (UTC)"
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
echo ""
echo "⏰ Note: Times are in UTC. Adjust for your local timezone if needed." 