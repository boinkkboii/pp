# backend/routers/pokemon.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from backend import crud

router = APIRouter(tags=["Pokemon & Synergy"])

@router.get("/encyclopedia/pokemon/{name}")
def read_pokemon_stats(name: str, db: Session = Depends(get_db)):
    db_species = crud.get_species_by_name(db, name)
    if not db_species:
        raise HTTPException(status_code=404, detail="Pokémon not found")
    return db_species

@router.get("/encyclopedia/moves/{name}")
def read_move_details(name: str, db: Session = Depends(get_db)):
    db_move = crud.get_move_by_name(db, name)
    if not db_move:
        raise HTTPException(status_code=404, detail="Move not found")
    return db_move

@router.get("/encyclopedia/{item_or_ability}s/{name}")
def read_item_or_ability(item_or_ability: str, name: str, db: Session = Depends(get_db)):
    if item_or_ability == "item":
        result = crud.get_item_by_name(db, name)
    elif item_or_ability == "ability":
        result = crud.get_ability_by_name(db, name)
    else:
        raise HTTPException(status_code=400, detail="Must be 'item' or 'ability'")
        
    if not result:
        raise HTTPException(status_code=404, detail="Not found")
    return result

@router.get("/synergy/{species_name}/teammates")
def read_common_teammates(species_name: str, format: str = None, db: Session = Depends(get_db)):
    results = crud.get_common_teammates(db, species_name, format_id=format)
    if not results:
        raise HTTPException(status_code=404, detail="No teammates found or species doesn't exist")
    return results

@router.get("/synergy/moves/{move_name}/users")
def read_move_users(move_name: str, format: str = None, db: Session = Depends(get_db)):
    results = crud.get_move_users(db, move_name, format_id=format)
    if not results:
        raise HTTPException(status_code=404, detail="No users found for this move")
    return results