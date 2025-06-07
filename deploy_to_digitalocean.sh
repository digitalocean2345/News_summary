#!/bin/bash

# Local deployment script for DigitalOcean
# Run this from your local machine to deploy to your droplet

set -e

# Configuration
DROPLET_IP=""
DROPLET_USER="deployer"
LOCAL_REPO_PATH="."
GIT_REPO_URL=""

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

# Function to get user input
get_droplet_info() {
    if [ -z "$DROPLET_IP" ]; then
        echo -n "Enter your DigitalOcean Droplet IP address: "
        read DROPLET_IP
    fi
    
    if [ -z "$GIT_REPO_URL" ]; then
        echo -n "Enter your Git repository URL (https://github.com/user/repo.git): "
        read GIT_REPO_URL
    fi
}

# Function to upload setup script to droplet
upload_setup_script() {
    print_status "Uploading setup script to droplet..."
    scp setup_droplet.sh root@$DROPLET_IP:/tmp/
    ssh root@$DROPLET_IP "chmod +x /tmp/setup_droplet.sh"
}

# Function to run setup script on droplet
run_setup_script() {
    print_status "Running setup script on droplet (this may take a few minutes)..."
    ssh root@$DROPLET_IP "/tmp/setup_droplet.sh"
}

# Function to deploy application
deploy_application() {
    print_status "Deploying application..."
    
    # Commands to run on the droplet as deployer user
    ssh $DROPLET_USER@$DROPLET_IP << EOF
        set -e
        cd /var/www/news_summary
        
        # Clone repository if not exists
        if [ ! -d ".git" ]; then
            echo "📥 Cloning repository..."
            git clone $GIT_REPO_URL .
        else
            echo "📥 Pulling latest changes..."
            git pull origin main
        fi
        
        # Create virtual environment if not exists
        if [ ! -d "venv" ]; then
            echo "🐍 Creating virtual environment..."
            python3.11 -m venv venv
        fi
        
        # Activate virtual environment and install dependencies
        echo "📦 Installing dependencies..."
        source venv/bin/activate
        pip install --upgrade pip
        pip install -r requirements.txt
        
        # Initialize database if not exists
        if [ ! -f "news_aggregator.db" ]; then
            echo "🗃️ Initializing database..."
            python -c "
from app.database import engine
from app.models import models
models.Base.metadata.create_all(bind=engine)
print('✅ Database initialized successfully')
"
        fi
        
        # Set proper permissions
        sudo chown deployer:www-data news_aggregator.db 2>/dev/null || true
        chmod 664 news_aggregator.db 2>/dev/null || true
        
        echo "✅ Application deployed successfully!"
EOF
}

# Function to start services
start_services() {
    print_status "Starting services on droplet..."
    ssh root@$DROPLET_IP << 'EOF'
        systemctl enable news-summary.service
        systemctl start news-summary.service
        systemctl status news-summary.service --no-pager
EOF
}

# Function to test deployment
test_deployment() {
    print_status "Testing deployment..."
    sleep 5  # Wait for services to start
    
    # Test health endpoint
    if curl -sf http://$DROPLET_IP/health > /dev/null; then
        print_status "✅ Health check passed!"
    else
        print_warning "⚠️ Health check failed, but app might still be starting..."
    fi
    
    echo ""
    echo "🎉 Deployment completed!"
    echo "🌐 Your app is available at: http://$DROPLET_IP"
    echo ""
    echo "📊 Useful commands:"
    echo "  - Check logs: ssh $DROPLET_USER@$DROPLET_IP 'sudo journalctl -u news-summary.service -f'"
    echo "  - Check status: ssh $DROPLET_USER@$DROPLET_IP 'sudo systemctl status news-summary.service'"
    echo "  - Restart app: ssh $DROPLET_USER@$DROPLET_IP 'sudo systemctl restart news-summary.service'"
    echo "  - SSH to droplet: ssh $DROPLET_USER@$DROPLET_IP"
}

# Main execution
main() {
    echo "🚀 DigitalOcean Deployment Script"
    echo "=================================="
    
    # Check if setup script exists
    if [ ! -f "setup_droplet.sh" ]; then
        print_error "setup_droplet.sh not found in current directory!"
        exit 1
    fi
    
    get_droplet_info
    
    echo ""
    print_status "Deployment configuration:"
    echo "  Droplet IP: $DROPLET_IP"
    echo "  Git Repository: $GIT_REPO_URL"
    echo "  User: $DROPLET_USER"
    echo ""
    
    echo -n "Proceed with deployment? (y/N): "
    read confirm
    if [[ ! $confirm =~ ^[Yy]$ ]]; then
        print_warning "Deployment cancelled."
        exit 0
    fi
    
    # Step 1: Upload and run setup script
    upload_setup_script
    run_setup_script
    
    # Step 2: Deploy application
    deploy_application
    
    # Step 3: Start services
    start_services
    
    # Step 4: Test deployment
    test_deployment
}

# Check if SSH key is set up
check_ssh() {
    if [ ! -f ~/.ssh/id_rsa ] && [ ! -f ~/.ssh/id_ed25519 ]; then
        print_warning "No SSH key found. You may need to set up SSH key authentication."
        print_warning "Generate a key with: ssh-keygen -t ed25519 -C 'your_email@example.com'"
        print_warning "Then add it to your droplet during creation."
    fi
}

# Show usage if no arguments
if [ $# -eq 0 ]; then
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  --ip IP_ADDRESS     Set droplet IP address"
    echo "  --repo REPO_URL     Set git repository URL"
    echo "  --help              Show this help message"
    echo ""
    echo "Example:"
    echo "  $0 --ip 104.248.1.1 --repo https://github.com/user/News_summary.git"
    echo ""
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --ip)
                DROPLET_IP="$2"
                shift 2
                ;;
            --repo)
                GIT_REPO_URL="$2"
                shift 2
                ;;
            --help)
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                exit 1
                ;;
        esac
    done
fi

check_ssh
main 