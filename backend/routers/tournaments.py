from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from backend import crud, schemas

router = APIRouter(tags=["Tournaments & Meta"])

@router.get("/tournaments/search")
def search_tournaments(q: str, db: Session = Depends(get_db)):
    tournaments = crud.search_tournaments(db, query=q)
    return tournaments

@router.get("/players/{player_name}/history")
def read_player_history(player_name: str, db: Session = Depends(get_db)):
    history = crud.get_player_history(db, player_name)
    if not history:
        raise HTTPException(status_code=404, detail="Player not found")
    # Format the output so the AI can read it easily
    return [{"tournament": h.tournament.name, "rank": h.rank, "date": h.tournament.date} for h in history]

@router.get("/formats/{format_id}/meta")
def read_format_meta(format_id: str, db: Session = Depends(get_db)):
    meta = crud.get_format_meta(db, format_id)
    if not meta:
        raise HTTPException(status_code=404, detail="Format not found or no data available")
    return meta

@router.get("/meta/history")
def read_historical_meta(months: int, db: Session = Depends(get_db)):
    meta = crud.get_historical_meta(db, months)
    if not meta:
        raise HTTPException(status_code=404, detail="No historical data found for that timeframe")
    return meta

@router.get("/tournaments/", response_model=List[schemas.Tournament])
def read_tournaments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    tournaments = crud.get_tournaments(db, skip=skip, limit=limit)
    return tournaments

@router.get("/tournaments/{tournament_id}", response_model=schemas.Tournament)
def read_single_tournament(tournament_id: str, db: Session = Depends(get_db)):
    db_tournament = crud.get_tournament_by_id(db, tournament_id=tournament_id)
    if db_tournament is None:
        raise HTTPException(status_code=404, detail="Tournament not found")
    return db_tournament

@router.get("/tournaments/{tournament_id}/teams", response_model=List[schemas.TournamentResultBase])
def read_tournament_teams(tournament_id: str, db: Session = Depends(get_db)):
    """Returns the standings, players, and full teams for a specific tournament."""
    results = crud.get_tournament_results(db, limitless_tournament_id=tournament_id)
    if not results:
        raise HTTPException(status_code=404, detail="No teams found for this tournament")
    return results

@router.get("/tournaments/{tournament_id}/meta", response_model=List[schemas.TournamentMetagameStatBase])
def read_tournament_meta(tournament_id: str, db: Session = Depends(get_db)):
    """Returns the most used Pokémon and their usage percentages for a tournament."""
    stats = crud.get_tournament_meta(db, limitless_tournament_id=tournament_id)
    
    if not stats:
        raise HTTPException(status_code=404, detail="No metagame stats found for this tournament")
        
    return stats