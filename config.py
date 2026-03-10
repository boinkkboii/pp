import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

class Config:
    # Target URLs
    LIMITLESS_VGC_BASE_URL = "https://limitlessvgc.com"
    
    # Scraping Settings
    REQUEST_DELAY = 2.0  # Seconds to wait between requests to avoid IP bans
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    
    # Database Settings
    # Fallback to a local MySQL instance if environment variables aren't set
    DB_USER = os.getenv("DB_USER", "default_user")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_NAME = os.getenv("DB_NAME", "vgc_db")
    
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"