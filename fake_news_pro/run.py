"""
Run this file to start the backend server.
It fixes the module path issue automatically.
"""
import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import uvicorn

if __name__ == "__main__":
    print("\n" + "="*50)
    print("  🔍 AI Fake News Detector PRO - Backend")
    print("  Running on: http://localhost:8000")
    print("  API Docs:   http://localhost:8000/docs")
    print("="*50 + "\n")
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
