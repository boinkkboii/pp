# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 1. Import BOTH of your new router files
from backend.routers import tournaments, pokemon, chat
from database import engine, Base

app = FastAPI(title="Limitless VGC API", version="1.1.0") # Bumped version for the massive update!

# --- CORS Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"], 
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

@app.get("/")
def read_root():
    return {"status": "online", "message": "VGC Database API is running with Advanced Synergy!"}