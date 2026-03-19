# backend/crud.py
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy import func, desc, and_
from datetime import date, timedelta
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
def get_tournaments(db: Session, skip: int = 0, limit: int = 100):
    return db.query(database.Tournament)\
             .options(joinedload(database.Tournament.format))\
             .order_by(desc(database.Tournament.date))\
             .offset(skip)\
             .limit(limit)\
             .all()

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
            selectinload(database.TournamentResult.team).selectinload(database.Team.pokemon)
        )
        .join(database.Tournament)
        .filter(database.Tournament.limitless_id == limitless_tournament_id)
        .all()
    )

def get_tournament_meta(db: Session, limitless_tournament_id: str):
    return (
        db.query(database.TournamentMetagameStat)
        .options(joinedload(database.TournamentMetagameStat.species))
        .join(database.Tournament)
        .filter(database.Tournament.limitless_id == limitless_tournament_id)
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