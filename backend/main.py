# backend/main.py
import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S" # Formats the time to look like "2026-03-25 21:02:40"
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("google_genai.models").setLevel(logging.WARNING)
logging.getLogger("google_genai.types").setLevel(logging.WARNING)

# 1. Initialize Limiter
limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="Limitless VGC API", version="1.1.0")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# 1. Import BOTH of your new router files
from backend.routers import tournaments, pokemon, chat, teambuilder
from database import engine, Base

# --- ENSURE TABLES EXIST ---
Base.metadata.create_all(bind=engine)

# --- MIDDLEWARE: API Key Check (Optional but Recommended) ---
@app.middleware("http")
async def verify_api_key(request: Request, call_next):
    # Skip check for open routes (like root or options)
    if request.method == "OPTIONS" or request.url.path == "/":
        return await call_next(request)
        
    api_key = request.headers.get("X-API-KEY")
    expected_key = os.getenv("VGC_API_KEY")
    
    # Only enforce if a key is configured in the environment
    if expected_key and api_key != expected_key:
        raise HTTPException(status_code=403, detail="Invalid API Key")
        
    return await call_next(request)

# --- CORS Middleware ---
# Load allowed origins from environment or default to local development ports
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins, 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- ROUTER REGISTRATION ---
# 2. Mount the routers strictly to "/api" 
# This allows the routers themselves to handle the sub-paths (/encyclopedia, /synergy, /players, etc.)
app.include_router(tournaments.router, prefix="/api")
app.include_router(pokemon.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(teambuilder.router, prefix="/api")

@app.get("/")
def read_root():
    return {"status": "online", "message": "VGC Database API is running with Advanced Synergy!"}