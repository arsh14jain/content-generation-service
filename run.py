#!/usr/bin/env python3
"""
Startup script for the Educational Content Generation Service
"""

import os
import sys
import logging
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def setup_environment():
    """Set up environment variables from .env file if it exists"""
    env_file = project_root / ".env"
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ.setdefault(key, value)

def check_requirements():
    """Check if basic requirements are met"""
    from config import config
    
    issues = []
    
    # Check Gemini API key
    if config.GEMINI_API_KEY == "your_gemini_api_key_here":
        issues.append("GEMINI_API_KEY not configured. Please set your Gemini API key.")
    
    # Check database URL
    if "username:password@localhost" in config.DATABASE_URL:
        issues.append("DATABASE_URL not configured. Please set your PostgreSQL connection string.")
    
    if issues:
        print("⚠️  Configuration Issues Found:")
        for issue in issues:
            print(f"   - {issue}")
        print("\nPlease check your environment variables or .env file.")
        print("See README.md for setup instructions.")
        return False
    
    return True

def main():
    """Main entry point"""
    print("🚀 Starting Educational Content Generation Service")
    
    # Set up environment
    setup_environment()
    
    # Check configuration
    if not check_requirements():
        sys.exit(1)
    
    # Import and run the application
    try:
        import uvicorn
        from config import config
        
        print(f"📡 Server starting on {config.HOST}:{config.PORT}")
        print(f"🔧 Debug mode: {config.DEBUG}")
        print(f"📊 API docs available at: http://{config.HOST}:{config.PORT}/docs")
        
        uvicorn.run(
            "app.main:app",
            host=config.HOST,
            port=config.PORT,
            reload=config.DEBUG,
            log_level=config.LOG_LEVEL.lower()
        )
        
    except ImportError as e:
        print(f"❌ Missing dependencies: {e}")
        print("Please run: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()