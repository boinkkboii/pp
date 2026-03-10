# backend/crud.py
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_
from datetime import datetime, timedelta
import database

# ==========================================================
# CATEGORY 1: ENCYCLOPEDIA & FACT-CHECKING
# ==========================================================
def get_species_by_name(db: Session, name: str):
    return db.query(database.Species).filter(database.Species.name.ilike(name)).first()

def get_move_by_name(db: Session, name: str):
    return db.query(database.Move).filter(database.Move.name.ilike(name)).first()

def get_item_by_name(db: Session, name: str):
    return db.query(database.Item).filter(database.Item.name.ilike(name)).first()

def get_ability_by_name(db: Session, name: str):
    return db.query(database.Ability).filter(database.Ability.name.ilike(name)).first()

# ==========================================================
# CATEGORY 2: EVENT & PLAYER DISCOVERY
# ==========================================================
def search_tournaments(db: Session, query: str):
    """
    Splits the user query into individual words and searches for tournaments 
    that contain ALL of the words, regardless of order.
    (e.g., "Worlds 2025" will match "2025 Pokémon World Championships")
    """
    # Split "Worlds 2025" into ["Worlds", "2025"]
    terms = query.split() 
    
    # Create a list of ILIKE conditions for each word
    # We slice the 's' off 'Worlds' simply to catch 'World'
    filters = []
    for term in terms:
        # Simple plural handler for 'Worlds' -> 'World'
        search_term = term[:-1] if term.lower().endswith('s') else term
        filters.append(database.Tournament.name.ilike(f"%{search_term}%"))
        
    # Return tournaments that match ALL the filters
    return db.query(database.Tournament).filter(and_(*filters)).limit(10).all()

def get_player_history(db: Session, player_name: str):
    """Finds all tournament results for a specific player."""
    return (
        db.query(database.TournamentResult)
        .join(database.Player)
        .filter(database.Player.name.ilike(f"%{player_name}%"))
        .all()
    )

# ==========================================================
# CATEGORY 3: MICRO ANALYSIS
# ==========================================================
def get_tournaments(db: Session, skip: int = 0, limit: int = 100):
    return db.query(database.Tournament).order_by(desc(database.Tournament.date)).offset(skip).limit(limit).all()

def get_tournament_by_id(db: Session, tournament_id: str):
    return db.query(database.Tournament).filter(database.Tournament.limitless_id == tournament_id).first()

def get_tournament_results(db: Session, limitless_tournament_id: str):
    return (
        db.query(database.TournamentResult)
        .join(database.Tournament)
        .filter(database.Tournament.limitless_id == limitless_tournament_id)
        .all()
    )

def get_tournament_meta(db: Session, limitless_tournament_id: str):
    return (
        db.query(database.TournamentMetagameStat)
        .join(database.Tournament)
        .filter(database.Tournament.limitless_id == limitless_tournament_id)
        .all()
    )

# ==========================================================
# CATEGORY 4: MACRO ANALYSIS (Aggregations)
# ==========================================================
def get_format_meta(db: Session, format_id: str):
    """Averages usage stats across all tournaments in a specific format."""
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
    cutoff_date = (datetime.now() - timedelta(days=30 * months)).strftime("%Y-%m-%d")
    
    results = (
        db.query(
            database.Species.name,
            func.avg(database.TournamentMetagameStat.usage_share_pct).label('avg_usage')
        )
        .join(database.TournamentMetagameStat.species)
        .join(database.TournamentMetagameStat.tournament)
        .filter(database.Tournament.date >= cutoff_date)
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
    """Finds the most common Pokémon paired with the target species."""
    target_species = get_species_by_name(db, species_name)
    if not target_species:
        return []

    # 1. Find all teams that contain the target Pokémon
    teams_query = db.query(database.TeamPokemon.team_id).filter(database.TeamPokemon.species_id == target_species.id)
    if format_id:
        teams_query = teams_query.join(database.Team).join(database.TournamentResult).join(database.Tournament).join(database.Format).filter(database.Format.limitless_id == format_id)

    # 2. Count the OTHER Pokémon on those exact same teams
    results = (
        db.query(
            database.Species.name,
            func.count(database.TeamPokemon.id).label('pairings')
        )
        .join(database.TeamPokemon.species)
        .filter(
            database.TeamPokemon.team_id.in_(teams_query),
            database.TeamPokemon.species_id != target_species.id # Don't count the target itself!
        )
        .group_by(database.Species.id)
        .order_by(desc('pairings'))
        .limit(10)
        .all()
    )
    return [{"teammate": r.name, "pairings_count": r.pairings} for r in results]

def get_move_users(db: Session, move_name: str, format_id: str = None):
    """Finds which Pokémon most commonly run a specific move."""
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