#!/usr/bin/env python3
"""
Simple SQLite GCP Deployment Script for News Summary Application
"""

import os
import subprocess
import sys

class SQLiteGCPDeployer:
    def __init__(self):
        self.project_id = None
        self.region = "us-central1"
        
    def run_command(self, command: str, check: bool = True):
        """Run a shell command and return the result"""
        print(f"🔧 Running: {command}")
        try:
            result = subprocess.run(command, shell=True, check=check, 
                                  capture_output=True, text=True)
            if result.stdout:
                print(result.stdout)
            return result
        except subprocess.CalledProcessError as e:
            print(f"❌ Error: {e}")
            if e.stderr:
                print(f"Error output: {e.stderr}")
            if check:
                sys.exit(1)
            return e
    
    def check_gcloud(self):
        """Check if gcloud is installed"""
        print("🔍 Checking Google Cloud SDK...")
        try:
            result = self.run_command("gcloud version", check=False)
            if result.returncode != 0:
                print("❌ Google Cloud SDK not found!")
                print("📥 Please install from: https://cloud.google.com/sdk/docs/install-sdk")
                return False
            print("✅ Google Cloud SDK found!")
            return True
        except Exception:
            print("❌ Google Cloud SDK not found!")
            print("📥 Please install from: https://cloud.google.com/sdk/docs/install-sdk")
            return False
    
    def setup_project(self):
        """Setup GCP project"""
        print("\n📋 Setting up GCP project...")
        
        # Check current project
        result = self.run_command("gcloud config get-value project", check=False)
        if result.returncode == 0 and result.stdout.strip():
            current_project = result.stdout.strip()
            print(f"Current project: {current_project}")
            
            use_current = input(f"Use current project '{current_project}'? (y/n): ").lower()
            if use_current == 'y':
                self.project_id = current_project
            else:
                self.project_id = input("Enter your GCP project ID: ").strip()
                if self.project_id:
                    self.run_command(f"gcloud config set project {self.project_id}")
        else:
            self.project_id = input("Enter your GCP project ID: ").strip()
            if not self.project_id:
                print("❌ Project ID is required!")
                return False
            self.run_command(f"gcloud config set project {self.project_id}")
        
        print(f"✅ Using project: {self.project_id}")
        return True
    
    def setup_app_engine(self):
        """Setup App Engine application"""
        print("\n🚀 Setting up App Engine...")
        
        # Check if App Engine app exists
        result = self.run_command("gcloud app describe", check=False)
        if result.returncode != 0:
            print("Creating App Engine application...")
            self.run_command(f"gcloud app create --region={self.region}")
        else:
            print("✅ App Engine application already exists")
        
        # Enable App Engine API
        print("Enabling App Engine API...")
        self.run_command("gcloud services enable appengine.googleapis.com")
        return True
    
    def copy_database(self):
        """Copy local SQLite database for initial data"""
        print("\n📊 Preparing database...")
        
        # Check if local database exists
        if os.path.exists("news.db"):
            print("✅ Found local database: news.db")
            # The database will be included in the deployment
        elif os.path.exists("news_aggregator.db"):
            print("✅ Found local database: news_aggregator.db")
            # Copy to expected location
            self.run_command("copy news_aggregator.db news.db" if os.name == 'nt' else "cp news_aggregator.db news.db")
        else:
            print("⚠️ No local database found - will create fresh database on deployment")
        
        return True
    
    def deploy_app(self):
        """Deploy the application"""
        print("\n🚀 Deploying to Google App Engine...")
        
        # Deploy
        self.run_command("gcloud app deploy app.yaml --quiet")
        
        # Get app URL
        result = self.run_command("gcloud app describe --format='value(defaultHostname)'")
        if result.stdout:
            app_url = f"https://{result.stdout.strip()}"
            print(f"\n🎉 Deployment successful!")
            print(f"📱 Your app is live at: {app_url}")
            
            # Initialize database if needed
            print("\n🔄 Initializing database...")
            self.run_command(f"curl -X POST {app_url}/api/admin/init-database", check=False)
            
            print(f"\n✅ Your News Summary app is ready!")
            print(f"🌐 Visit: {app_url}")
            print(f"📊 Same UI as localhost, now on Google Cloud!")
            
        return True
    
    def run_deployment(self):
        """Run the complete deployment"""
        print("🚀 SQLite Deployment to Google Cloud Platform")
        print("=" * 50)
        print("✨ This will give you the EXACT same UI as localhost!")
        print("💰 Cost: FREE (no database costs)")
        print("=" * 50)
        
        if not self.check_gcloud():
            return False
        
        if not self.setup_project():
            return False
        
        if not self.setup_app_engine():
            return False
        
        if not self.copy_database():
            return False
        
        if not self.deploy_app():
            return False
        
        print("\n🎊 SUCCESS! Your News Summary app is now live on Google Cloud!")
        print("🔄 Updates: Just run 'gcloud app deploy' to update")
        print("📈 Monitoring: Check Google Cloud Console for logs and metrics")
        
        return True

if __name__ == "__main__":
    deployer = SQLiteGCPDeployer()
    deployer.run_deployment() 