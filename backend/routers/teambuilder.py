from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import httpx
from .. import crud, schemas, models
from ..database import get_db
from .auth import get_current_user

router = APIRouter(prefix="/teambuilder", tags=["teambuilder"])

# --- ENCYCLOPEDIA SEARCH ---

@router.get("/search/pokemon", response_model=List[schemas.SpeciesBase])
def search_pokemon(q: str, db: Session = Depends(get_db)):
    return crud.search_species(db, q)

@router.get("/search/moves", response_model=List[schemas.MoveBase])
def search_moves(q: str, db: Session = Depends(get_db)):
    return crud.search_moves(db, q)

@router.get("/search/items", response_model=List[schemas.ItemBase])
def search_items(q: str, db: Session = Depends(get_db)):
    return crud.search_items(db, q)

@router.get("/search/abilities", response_model=List[schemas.AbilityBase])
def search_abilities(q: str, db: Session = Depends(get_db)):
    return crud.search_abilities(db, q)

@router.get("/species/{species_id}/abilities", response_model=List[schemas.AbilityBase])
async def get_species_abilities(species_id: int, db: Session = Depends(get_db)):
    # 1. Try local competitive data first
    competitive = crud.get_species_abilities(db, species_id)
    if competitive:
        return competitive
    
    # 2. Fallback to PokeAPI
    db_species = db.query(models.Species).filter(models.Species.id == species_id).first()
    if not db_species:
        raise HTTPException(status_code=404, detail="Species not found")
    
    # Use limitless_id as it's already slugified (e.g., 'flutter-mane')
    poke_slug = db_species.limitless_id.lower()
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"https://pokeapi.co/api/v2/pokemon/{poke_slug}")
            if response.status_code != 200:
                # If slug fails, try name
                response = await client.get(f"https://pokeapi.co/api/v2/pokemon/{db_species.name.lower().replace(' ', '-')}")
                if response.status_code != 200:
                    return []
            
            data = response.json()
            abilities = []
            for entry in data.get("abilities", []):
                ability_name = entry["ability"]["name"].replace("-", " ").title()
                # Sync with local database
                db_ability = crud.get_or_create_ability(db, ability_name)
                abilities.append(db_ability)
            
            return abilities
        except Exception as e:
            print(f"PokeAPI error: {e}")
            return []

# --- USER TEAMS CRUD ---

@router.get("/teams", response_model=List[schemas.UserTeamBase])
def list_teams(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: models.user = Depends(get_current_user)
):
    return crud.get_user_teams(db, user_id=current_user.id, skip=skip, limit=limit)

@router.post("/teams", response_model=schemas.UserTeamBase)
def create_team(
    team: schemas.UserTeamCreate, 
    db: Session = Depends(get_db),
    current_user: models.user = Depends(get_current_user)
):
    return crud.create_user_team(db, user_id=current_user.id, name=team.name, format_id=team.format_id)

@router.get("/teams/{team_id}", response_model=schemas.UserTeamBase)
def get_team(
    team_id: int, 
    db: Session = Depends(get_db),
    current_user: models.user = Depends(get_current_user)
):
    db_team = crud.get_user_team(db, team_id, user_id=current_user.id)
    if not db_team:
        raise HTTPException(status_code=404, detail="Team not found")
    return db_team

@router.put("/teams/{team_id}", response_model=schemas.UserTeamBase)
def update_team(
    team_id: int, 
    team: schemas.UserTeamUpdate, 
    db: Session = Depends(get_db),
    current_user: models.user = Depends(get_current_user)
):
    db_team = crud.update_user_team(db, team_id, user_id=current_user.id, name=team.name, format_id=team.format_id)
    if not db_team:
        raise HTTPException(status_code=404, detail="Team not found")
    return db_team

@router.delete("/teams/{team_id}")
def delete_team(
    team_id: int, 
    db: Session = Depends(get_db),
    current_user: models.user = Depends(get_current_user)
):
    success = crud.delete_user_team(db, team_id, user_id=current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Team not found")
    return {"message": "Team deleted"}

# --- TEAM POKEMON UPDATES ---

@router.put("/pokemon/{pokemon_id}", response_model=schemas.UserTeamPokemonBase)
def update_pokemon(
    pokemon_id: int, 
    updates: schemas.UserTeamPokemonUpdate, 
    db: Session = Depends(get_db),
    current_user: models.user = Depends(get_current_user)
):
    db_pokemon = crud.update_user_team_pokemon(db, pokemon_id, user_id=current_user.id, updates=updates.dict(exclude_unset=True))
    if not db_pokemon:
        raise HTTPException(status_code=404, detail="Pokemon slot not found or access denied")
    return db_pokemon

@router.put("/pokemon/{pokemon_id}/moves/{slot}", response_model=schemas.UserTeamPokemonMoveBase)
def update_pokemon_move(
    pokemon_id: int, 
    slot: int, 
    move: schemas.UserTeamPokemonMoveUpdate, 
    db: Session = Depends(get_db),
    current_user: models.user = Depends(get_current_user)
):
    db_move = crud.update_user_team_pokemon_move(db, pokemon_id, user_id=current_user.id, slot=slot, move_id=move.move_id)
    if not db_move:
        raise HTTPException(status_code=404, detail="Move slot not found or access denied")
    return db_move
