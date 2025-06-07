# Run startup script first
try:
    from startup import main as startup_main
    startup_main()
except Exception as e:
    print(f"⚠️ Startup script failed: {e}")

from app.main import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080) 