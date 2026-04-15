import os
import logging
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

class Config:
    # Target URLs
    LIMITLESS_VGC_BASE_URL = os.getenv("LIMITLESS_VGC_BASE_URL")
    
    # Scraping Settings
    REQUEST_DELAY = 2.0  # Seconds to wait between requests
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    
    # Database Settings
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_NAME = os.getenv("DB_NAME", "vgc_db")
    
    # Security
    VGC_API_KEY = os.getenv("VGC_API_KEY")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

    # Fail-Fast Validation
    required_vars = {
        "DB_USER": DB_USER,
        "DB_PASSWORD": DB_PASSWORD,
        "VGC_API_KEY": VGC_API_KEY,
        "GEMINI_API_KEY": GEMINI_API_KEY
    }

    # Only validate if not using a specific override
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        missing = [k for k, v in required_vars.items() if v is None and k not in ["GEMINI_API_KEY"]]
        if missing:
            raise RuntimeError(f"CRITICAL: Missing required environment variables: {', '.join(missing)}. Check your .env file.")
        
        if DB_USER and DB_PASSWORD:
            SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
        else:
            # Local SQLite fallback - helpful for quick dev, but could be restricted in production
            SQLALCHEMY_DATABASE_URI = "sqlite:///./test_vgc.db"
    else:
        SQLALCHEMY_DATABASE_URI = DATABASE_URL

    if not GEMINI_API_KEY:
        logging.warning("GEMINI_API_KEY is not set. AI Coach features will be disabled.")
