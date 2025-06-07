# Google Cloud Platform (GCP) Deployment Guide

This guide will help you deploy your News Summary application to Google Cloud Platform, maintaining the same UI and functionality as your localhost setup.

## Prerequisites

1. **Google Cloud Account**: Create a GCP account at https://cloud.google.com/
2. **Google Cloud SDK**: Install the `gcloud` CLI tool
3. **Project Setup**: Create a new GCP project

## Deployment Options

You have two main options for deployment:

### Option 1: Google App Engine (Recommended for beginners)
- Fully managed platform
- Auto-scaling
- Easy to deploy
- Built-in load balancing

### Option 2: Google Cloud Run (More flexible)
- Container-based deployment
- More control over configuration
- Better for complex applications

## Step-by-Step Deployment

### 1. Set up Google Cloud Project

```bash
# Install Google Cloud SDK first, then:
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
gcloud app create --region=us-central1  # or your preferred region
```

### 2. Set up Cloud SQL (PostgreSQL Database)

```bash
# Create a PostgreSQL instance
gcloud sql instances create news-db-instance \
    --database-version=POSTGRES_14 \
    --tier=db-f1-micro \
    --region=us-central1

# Create database
gcloud sql databases create news_aggregator --instance=news-db-instance

# Create database user
gcloud sql users create dbuser --instance=news-db-instance --password=your_secure_password
```

### 3. Configure Database Connection

Update the `app.yaml` file with your actual database connection details:

```yaml
env_variables:
  DATABASE_URL: postgresql://dbuser:your_secure_password@/news_aggregator?host=/cloudsql/YOUR_PROJECT_ID:us-central1:news-db-instance
```

### 4. Deploy to App Engine

```bash
# Deploy the application
gcloud app deploy app.yaml

# Open the deployed application
gcloud app browse
```

### Alternative: Deploy to Cloud Run

```bash
# Build and deploy to Cloud Run
gcloud run deploy news-summary-app \
    --source . \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --set-env-vars DATABASE_URL="postgresql://dbuser:your_secure_password@/news_aggregator?host=/cloudsql/YOUR_PROJECT_ID:us-central1:news-db-instance" \
    --add-cloudsql-instances YOUR_PROJECT_ID:us-central1:news-db-instance
```

## Environment Configuration

### Required Environment Variables

1. **DATABASE_URL**: PostgreSQL connection string
2. **GOOGLE_CLOUD_PROJECT**: Your GCP project ID

### Optional Configuration

- **Translation API**: If you want to use Google Translate instead of Microsoft Translator
- **Monitoring**: Enable Cloud Monitoring for better observability

## Database Initialization

After deployment, initialize your database tables:

```bash
# Option 1: Use the API endpoint
curl -X POST https://YOUR_APP_URL/api/admin/init-database

# Option 2: Run migration script locally connected to Cloud SQL
gcloud sql connect news-db-instance --user=dbuser
# Then run your table creation scripts
```

## Key Benefits of GCP Deployment

1. **Same UI Experience**: Your FastAPI templates and static files will work exactly the same
2. **PostgreSQL Database**: Better performance and reliability than SQLite
3. **Auto-scaling**: Handles traffic spikes automatically
4. **HTTPS by default**: Secure connections out of the box
5. **Custom domain**: Easy to set up custom domains
6. **Monitoring**: Built-in monitoring and logging

## Cost Considerations

- **App Engine**: Free tier available, pay-per-use
- **Cloud SQL**: $7-10/month for basic PostgreSQL instance
- **Cloud Run**: Very cost-effective, pay only for requests
- **Storage**: Minimal costs for static files

## Monitoring and Maintenance

1. **Cloud Logging**: View application logs
   ```bash
   gcloud app logs tail -s default
   ```

2. **Cloud Monitoring**: Set up alerts for downtime or errors

3. **Updates**: Deploy updates easily
   ```bash
   gcloud app deploy
   ```

## Troubleshooting

### Common Issues:

1. **Database Connection**: Ensure Cloud SQL instance is running and accessible
2. **Static Files**: Verify static files are properly mounted in app.yaml
3. **Dependencies**: Check that all requirements are in requirements.txt

### Debug Commands:

```bash
# View logs
gcloud app logs tail -s default

# SSH into App Engine instance (if needed)
gcloud app ssh

# Check Cloud SQL connection
gcloud sql connect news-db-instance --user=dbuser
```

## Security Best Practices

1. **Environment Variables**: Store sensitive data in environment variables
2. **IAM Roles**: Use least-privilege access
3. **Database Security**: Use strong passwords and SSL connections
4. **HTTPS**: Always use HTTPS in production (enabled by default)

## Next Steps

1. Deploy using the commands above
2. Test all functionality matches your localhost
3. Set up monitoring and alerts
4. Configure custom domain (optional)
5. Set up automated deployments via Cloud Build

Your News Summary application will have the exact same UI and functionality as localhost, but with the benefits of cloud hosting, better database performance, and automatic scaling! 