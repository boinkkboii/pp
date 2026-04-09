from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy import func, desc, and_
from datetime import date, timedelta
from ..models import Tournament, TournamentResult, TournamentMetagameStat, Format, Player, Species, Team

def search_tournaments(db: Session, query: str):
    terms = query.split() 
    filters = []
    for term in terms:
        search_term = term[:-1] if term.lower().endswith('s') else term
        filters.append(Tournament.name.ilike(f"%{search_term}%"))
        
    return db.query(Tournament)\
             .options(joinedload(Tournament.format))\
             .filter(and_(*filters))\
             .limit(10)\
             .all()

def get_player_history(db: Session, player_name: str):
    return (
        db.query(TournamentResult)
        .options(
            joinedload(TournamentResult.player),
            joinedload(TournamentResult.tournament)
        )
        .join(Player)
        .filter(Player.name.ilike(f"%{player_name}%"))
        .all()
    )

def get_tournaments(db: Session, skip: int = 0, limit: int = 100, format_name: str = None, time_frame: str = None):
    query = db.query(Tournament).options(joinedload(Tournament.format))
    
    if format_name:
        query = query.join(Format).filter(Format.name.ilike(f"%{format_name}%"))
        
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
            query = query.filter(Tournament.date >= cutoff)
            
    return query.order_by(desc(Tournament.date)).offset(skip).limit(limit).all()

def get_tournament_by_id(db: Session, tournament_id: str):
    return db.query(Tournament)\
             .options(joinedload(Tournament.format))\
             .filter(Tournament.limitless_id == tournament_id)\
             .first()

def get_tournament_results(db: Session, limitless_tournament_id: str):
    return (
        db.query(TournamentResult)
        .options(
            joinedload(TournamentResult.player),
            selectinload(TournamentResult.team).selectinload(Team.pokemons)
        )
        .join(Tournament)
        .filter(Tournament.limitless_id == limitless_tournament_id)
        .all()
    )

def get_tournament_meta(db: Session, limitless_tournament_id: str):
    tournament = db.query(Tournament).filter(Tournament.limitless_id == limitless_tournament_id).first()
    if not tournament:
        return []
    
    return (
        db.query(TournamentMetagameStat)
        .options(joinedload(TournamentMetagameStat.species))
        .filter(TournamentMetagameStat.tournament_id == tournament.id)
        .order_by(TournamentMetagameStat.usage_share_pct.desc())
        .all()
    )

def get_latest_meta(db: Session, limit: int = 12):
    latest_tourney_with_stats = (
        db.query(Tournament)
        .join(TournamentMetagameStat)
        .order_by(desc(Tournament.date))
        .first()
    )

    if not latest_tourney_with_stats:
        return []

    return (
        db.query(TournamentMetagameStat)
        .options(joinedload(TournamentMetagameStat.species))
        .filter(TournamentMetagameStat.tournament_id == latest_tourney_with_stats.id)
        .order_by(TournamentMetagameStat.usage_share_pct.desc())
        .limit(limit)
        .all()
    )

def get_format_meta(db: Session, format_id: str):
    results = (
        db.query(
            Species.name,
            func.avg(TournamentMetagameStat.usage_share_pct).label('avg_usage')
        )
        .join(TournamentMetagameStat.species)
        .join(TournamentMetagameStat.tournament)
        .join(Tournament.format)
        .filter(Format.limitless_id == format_id)
        .group_by(Species.id)
        .order_by(desc('avg_usage'))
        .limit(50)
        .all()
    )
    return [{"species": r.name, "avg_usage_pct": round(r.avg_usage, 2)} for r in results]

def get_historical_meta(db: Session, months: int):
    cutoff_date = date.today() - timedelta(days=30 * months)
    
    results = (
        db.query(
            Species.name,
            func.avg(TournamentMetagameStat.usage_share_pct).label('avg_usage')
        )
        .join(TournamentMetagameStat.species)
        .join(TournamentMetagameStat.tournament)
        .filter(Tournament.date >= cutoff_date)
        .group_by(Species.id)
        .order_by(desc('avg_usage'))
        .limit(50)
        .all()
    )
    return [{"species": r.name, "avg_usage_pct": round(r.avg_usage, 2)} for r in results]

def get_all_formats(db: Session):
    return db.query(Format).all()
