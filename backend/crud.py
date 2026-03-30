# backend/crud.py
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy import func, desc, and_
from datetime import date, timedelta
import database

# ==========================================================
# CATEGORY 1: ENCYCLOPEDIA & FACT-CHECKING
# ==========================================================
def search_species(db: Session, query: str):
    return db.query(database.Species).filter(database.Species.name.ilike(f"%{query}%")).limit(20).all()

def search_moves(db: Session, query: str):
    return db.query(database.Move).filter(database.Move.name.ilike(f"%{query}%")).limit(20).all()

def search_items(db: Session, query: str):
    return db.query(database.Item).filter(database.Item.name.ilike(f"%{query}%")).limit(20).all()

def search_abilities(db: Session, query: str):
    return db.query(database.Ability).filter(database.Ability.name.ilike(f"%{query}%")).limit(20).all()

def get_species_abilities(db: Session, species_id: int):
    """Returns a list of unique abilities that have been seen on this species in the database."""
    return (
        db.query(database.Ability)
        .join(database.TeamPokemon)
        .filter(database.TeamPokemon.species_id == species_id)
        .distinct()
        .all()
    )

def get_species_by_name(db: Session, name: str):
    return db.query(database.Species).filter(database.Species.name.ilike(name)).first()

def get_move_by_name(db: Session, name: str):
    return db.query(database.Move).filter(database.Move.name.ilike(name)).first()

def get_item_by_name(db: Session, name: str):
    return db.query(database.Item).filter(database.Item.name.ilike(name)).first()

def get_ability_by_name(db: Session, name: str):
    return db.query(database.Ability).filter(database.Ability.name.ilike(name)).first()

def get_or_create_ability(db: Session, name: str):
    ability = get_ability_by_name(db, name)
    if not ability:
        ability = database.Ability(name=name)
        db.add(ability)
        db.commit()
        db.refresh(ability)
    return ability

# ==========================================================
# CATEGORY 2: EVENT & PLAYER DISCOVERY
# ==========================================================
def search_tournaments(db: Session, query: str):
    terms = query.split() 
    filters = []
    for term in terms:
        search_term = term[:-1] if term.lower().endswith('s') else term
        filters.append(database.Tournament.name.ilike(f"%{search_term}%"))
        
    return db.query(database.Tournament)\
             .options(joinedload(database.Tournament.format))\
             .filter(and_(*filters))\
             .limit(10)\
             .all()

def get_player_history(db: Session, player_name: str):
    return (
        db.query(database.TournamentResult)
        .options(
            joinedload(database.TournamentResult.player),
            joinedload(database.TournamentResult.tournament)
        )
        .join(database.Player)
        .filter(database.Player.name.ilike(f"%{player_name}%"))
        .all()
    )

# ==========================================================
# CATEGORY 3: MICRO ANALYSIS
# ==========================================================
def get_tournaments(db: Session, skip: int = 0, limit: int = 100, format_name: str = None, time_frame: str = None):
    query = db.query(database.Tournament).options(joinedload(database.Tournament.format))
    
    # FILTER 1: The Format
    if format_name:
        query = query.join(database.Format).filter(database.Format.name.ilike(f"%{format_name}%"))
        
    # FILTER 2: The Time Frame
    if time_frame:
        today = date.today()
        if time_frame == "last_week":
            cutoff = today - timedelta(days=7)
        elif time_frame == "last_month":
            cutoff = today - timedelta(days=30)
        elif time_frame == "last_3_months":
            cutoff = today - timedelta(days=90)
        elif time_frame == "last_year":
            cutoff = today - timedelta(days=365)
        else:
            cutoff = None
            
        if cutoff:
            query = query.filter(database.Tournament.date >= cutoff)
            
    return query.order_by(desc(database.Tournament.date)).offset(skip).limit(limit).all()

def get_tournament_by_id(db: Session, tournament_id: str):
    return db.query(database.Tournament)\
             .options(joinedload(database.Tournament.format))\
             .filter(database.Tournament.limitless_id == tournament_id)\
             .first()

def get_tournament_results(db: Session, limitless_tournament_id: str):
    return (
        db.query(database.TournamentResult)
        .options(
            joinedload(database.TournamentResult.player),
            selectinload(database.TournamentResult.team).selectinload(database.Team.pokemons)
        )
        .join(database.Tournament)
        .filter(database.Tournament.limitless_id == limitless_tournament_id)
        .all()
    )

def get_tournament_meta(db: Session, limitless_tournament_id: str):
    """Fetches the metagame usage stats using a bulletproof two-step query."""
    tournament = db.query(database.Tournament).filter(database.Tournament.limitless_id == limitless_tournament_id).first()

    if not tournament:
        return []
    
    return (
        db.query(database.TournamentMetagameStat)
        .options(joinedload(database.TournamentMetagameStat.species))
        .filter(database.TournamentMetagameStat.tournament_id == tournament.id)
        .order_by(database.TournamentMetagameStat.usage_share_pct.desc())
        .all()
    )

from sqlalchemy import desc # Make sure this is imported at the top!

def get_latest_meta(db: Session, limit: int = 12):
    """Finds the most recent tournament with meta stats and returns the Top Pokémon."""
    latest_tourney_with_stats = (
        db.query(database.Tournament)
        .join(database.TournamentMetagameStat)
        .order_by(desc(database.Tournament.date))
        .first()
    )

    if not latest_tourney_with_stats:
        return []

    return (
        db.query(database.TournamentMetagameStat)
        .options(joinedload(database.TournamentMetagameStat.species))
        .filter(database.TournamentMetagameStat.tournament_id == latest_tourney_with_stats.id)
        .order_by(database.TournamentMetagameStat.usage_share_pct.desc())
        .limit(limit)
        .all()
    )

# ==========================================================
# CATEGORY 4: MACRO ANALYSIS (Aggregations)
# ==========================================================
def get_format_meta(db: Session, format_id: str):
    results = (
        db.query(
            database.Species.name,
            func.avg(database.TournamentMetagameStat.usage_share_pct).label('avg_usage')
        )
        .join(database.TournamentMetagameStat.species)
        .join(database.TournamentMetagameStat.tournament)
        .join(database.Tournament.format)
        .filter(database.Format.limitless_id == format_id)
        .group_by(database.Species.id)
        .order_by(desc('avg_usage'))
        .limit(50)
        .all()
    )
    return [{"species": r.name, "avg_usage_pct": round(r.avg_usage, 2)} for r in results]

def get_historical_meta(db: Session, months: int):
    """Averages usage stats for tournaments strictly within the last X months."""
    cutoff_date = date.today() - timedelta(days=30 * months)
    
    results = (
        db.query(
            database.Species.name,
            func.avg(database.TournamentMetagameStat.usage_share_pct).label('avg_usage')
        )
        .join(database.TournamentMetagameStat.species)
        .join(database.TournamentMetagameStat.tournament)
        .filter(database.Tournament.date >= cutoff_date) # Now comparing a Date object to a Date object
        .group_by(database.Species.id)
        .order_by(desc('avg_usage'))
        .limit(50)
        .all()
    )
    return [{"species": r.name, "avg_usage_pct": round(r.avg_usage, 2)} for r in results]

# ==========================================================
# CATEGORY 5: TEAMBUILDING & SYNERGY
# ==========================================================
def get_common_teammates(db: Session, species_name: str, format_id: str = None):
    target_species = get_species_by_name(db, species_name)
    if not target_species:
        return []

    teams_query = db.query(database.TeamPokemon.team_id).filter(database.TeamPokemon.species_id == target_species.id)
    if format_id:
        teams_query = teams_query.join(database.Team).join(database.TournamentResult).join(database.Tournament).join(database.Format).filter(database.Format.limitless_id == format_id)

    results = (
        db.query(
            database.Species.name,
            func.count(database.TeamPokemon.id).label('pairings')
        )
        .join(database.TeamPokemon.species)
        .filter(
            database.TeamPokemon.team_id.in_(teams_query),
            database.TeamPokemon.species_id != target_species.id 
        )
        .group_by(database.Species.id)
        .order_by(desc('pairings'))
        .limit(10)
        .all()
    )
    return [{"teammate": r.name, "pairings_count": r.pairings} for r in results]

def get_move_users(db: Session, move_name: str, format_id: str = None):
    target_move = get_move_by_name(db, move_name)
    if not target_move:
        return []

    query = (
        db.query(
            database.Species.name,
            func.count(database.TeamPokemonMove.pokemon_id).label('usage_count')
        )
        .join(database.TeamPokemonMove.pokemon)
        .join(database.TeamPokemon.species)
        .filter(database.TeamPokemonMove.move_id == target_move.id)
    )

    if format_id:
        query = query.join(database.TeamPokemon.team).join(database.Team.results).join(database.TournamentResult.tournament).join(database.Tournament.format).filter(database.Format.limitless_id == format_id)

    results = query.group_by(database.Species.id).order_by(desc('usage_count')).limit(10).all()
    return [{"species": r.name, "usage_count": r.usage_count} for r in results]

def get_pokemon_standard_build(db: Session, species_name: str, format_id: str = None):
    target_species = get_species_by_name(db, species_name)
    if not target_species:
        return {}

    # Base query for all instances of this species on teams
    query = db.query(database.TeamPokemon).filter(database.TeamPokemon.species_id == target_species.id)
    
    if format_id:
        query = query.join(database.Team).join(database.TournamentResult).join(database.Tournament).join(database.Format).filter(database.Format.limitless_id == format_id)

    # 1. Get Top Item
    top_item = (
        db.query(database.Item.name, func.count(database.TeamPokemon.item_id).label('count'))
        .join(database.TeamPokemon.item)
        .filter(database.TeamPokemon.id.in_(query.with_entities(database.TeamPokemon.id)))
        .group_by(database.Item.id)
        .order_by(desc('count'))
        .first()
    )

    # 2. Get Top Ability
    top_ability = (
        db.query(database.Ability.name, func.count(database.TeamPokemon.ability_id).label('count'))
        .join(database.TeamPokemon.ability)
        .filter(database.TeamPokemon.id.in_(query.with_entities(database.TeamPokemon.id)))
        .group_by(database.Ability.id)
        .order_by(desc('count'))
        .first()
    )

    # 3. Get Top Tera Type
    top_tera = (
        db.query(database.TeamPokemon.tera_type, func.count(database.TeamPokemon.tera_type).label('count'))
        .filter(database.TeamPokemon.id.in_(query.with_entities(database.TeamPokemon.id)))
        .group_by(database.TeamPokemon.tera_type)
        .order_by(desc('count'))
        .first()
    )

    # 4. Get Top 4 Moves
    top_moves = (
        db.query(database.Move.name, func.count(database.TeamPokemonMove.move_id).label('count'))
        .join(database.TeamPokemonMove.move)
        .filter(database.TeamPokemonMove.pokemon_id.in_(query.with_entities(database.TeamPokemon.id)))
        .group_by(database.Move.id)
        .order_by(desc('count'))
        .limit(4)
        .all()
    )

    return {
        "species": target_species.name,
        "item": top_item[0] if top_item else "Unknown",
        "ability": top_ability[0] if top_ability else "Unknown",
        "tera_type": top_tera[0] if top_tera else "Unknown",
        "moves": [m[0] for m in top_moves]
    }

# ==========================================================
# CATEGORY 5: UTILIY
# ==========================================================
def get_all_formats(db: Session):
    """Fetches a list of all available tournament formats."""
    return db.query(database.Format).all()

# ==========================================================
# CATEGORY 6: USER TEAMBUILDER CRUD
# ==========================================================

def get_user_teams(db: Session, skip: int = 0, limit: int = 100):
    return db.query(database.UserTeam).options(
        selectinload(database.UserTeam.pokemons).selectinload(database.UserTeamPokemon.species)
    ).offset(skip).limit(limit).all()

def get_user_team(db: Session, team_id: int):
    return db.query(database.UserTeam).options(
        selectinload(database.UserTeam.pokemons).selectinload(database.UserTeamPokemon.moves).selectinload(database.UserTeamPokemonMove.move),
        selectinload(database.UserTeam.pokemons).selectinload(database.UserTeamPokemon.species),
        selectinload(database.UserTeam.pokemons).selectinload(database.UserTeamPokemon.item),
        selectinload(database.UserTeam.pokemons).selectinload(database.UserTeamPokemon.ability)
    ).filter(database.UserTeam.id == team_id).first()

def create_user_team(db: Session, name: str, format_id: int = None):
    db_team = database.UserTeam(name=name, format_id=format_id)
    db.add(db_team)
    db.commit()
    db.refresh(db_team)
    
    # Initialize 6 empty slots
    for i in range(1, 7):
        db_pokemon = database.UserTeamPokemon(team_id=db_team.id)
        db.add(db_pokemon)
        db.commit()
        db.refresh(db_pokemon)
        
        # Initialize 4 empty move slots
        for slot in range(1, 5):
            db_move = database.UserTeamPokemonMove(pokemon_id=db_pokemon.id, slot=slot)
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
    db_pokemon = db.query(database.UserTeamPokemon).filter(database.UserTeamPokemon.id == pokemon_id).first()
    if not db_pokemon:
        return None
    for key, value in updates.items():
        if hasattr(db_pokemon, key):
            setattr(db_pokemon, key, value)
    db.commit()
    db.refresh(db_pokemon)
    return db_pokemon

def update_user_team_pokemon_move(db: Session, pokemon_id: int, slot: int, move_id: int = None):
    db_move = db.query(database.UserTeamPokemonMove).filter(
        database.UserTeamPokemonMove.pokemon_id == pokemon_id,
        database.UserTeamPokemonMove.slot == slot
    ).first()
    if not db_move:
        return None
    db_move.move_id = move_id
    db.commit()
    db.refresh(db_move)
    return db_move