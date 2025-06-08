# Microsoft Translator API Key Setup Guide

This guide will help you add the Microsoft Translator API key to your DigitalOcean droplet to enable translation functionality in your news aggregator app.

## 🔑 Prerequisites

1. **Microsoft Azure Account**: You need an active Azure account
2. **Translator Service**: Create a Microsoft Translator resource in Azure
3. **DigitalOcean Droplet**: Your app should already be deployed on a droplet

## 📋 Step 1: Get Your Microsoft Translator API Key

1. Go to [Azure Portal](https://portal.azure.com/)
2. Navigate to **Create a resource** → **AI + Machine Learning** → **Translator**
3. Fill in the required information:
   - **Subscription**: Your Azure subscription
   - **Resource Group**: Create new or use existing
   - **Region**: Choose a region close to your users
   - **Name**: Give your translator service a name
   - **Pricing Tier**: Choose F0 (Free) for testing or S1 for production
4. Click **Review + Create** and then **Create**
5. Once deployed, go to your Translator resource
6. Navigate to **Keys and Endpoint** in the left sidebar
7. Copy **Key 1** and note the **Location/Region**

## 🚀 Step 2: Deploy API Key to Your Droplet

### Option A: Automated Setup (Recommended)

Run this command from your local machine:

```bash
./deploy_translator_key.sh YOUR_DROPLET_IP
```

The script will:
- Upload the setup script to your droplet
- Prompt you for your API key and region
- Configure the systemd service
- Restart your application
- Test the translation functionality

### Option B: Manual Setup

1. **SSH to your droplet:**
   ```bash
   ssh root@YOUR_DROPLET_IP
   ```

2. **Upload and run the setup script:**
   ```bash
   # Upload the script (from your local machine)
   scp setup_translator_key.sh root@YOUR_DROPLET_IP:/tmp/
   
   # SSH to droplet and run
   ssh root@YOUR_DROPLET_IP
   chmod +x /tmp/setup_translator_key.sh
   /tmp/setup_translator_key.sh
   ```

3. **Enter your API key when prompted**

## 🧪 Step 3: Test Translation Functionality

### Test via API Endpoint
```bash
curl http://YOUR_DROPLET_IP/api/test-translation
```

### Test via Python Script (on droplet)
```bash
# SSH to your droplet
ssh root@YOUR_DROPLET_IP

# Run the test script
python3 /var/www/news_summary/test_translation_on_droplet.py
```

## 🔧 Configuration Details

The setup script configures the following:

### Environment Variables
- `MS_TRANSLATOR_KEY`: Your Microsoft Translator API key
- `MS_TRANSLATOR_LOCATION`: Your Azure region (e.g., 'eastus', 'westeurope', or 'global')

### Files Updated
- `/etc/systemd/system/news-summary.service`: Systemd service with environment variables
- `/var/www/news_summary/.env`: Environment file for the application

## 📊 Monitoring and Troubleshooting

### Check Service Status
```bash
systemctl status news-summary.service
```

### View Application Logs
```bash
journalctl -u news-summary.service -f
```

### Restart Service
```bash
systemctl restart news-summary.service
```

### Common Issues

1. **"API key not found" error**
   - Verify the API key is correctly set in the service file
   - Check that the service was restarted after configuration

2. **Translation requests failing**
   - Verify your Azure Translator service is active
   - Check if you have remaining quota (Free tier: 2M characters/month)
   - Ensure the region is correctly configured

3. **Service not starting**
   - Check logs: `journalctl -u news-summary.service -n 50`
   - Verify all dependencies are installed
   - Check file permissions

## 💰 Pricing Information

### Microsoft Translator Pricing
- **Free Tier (F0)**: 2 million characters per month
- **Standard Tier (S1)**: $10 per million characters
- **Volume discounts** available for higher usage

### Usage Monitoring
- Monitor usage in Azure Portal → Your Translator Resource → Metrics
- Set up alerts for quota usage

## 🔒 Security Best Practices

1. **Protect your API key**
   - Never commit API keys to version control
   - Use environment variables only
   - Rotate keys regularly

2. **Network Security**
   - Use HTTPS in production
   - Consider IP restrictions in Azure if needed

3. **Access Control**
   - Limit access to your droplet
   - Use SSH keys instead of passwords
   - Regular security updates

## 📈 Performance Optimization

1. **Caching**: Consider implementing translation caching to reduce API calls
2. **Batch Processing**: Process multiple translations in batches when possible
3. **Error Handling**: Implement retry logic for failed translations

## 🆘 Support

If you encounter issues:

1. **Check the logs** first using the commands above
2. **Verify your Azure setup** in the Azure Portal
3. **Test the API key** using the provided test scripts
4. **Review the configuration** files for any syntax errors

## 📝 Files Created by This Setup

- `setup_translator_key.sh`: Server-side setup script
- `deploy_translator_key.sh`: Local deployment script  
- `test_translation_on_droplet.py`: Comprehensive test script
- `TRANSLATOR_SETUP_GUIDE.md`: This guide

---

**🎉 Once setup is complete, your news aggregator will automatically translate Chinese articles to English!** 