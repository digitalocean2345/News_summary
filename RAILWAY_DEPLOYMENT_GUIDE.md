# Railway Free Tier Deployment Guide

## 🎯 Overview
Deploy your News Aggregator app to Railway Free Tier + GitHub Actions for **$0/month**

### What you'll get:
- ✅ **Free hosting** (Railway's $5 monthly credit covers your usage)
- ✅ **Free PostgreSQL database** 
- ✅ **Automated scraping** twice daily via GitHub Actions
- ✅ **Professional monitoring** and health checks
- ✅ **Access from any device** via public URL

---

## 🚀 Step-by-Step Deployment

### 1. **Prepare Your Repository**

First, commit all the new files we just created:

```bash
git add .
git commit -m "Add Railway deployment configuration and GitHub Actions"
git push origin main
```

### 2. **Sign Up for Railway**

1. Go to [Railway.app](https://railway.app)
2. Sign up with your GitHub account
3. Verify your account (no credit card required for free tier)

### 3. **Deploy to Railway**

1. **Create New Project**:
   - Click "New Project" 
   - Select "Deploy from GitHub repo"
   - Choose your news aggregator repository

2. **Railway will automatically**:
   - Detect it's a Python app
   - Use the `railway.toml` configuration
   - Install dependencies from `requirements.txt`
   - Start your app with the specified command

3. **Add PostgreSQL Database**:
   - In your Railway project dashboard
   - Click "New" → "Database" → "Add PostgreSQL"
   - Railway automatically connects it to your app

### 4. **Configure Environment Variables**

In Railway project settings → Variables, add:

```env
# Railway provides DATABASE_URL automatically, but add these:
MICROSOFT_TRANSLATOR_KEY=your_translator_api_key
MICROSOFT_TRANSLATOR_REGION=your_region (e.g., eastus)
```

**To get Microsoft Translator API key:**
1. Go to [Azure Portal](https://portal.azure.com)
2. Create "Translator" resource (has free tier)
3. Copy the key and region

### 5. **Initialize Database**

Once deployed, run the database initialization:

1. Go to your Railway project
2. Open the service logs
3. Or run manually via Railway CLI:
   ```bash
   railway run python init_railway_db.py
   ```

### 6. **Set Up GitHub Actions**

1. **Add Repository Secret**:
   - Go to your GitHub repo → Settings → Secrets and Variables → Actions
   - Add new secret:
     - Name: `RAILWAY_APP_URL`
     - Value: `https://your-app-name.up.railway.app` (get from Railway dashboard)

2. **Test the Workflow**:
   - Go to Actions tab in GitHub
   - Click "News Scraper Automation"
   - Click "Run workflow" to test manually

### 7. **Verify Everything Works**

1. **Check your app**: Visit your Railway URL
2. **Test health endpoint**: `https://your-app.up.railway.app/health`
3. **Test scraper**: `https://your-app.up.railway.app/api/news/fetch`
4. **Check GitHub Actions**: Should run automatically at 6 AM & 6 PM UTC

---

## 📊 Configuration Files Explained

### `railway.toml`
```toml
[build]
builder = "nixpacks"          # Railway's automatic builder

[deploy]
startCommand = "uvicorn app.main:app --host 0.0.0.0 --port $PORT"

[env]
PYTHONPATH = "/app"           # Ensures Python can find your modules
```

### `.github/workflows/scraper.yml`
- **Runs twice daily** at 6 AM & 6 PM UTC
- **Calls your scraper API** endpoint
- **Includes health checks** and error handling
- **Provides detailed logging** for debugging

### Updated `app/database.py`
- **Automatically switches** between SQLite (local) and PostgreSQL (Railway)
- **Handles Railway's URL format** (postgres:// → postgresql://)
- **Connection pooling** for production reliability

---

## 🔧 Troubleshooting

### Common Issues:

**1. "Module not found" errors:**
```bash
# In Railway, check if PYTHONPATH is set correctly
# Should be: PYTHONPATH=/app
```

**2. Database connection issues:**
```bash
# Check DATABASE_URL in Railway variables
# Should start with postgresql://
```

**3. GitHub Actions failing:**
```bash
# Check RAILWAY_APP_URL secret is correct
# Format: https://your-app.up.railway.app (no trailing slash)
```

**4. Scraper endpoint timeout:**
```bash
# Increase timeout in GitHub Actions (currently 10 minutes)
# Or optimize your scraper code
```

### Debug Commands:

```bash
# Test locally with Railway database
railway link
railway run python init_railway_db.py

# Check Railway logs
railway logs

# Test endpoints locally
curl http://localhost:8000/health
curl -X POST http://localhost:8000/api/news/fetch
```

---

## 💰 Cost Breakdown

### Railway Free Tier Limits:
- **$5 credit per month** (resets monthly)
- **512MB RAM** 
- **1GB disk space**
- **100GB bandwidth**

### Your App Usage (estimated):
- **Web app running**: ~$3/month
- **PostgreSQL database**: ~$1.50/month  
- **Total**: ~$4.50/month ✅ **Under free limit!**

### GitHub Actions:
- **2,000 minutes/month free**
- **Your usage**: ~300 minutes/month (twice daily scraping)
- **Cost**: $0

---

## 🎯 Next Steps

After deployment:

1. **Monitor your app**: Check Railway dashboard regularly
2. **Optimize scrapers**: Reduce execution time if needed
3. **Set up alerts**: Railway can notify you of issues
4. **Scale if needed**: Upgrade to paid plan if you exceed free limits

---

## 🆘 Need Help?

1. **Railway docs**: [docs.railway.app](https://docs.railway.app)
2. **GitHub Actions docs**: [docs.github.com/actions](https://docs.github.com/en/actions)
3. **Railway Discord**: Very helpful community
4. **Check logs**: Both Railway and GitHub Actions provide detailed logs

Your app should now be running 24/7 on Railway with automated scraping via GitHub Actions, all for **free**! 🎉 