#!/usr/bin/env python3
"""
Simple script to run the Podcast Relationship Mapper server.
"""

import os
import sys
from pathlib import Path

def check_requirements():
    """Check if all requirements are met before starting."""
    
    # Check if Gemini API key is set
    if not os.getenv('GEMINI_API_KEY'):
        print("❌ Error: GEMINI_API_KEY environment variable not set")
        print("Please set your Gemini API key:")
        print("export GEMINI_API_KEY='your_api_key_here'")
        print("\nGet your API key from: https://aistudio.google.com/app/apikey")
        return False
    
    # Check if required files exist
    required_files = ['main.py', 'database.py', 'audio_processor.py', 'data_service.py']
    for file in required_files:
        if not Path(file).exists():
            print(f"❌ Error: Required file {file} not found")
            return False
    
    # Try importing required packages
    try:
        import fastapi
        import uvicorn
        import sqlalchemy
        import pydub
        import google.generativeai
    except ImportError as e:
        print(f"❌ Error: Missing required package: {e}")
        print("Please install requirements: pip install -r requirements.txt")
        return False
    
    return True

def main():
    print("🎙️  Podcast Relationship Mapper")
    print("=" * 40)
    
    if not check_requirements():
        sys.exit(1)
    
    print("✅ All requirements met")
    print("🚀 Starting server...")
    print("\nServer will be available at: http://localhost:8000")
    print("API documentation at: http://localhost:8000/docs")
    print("\nTo stop the server, press Ctrl+C")
    print("-" * 40)
    
    # Initialize database
    try:
        from database import create_tables
        create_tables()
        print("✅ Database initialized")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        sys.exit(1)
    
    # Start the server
    try:
        import uvicorn
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
    except Exception as e:
        print(f"❌ Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()