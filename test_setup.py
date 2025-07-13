#!/usr/bin/env python3
"""
Test script to verify the Podcast Relationship Mapper setup.
"""

import os
import sys
from pathlib import Path

def test_imports():
    """Test if all required packages can be imported."""
    print("Testing package imports...")
    
    packages = [
        ('fastapi', 'FastAPI'),
        ('uvicorn', 'Uvicorn'),
        ('sqlalchemy', 'SQLAlchemy'),
        ('pydub', 'PyDub'),
        ('google.generativeai', 'Google Generative AI')
    ]
    
    for package, name in packages:
        try:
            __import__(package)
            print(f"  ✅ {name}")
        except ImportError as e:
            print(f"  ❌ {name}: {e}")
            return False
    
    return True

def test_database():
    """Test database creation and basic operations."""
    print("\nTesting database setup...")
    
    try:
        from database import create_tables, get_db, Episode, Entity
        from sqlalchemy.orm import Session
        
        # Create tables
        create_tables()
        print("  ✅ Database tables created")
        
        # Test database connection
        db_gen = get_db()
        db = next(db_gen)
        
        # Test basic query
        episodes = db.query(Episode).all()
        print(f"  ✅ Database connection working (found {len(episodes)} episodes)")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"  ❌ Database test failed: {e}")
        return False

def test_audio_processor():
    """Test audio processor initialization."""
    print("\nTesting audio processor...")
    
    # Check if API key is set
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("  ⚠️  GEMINI_API_KEY not set - audio processing will fail")
        print("     Set your API key: export GEMINI_API_KEY='your_key'")
        return False
    
    try:
        from audio_processor import AudioProcessor
        processor = AudioProcessor(api_key)
        print("  ✅ Audio processor initialized")
        return True
    except Exception as e:
        print(f"  ❌ Audio processor test failed: {e}")
        return False

def test_api():
    """Test FastAPI application setup."""
    print("\nTesting API setup...")
    
    try:
        from main import app
        print("  ✅ FastAPI app created")
        
        # Check if routes are registered
        routes = [route.path for route in app.routes]
        expected_routes = ['/api/episodes', '/api/episodes/{episode_id}/process']
        
        for route in expected_routes:
            if any(route in r for r in routes):
                print(f"  ✅ Route {route} registered")
            else:
                print(f"  ❌ Route {route} missing")
                return False
        
        return True
    except Exception as e:
        print(f"  ❌ API test failed: {e}")
        return False

def test_frontend():
    """Test frontend files."""
    print("\nTesting frontend files...")
    
    frontend_files = [
        'frontend/index.html',
        'frontend/styles.css',
        'frontend/app.js'
    ]
    
    for file in frontend_files:
        if Path(file).exists():
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file} missing")
            return False
    
    return True

def main():
    print("🧪 Podcast Relationship Mapper - Setup Test")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_database,
        test_audio_processor,
        test_api,
        test_frontend
    ]
    
    all_passed = True
    for test in tests:
        if not test():
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All tests passed! Your setup is ready.")
        print("\nNext steps:")
        print("1. Set GEMINI_API_KEY if not already set")
        print("2. Run: python run_server.py")
        print("3. Open frontend in browser")
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        sys.exit(1)

if __name__ == "__main__":
    main()