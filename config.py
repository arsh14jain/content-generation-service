import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # API Configuration
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "your_gemini_api_key_here")
    API_KEY: str = os.getenv("API_KEY", "your_secure_api_key_here")
    
    # Scheduling Configuration
    POST_GENERATION_INTERVAL_HOURS: int = int(os.getenv("POST_GENERATION_INTERVAL_HOURS", "6"))
    POSTS_PER_TOPIC: int = int(os.getenv("POSTS_PER_TOPIC", "10"))
    
    # Database Configuration
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://username:password@localhost/educational_content")
    
    # Server Configuration
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

config = Config()