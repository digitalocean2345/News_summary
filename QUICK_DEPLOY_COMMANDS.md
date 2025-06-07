# Quick GCP Deployment Commands

## Step 1: Install Google Cloud SDK
Download and install from: https://cloud.google.com/sdk/docs/install-sdk

## Step 2: Authentication and Project Setup
```bash
# Login to Google Cloud
gcloud auth login

# Set your project (replace YOUR_PROJECT_ID with your actual project ID)
gcloud config set project YOUR_PROJECT_ID

# Create App Engine app
gcloud app create --region=us-central1

# Enable required APIs
gcloud services enable appengine.googleapis.com
gcloud services enable sql-component.googleapis.com
gcloud services enable sqladmin.googleapis.com
```

## Step 3: Create Database
```bash
# Create PostgreSQL instance (replace YOUR_PASSWORD with a secure password)
gcloud sql instances create news-db-instance \
    --database-version=POSTGRES_14 \
    --tier=db-f1-micro \
    --region=us-central1

# Create database
gcloud sql databases create news_aggregator --instance=news-db-instance

# Create database user (replace YOUR_PASSWORD)
gcloud sql users create dbuser --instance=news-db-instance --password=YOUR_PASSWORD
```

## Step 4: Update app.yaml
Edit the app.yaml file and replace the DATABASE_URL with your actual details:
```yaml
env_variables:
  DATABASE_URL: postgresql://dbuser:YOUR_PASSWORD@/news_aggregator?host=/cloudsql/YOUR_PROJECT_ID:us-central1:news-db-instance
```

## Step 5: Deploy
```bash
# Deploy to App Engine
gcloud app deploy app.yaml

# Open your deployed app
gcloud app browse
```

## Step 6: Initialize Database
After deployment, visit: https://YOUR_APP_URL/api/admin/init-database

## Your app will be available at:
https://YOUR_PROJECT_ID.uc.r.appspot.com

The UI will be EXACTLY the same as your localhost! 