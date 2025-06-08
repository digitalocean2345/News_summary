# Database Persistence Fix for Digital Ocean

## 🚨 Problem

Your Digital Ocean server was losing database data after service restarts because:

1. **Wrong Database Path**: The database was being created in temporary locations like `/tmp/news.db`
2. **Missing Environment Variables**: The service wasn't properly configured with `ENVIRONMENT=production`
3. **Incorrect Permissions**: Database files didn't have proper permissions for the service user
4. **Service Configuration**: The systemd service had `PrivateTmp=true` which isolated the filesystem

## ✅ Solution

The fix involves several components:

### 1. Updated Database Configuration
- **File**: `app/database.py`
- **Change**: Database now uses persistent path `/var/www/news_summary/news_aggregator.db`
- **Benefit**: Data persists across restarts

### 2. Fixed Service Configuration  
- **File**: `digital_ocean_service.service`
- **Changes**: 
  - Added `ENVIRONMENT=production`
  - Set `PrivateTmp=false`
  - Added proper directory setup
- **Benefit**: Service runs with correct environment

### 3. Database Setup Script
- **File**: `setup_production_db.py`
- **Purpose**: Ensures proper database initialization and migration
- **Features**: 
  - Creates database directory
  - Migrates existing data
  - Sets proper permissions
  - Verifies database integrity

### 4. Deployment Fix Script
- **File**: `fix_digitalocean_persistence.sh`
- **Purpose**: One-command fix for the entire issue
- **Features**:
  - Updates service configuration
  - Migrates database to persistent location
  - Sets proper permissions
  - Creates deployment and health check scripts

## 🚀 How to Apply the Fix

### Step 1: Upload Files to Your Server

From your local machine, upload the fix files to your Digital Ocean droplet:

```bash
# Upload the files to your droplet
scp app/database.py root@YOUR_DROPLET_IP:/var/www/news_summary/app/
scp setup_production_db.py root@YOUR_DROPLET_IP:/var/www/news_summary/
scp fix_digitalocean_persistence.sh root@YOUR_DROPLET_IP:/var/www/news_summary/
```

### Step 2: SSH into Your Server

```bash
ssh root@YOUR_DROPLET_IP
```

### Step 3: Switch to Deployer User

```bash
sudo su - deployer
cd /var/www/news_summary
```

### Step 4: Make Scripts Executable

```bash
chmod +x setup_production_db.py
chmod +x fix_digitalocean_persistence.sh
```

### Step 5: Run the Fix Script

```bash
./fix_digitalocean_persistence.sh
```

This script will:
- ✅ Stop the service
- ✅ Backup existing database
- ✅ Update service configuration
- ✅ Setup persistent database location
- ✅ Migrate existing data
- ✅ Set proper permissions
- ✅ Restart the service
- ✅ Verify everything is working

## 🔍 Verification

After running the fix, you can verify everything is working:

### Check Database Health
```bash
./check_db_health.sh
```

### Check Service Status
```bash
sudo systemctl status news-summary.service
```

### Test Your Application
Visit `http://YOUR_DROPLET_IP` and verify your data is showing.

### Test Persistence
Restart the service and verify data persists:
```bash
sudo systemctl restart news-summary.service
# Wait a few seconds, then check your application again
```

## 📁 File Locations After Fix

- **Database**: `/var/www/news_summary/news_aggregator.db`
- **Application**: `/var/www/news_summary/`
- **Service Config**: `/etc/systemd/system/news-summary.service`
- **Logs**: `sudo journalctl -u news-summary.service -f`

## 🛠️ Ongoing Management

### Deploy Updates
```bash
cd /var/www/news_summary
./deploy.sh
```

### Check Database Health
```bash
./check_db_health.sh
```

### Manual Database Backup
```bash
./backup_db.sh
```

### View Service Logs
```bash
sudo journalctl -u news-summary.service -f
```

## 🎯 What This Fix Accomplishes

1. **✅ Persistent Storage**: Database is now stored in a permanent location
2. **✅ Proper Permissions**: Service can read/write to database
3. **✅ Environment Configuration**: Production environment is properly set
4. **✅ Automatic Migration**: Existing data is preserved and migrated
5. **✅ Service Reliability**: Service starts correctly with database access
6. **✅ Easy Management**: Scripts for deployment, health checks, and backups

## 🚨 Troubleshooting

### If the Service Won't Start
```bash
sudo journalctl -u news-summary.service -n 50
```

### If Database is Empty
1. Check if migration occurred: `ls -la /var/www/news_summary/news_aggregator*`
2. Run setup again: `python setup_production_db.py`
3. Check permissions: `ls -la /var/www/news_summary/news_aggregator.db`

### If UI Shows No Data
1. Run health check: `./check_db_health.sh`
2. Check service logs: `sudo journalctl -u news-summary.service -f`
3. Verify database path in app: Check that `ENVIRONMENT=production` is set

## 📞 Support

If you encounter any issues after applying this fix, check:

1. Service status: `sudo systemctl status news-summary.service`
2. Database health: `./check_db_health.sh`
3. Application logs: `sudo journalctl -u news-summary.service -f`
4. File permissions: `ls -la /var/www/news_summary/`

Your database will now persist across all service restarts! 🎉 