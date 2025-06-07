#!/usr/bin/env python3
"""
Minimal test app for App Engine debugging
"""

from fastapi import FastAPI

# Minimal FastAPI app
app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Minimal test working"} 