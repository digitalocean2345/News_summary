# 🔧 Fix App Engine Deployment Errors

## 🚨 Common Issues and Solutions

### Issue 1: Internal Server Error with Gunicorn

**Problem**: The app deploys but shows "Internal Server Error"
**Cause**: Incorrect entrypoint configuration or missing dependencies

### ✅ **SOLUTION: Updated Files**

I've fixed several issues in your deployment:

1. **Fixed `app.yaml`**: Added proper gunicorn entrypoint
2. **Fixed `requirements.txt`**: Added gunicorn dependency  
3. **Fixed `app/database.py`**: SQLite path for App Engine
4. **Added `startup.py`**: Initialize database and directories
5. **Updated `main.py`**: Include startup script

### 🚀 **Quick Fix Steps**

#### Step 1: Test Simple Version First
```bash
# Deploy simple health check first to test basic deployment
gcloud app deploy app_simple.yaml

# Test if it works
curl https://YOUR_PROJECT_ID.uc.r.appspot.com/health
```

If the simple version works, proceed to Step 2.

#### Step 2: Deploy Full Application
```bash
# Deploy the full application
gcloud app deploy app.yaml

# Initialize database
curl -X POST https://YOUR_PROJECT_ID.uc.r.appspot.com/api/admin/init-database
```

### 🛠️ **Alternative: Debug the Current Deployment**

#### Check Logs
```bash
# View recent logs
gcloud app logs tail -s default

# View specific error logs
gcloud app logs read --severity=ERROR
```

#### Common Error Fixes

**Error**: "ModuleNotFoundError"
**Fix**: Ensure all imports are correct and dependencies are in requirements.txt

**Error**: "Database connection failed"  
**Fix**: The updated database.py should fix SQLite path issues

**Error**: "Template directory not found"
**Fix**: The startup.py script now creates necessary directories

### 📋 **Files That Were Updated**

#### 1. `app.yaml` (Main configuration)
```yaml
runtime: python311
entrypoint: gunicorn -b :$PORT main:app
env_variables:
  ENVIRONMENT: production
# ... rest of config
```

#### 2. `requirements.txt` (Added gunicorn)
```
fastapi[all]>=0.104.0
uvicorn[standard]>=0.24.0
gunicorn>=21.2.0  # <-- Added this
# ... rest of dependencies
```

#### 3. `app/database.py` (Fixed SQLite path)
```python
if not DATABASE_URL:
    if os.getenv('ENVIRONMENT') == 'production':
        DATABASE_URL = "sqlite:////tmp/news.db"  # <-- Fixed path
    else:
        DATABASE_URL = "sqlite:///./news.db"
```

### 🔍 **Debugging Steps**

1. **Check if Google Cloud SDK is working**:
   ```bash
   gcloud version
   gcloud auth list
   gcloud config get-value project
   ```

2. **If gcloud is not working**:
   - Reinstall Google Cloud SDK
   - Add to PATH: `C:\Users\YOUR_USER\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin`
   - Restart terminal

3. **Test deployment step by step**:
   ```bash
   # Test simple app first
   gcloud app deploy app_simple.yaml
   
   # If that works, deploy full app
   gcloud app deploy app.yaml
   ```

### 🆘 **If Still Getting Errors**

#### Option 1: Use Cloud Shell
1. Go to https://console.cloud.google.com/
2. Click "Activate Cloud Shell" (top right)
3. Upload your files:
   ```bash
   # In Cloud Shell
   git clone YOUR_REPOSITORY
   cd News_summary
   gcloud app deploy app.yaml
   ```

#### Option 2: Manual Fixes
Check the specific error in logs:
```bash
gcloud app logs tail -s default
```

Common fixes:
- **Import errors**: Check all file paths and imports
- **Database errors**: Ensure /tmp directory permissions
- **Template errors**: Check if templates directory exists

### ✅ **Expected Result**

Once fixed, your app should:
- ✅ Load without internal server error
- ✅ Show the calendar view at the root URL
- ✅ Have working news aggregation
- ✅ Same UI as localhost
- ✅ SQLite database working in /tmp/

### 📞 **Next Steps**

1. **Install/Fix Google Cloud SDK**
2. **Deploy simple version first**: `gcloud app deploy app_simple.yaml`
3. **If simple works, deploy full app**: `gcloud app deploy app.yaml`
4. **Check logs if errors persist**: `gcloud app logs tail -s default`

The fixes I made should resolve the internal server error. The main issues were:
- Missing gunicorn in requirements
- Incorrect SQLite path for App Engine
- Missing startup initialization 