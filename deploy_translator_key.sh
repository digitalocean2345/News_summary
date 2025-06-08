#!/bin/bash

# Local script to deploy Microsoft Translator API key to DigitalOcean droplet
# Run this from your local machine

set -e

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Get droplet IP
if [ -z "$1" ]; then
    echo -n "Enter your DigitalOcean Droplet IP address: "
    read DROPLET_IP
else
    DROPLET_IP=$1
fi

if [ -z "$DROPLET_IP" ]; then
    print_error "Droplet IP address is required!"
    exit 1
fi

print_status "Deploying Microsoft Translator API key setup to droplet: $DROPLET_IP"

# Check if setup script exists
if [ ! -f "setup_translator_key.sh" ]; then
    print_error "setup_translator_key.sh not found in current directory!"
    exit 1
fi

# Upload the setup script to the droplet
print_status "Uploading setup script to droplet..."
if ! scp setup_translator_key.sh root@$DROPLET_IP:/tmp/; then
    print_error "Failed to upload script. Check your SSH connection and IP address."
    exit 1
fi

# Make the script executable and run it
print_status "Running translator key setup on droplet..."
if ssh root@$DROPLET_IP "chmod +x /tmp/setup_translator_key.sh && /tmp/setup_translator_key.sh"; then
    print_status "✅ Translator key setup completed successfully!"
    
    echo ""
    print_status "🧪 Testing translation functionality..."
    sleep 2
    
    # Test the translation endpoint
    if curl -sf http://$DROPLET_IP/api/test-translation > /dev/null; then
        print_status "✅ Translation test passed!"
    else
        print_warning "⚠️ Translation test failed. Check the service logs."
    fi
    
    echo ""
    echo "🎉 Translation setup completed!"
    echo "🌐 Your app with translation is available at: http://$DROPLET_IP"
    echo ""
    echo "📊 Useful commands to run on your droplet:"
    echo "  - Check service status: ssh root@$DROPLET_IP 'systemctl status news-summary.service'"
    echo "  - View logs: ssh root@$DROPLET_IP 'journalctl -u news-summary.service -f'"
    echo "  - Test translation: curl http://$DROPLET_IP/api/test-translation"
    
else
    print_error "Failed to setup translator key. Please check the logs on your droplet."
    echo "You can manually run the setup by SSH'ing to your droplet and executing:"
    echo "  ssh root@$DROPLET_IP"
    echo "  /tmp/setup_translator_key.sh"
fi

# Clean up the uploaded script
ssh root@$DROPLET_IP "rm -f /tmp/setup_translator_key.sh" 2>/dev/null || true 