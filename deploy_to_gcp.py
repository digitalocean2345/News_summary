#!/usr/bin/env python3
"""
GCP Deployment Helper Script for News Summary Application
"""

import os
import subprocess
import sys
from typing import Dict, Optional

class GCPDeployer:
    def __init__(self):
        self.project_id: Optional[str] = None
        self.region = "us-central1"
        self.db_instance_name = "news-db-instance"
        self.db_name = "news_aggregator"
        self.db_user = "dbuser"
        
    def run_command(self, command: str, check: bool = True) -> subprocess.CompletedProcess:
        """Run a shell command and return the result"""
        print(f"Running: {command}")
        try:
            result = subprocess.run(command, shell=True, check=check, 
                                  capture_output=True, text=True)
            if result.stdout:
                print(result.stdout)
            return result
        except subprocess.CalledProcessError as e:
            print(f"Error running command: {e}")
            if e.stderr:
                print(f"Error output: {e.stderr}")
            if check:
                sys.exit(1)
            return e
    
    def check_prerequisites(self) -> bool:
        """Check if required tools are installed"""
        print("Checking prerequisites...")
        
        # Check if gcloud is installed
        try:
            result = self.run_command("gcloud version", check=False)
            if result.returncode != 0:
                print("❌ Google Cloud SDK not found. Please install it first.")
                print("Visit: https://cloud.google.com/sdk/docs/install")
                return False
        except Exception:
            print("❌ Google Cloud SDK not found. Please install it first.")
            return False
        
        print("✅ Google Cloud SDK found")
        return True
    
    def setup_project(self) -> bool:
        """Set up GCP project"""
        print("\n=== Setting up GCP Project ===")
        
        # Get current project
        result = self.run_command("gcloud config get-value project", check=False)
        if result.returncode == 0 and result.stdout.strip():
            self.project_id = result.stdout.strip()
            print(f"Current project: {self.project_id}")
            
            use_current = input(f"Use current project '{self.project_id}'? (y/n): ").lower()
            if use_current != 'y':
                project_id = input("Enter your GCP project ID: ").strip()
                if project_id:
                    self.project_id = project_id
                    self.run_command(f"gcloud config set project {self.project_id}")
        else:
            project_id = input("Enter your GCP project ID: ").strip()
            if not project_id:
                print("❌ Project ID is required")
                return False
            self.project_id = project_id
            self.run_command(f"gcloud config set project {self.project_id}")
        
        # Enable required APIs
        print("Enabling required APIs...")
        apis = [
            "appengine.googleapis.com",
            "sql-component.googleapis.com",
            "sqladmin.googleapis.com"
        ]
        for api in apis:
            self.run_command(f"gcloud services enable {api}")
        
        return True
    
    def setup_database(self) -> bool:
        """Set up Cloud SQL database"""
        print("\n=== Setting up Cloud SQL Database ===")
        
        # Check if instance already exists
        result = self.run_command(
            f"gcloud sql instances describe {self.db_instance_name}", 
            check=False
        )
        
        if result.returncode == 0:
            print(f"✅ Database instance '{self.db_instance_name}' already exists")
        else:
            print(f"Creating database instance '{self.db_instance_name}'...")
            db_password = input("Enter a secure database password: ").strip()
            if not db_password:
                print("❌ Database password is required")
                return False
            
            # Create SQL instance
            self.run_command(f"""
                gcloud sql instances create {self.db_instance_name} \
                    --database-version=POSTGRES_14 \
                    --tier=db-f1-micro \
                    --region={self.region}
            """)
            
            # Create database
            self.run_command(f"""
                gcloud sql databases create {self.db_name} \
                    --instance={self.db_instance_name}
            """)
            
            # Create user
            self.run_command(f"""
                gcloud sql users create {self.db_user} \
                    --instance={self.db_instance_name} \
                    --password={db_password}
            """)
            
        return True
    
    def update_app_config(self) -> bool:
        """Update app.yaml with correct database configuration"""
        print("\n=== Updating Application Configuration ===")
        
        # Get database password
        db_password = input("Enter your database password: ").strip()
        if not db_password:
            print("❌ Database password is required")
            return False
        
        # Update app.yaml
        database_url = f"postgresql://{self.db_user}:{db_password}@/{self.db_name}?host=/cloudsql/{self.project_id}:{self.region}:{self.db_instance_name}"
        
        app_yaml_content = f"""runtime: python311

env_variables:
  DATABASE_URL: {database_url}
  
automatic_scaling:
  min_instances: 1
  max_instances: 10
  target_cpu_utilization: 0.6

handlers:
- url: /static
  static_dir: app/static
  
- url: /.*
  script: auto
  secure: always

beta_settings:
  cloud_sql_instances: {self.project_id}:{self.region}:{self.db_instance_name}
"""
        
        with open("app.yaml", "w") as f:
            f.write(app_yaml_content)
        
        print("✅ Updated app.yaml with database configuration")
        return True
    
    def deploy_app(self) -> bool:
        """Deploy the application to App Engine"""
        print("\n=== Deploying Application ===")
        
        # Check if App Engine app exists
        result = self.run_command("gcloud app describe", check=False)
        if result.returncode != 0:
            print("Creating App Engine application...")
            self.run_command(f"gcloud app create --region={self.region}")
        
        # Deploy the application
        print("Deploying to App Engine...")
        self.run_command("gcloud app deploy app.yaml --quiet")
        
        # Get the app URL
        result = self.run_command("gcloud app describe --format='value(defaultHostname)'")
        if result.stdout:
            app_url = f"https://{result.stdout.strip()}"
            print(f"\n🎉 Deployment successful!")
            print(f"Your application is available at: {app_url}")
            
            # Initialize database
            print("\nInitializing database tables...")
            init_url = f"{app_url}/api/admin/init-database"
            self.run_command(f"curl -X POST {init_url}", check=False)
        
        return True
    
    def run_deployment(self):
        """Run the complete deployment process"""
        print("🚀 Starting GCP deployment for News Summary Application")
        print("=" * 60)
        
        if not self.check_prerequisites():
            return False
        
        if not self.setup_project():
            return False
        
        if not self.setup_database():
            return False
        
        if not self.update_app_config():
            return False
        
        if not self.deploy_app():
            return False
        
        print("\n✅ Deployment completed successfully!")
        print("Your News Summary application is now running on Google Cloud Platform")
        print("with the same UI and functionality as your localhost setup.")
        
        return True

if __name__ == "__main__":
    deployer = GCPDeployer()
    deployer.run_deployment() 