from sqlalchemy.orm import Session, selectinload
from ..models import UserTeam, UserTeamPokemon, UserTeamPokemonMove

def get_user_teams(db: Session, skip: int = 0, limit: int = 100):
    return db.query(UserTeam).options(
        selectinload(UserTeam.pokemons).selectinload(UserTeamPokemon.species)
    ).offset(skip).limit(limit).all()

def get_user_team(db: Session, team_id: int):
    return db.query(UserTeam).options(
        selectinload(UserTeam.pokemons).selectinload(UserTeamPokemon.moves).selectinload(UserTeamPokemonMove.move),
        selectinload(UserTeam.pokemons).selectinload(UserTeamPokemon.species),
        selectinload(UserTeam.pokemons).selectinload(UserTeamPokemon.item),
        selectinload(UserTeam.pokemons).selectinload(UserTeamPokemon.ability)
    ).filter(UserTeam.id == team_id).first()

def create_user_team(db: Session, name: str, format_id: int = None):
    db_team = UserTeam(name=name, format_id=format_id)
    db.add(db_team)
    db.commit()
    db.refresh(db_team)
    
    # Initialize 6 empty slots
    for i in range(1, 7):
        db_pokemon = UserTeamPokemon(team_id=db_team.id)
        db.add(db_pokemon)
        db.commit()
        db.refresh(db_pokemon)
        
        # Initialize 4 empty move slots
        for slot in range(1, 5):
            db_move = UserTeamPokemonMove(pokemon_id=db_pokemon.id, slot=slot)
            db.add(db_move)
    
    db.commit()
    db.refresh(db_team)
    return db_team

def update_user_team(db: Session, team_id: int, name: str = None, format_id: int = None):
    db_team = get_user_team(db, team_id)
    if not db_team:
        return None
    if name is not None:
        db_team.name = name
    if format_id is not None:
        db_team.format_id = format_id
    db.commit()
    db.refresh(db_team)
    return db_team

def delete_user_team(db: Session, team_id: int):
    db_team = get_user_team(db, team_id)
    if not db_team:
        return False
    db.delete(db_team)
    db.commit()
    return True

def update_user_team_pokemon(db: Session, pokemon_id: int, updates: dict):
    db_pokemon = db.query(UserTeamPokemon).filter(UserTeamPokemon.id == pokemon_id).first()
    if not db_pokemon:
        return None
    for key, value in updates.items():
        if hasattr(db_pokemon, key):
            setattr(db_pokemon, key, value)
    db.commit()
    db.refresh(db_pokemon)
    return db_pokemon

def update_user_team_pokemon_move(db: Session, pokemon_id: int, slot: int, move_id: int = None):
    db_move = db.query(UserTeamPokemonMove).filter(
        UserTeamPokemonMove.pokemon_id == pokemon_id,
        UserTeamPokemonMove.slot == slot
    ).first()
    if not db_move:
        return None
    db_move.move_id = move_id
    db.commit()
    db.refresh(db_move)
    return db_move
