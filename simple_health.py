#!/usr/bin/env python3
"""
Simple health check for debugging App Engine deployment
"""

import os
import logging
from fastapi import FastAPI
from fastapi.responses import JSONResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Simple FastAPI app for debugging
app = FastAPI(title="Health Check", version="1.0.0")

@app.on_event("startup")
async def startup_event():
    logger.info("🚀 Health check app starting up...")

@app.get("/")
async def root():
    return {
        "message": "App is working!",
        "status": "healthy",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "version": "1.0.0"
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "message": "Simple health check passed",
        "deployment": "Google App Engine",
        "environment": os.getenv("ENVIRONMENT", "development")
    }

@app.get("/test")
async def test():
    return {
        "message": "Test endpoint working",
        "gunicorn": "working",
        "fastapi": "working"
    }

# Export the app for gunicorn
app = app 