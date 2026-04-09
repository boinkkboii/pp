from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from ..models import Species, Move, Item, Ability, TeamPokemon, TeamPokemonMove

def search_species(db: Session, query: str):
    return db.query(Species).filter(Species.name.ilike(f"%{query}%")).limit(20).all()

def search_moves(db: Session, query: str):
    return db.query(Move).filter(Move.name.ilike(f"%{query}%")).limit(20).all()

def search_items(db: Session, query: str):
    return db.query(Item).filter(Item.name.ilike(f"%{query}%")).limit(20).all()

def search_abilities(db: Session, query: str):
    return db.query(Ability).filter(Ability.name.ilike(f"%{query}%")).limit(20).all()

def get_species_abilities(db: Session, species_id: int):
    return (
        db.query(Ability)
        .join(TeamPokemon)
        .filter(TeamPokemon.species_id == species_id)
        .distinct()
        .all()
    )

def get_species_by_name(db: Session, name: str):
    return db.query(Species).filter(Species.name.ilike(name)).first()

def get_move_by_name(db: Session, name: str):
    return db.query(Move).filter(Move.name.ilike(name)).first()

def get_item_by_name(db: Session, name: str):
    return db.query(Item).filter(Item.name.ilike(name)).first()

def get_ability_by_name(db: Session, name: str):
    return db.query(Ability).filter(Ability.name.ilike(name)).first()

def get_or_create_ability(db: Session, name: str):
    ability = get_ability_by_name(db, name)
    if not ability:
        ability = Ability(name=name)
        db.add(ability)
        db.commit()
        db.refresh(ability)
    return ability

def get_common_teammates(db: Session, species_name: str, format_id: str = None):
    target_species = get_species_by_name(db, species_name)
    if not target_species:
        return []

    from ..models import TournamentResult, Tournament, Format, Team
    teams_query = db.query(TeamPokemon.team_id).filter(TeamPokemon.species_id == target_species.id)
    if format_id:
        teams_query = teams_query.join(Team).join(TournamentResult).join(Tournament).join(Format).filter(Format.limitless_id == format_id)

    results = (
        db.query(
            Species.name,
            func.count(TeamPokemon.id).label('pairings')
        )
        .join(TeamPokemon.species)
        .filter(
            TeamPokemon.team_id.in_(teams_query),
            TeamPokemon.species_id != target_species.id 
        )
        .group_by(Species.id)
        .order_by(desc('pairings'))
        .limit(10)
        .all()
    )
    return [{"teammate": r.name, "pairings_count": r.pairings} for r in results]

def get_move_users(db: Session, move_name: str, format_id: str = None):
    target_move = get_move_by_name(db, move_name)
    if not target_move:
        return []

    from ..models import TournamentResult, Tournament, Format, Team
    query = (
        db.query(
            Species.name,
            func.count(TeamPokemonMove.pokemon_id).label('usage_count')
        )
        .join(TeamPokemonMove.pokemon)
        .join(TeamPokemon.species)
        .filter(TeamPokemonMove.move_id == target_move.id)
    )

    if format_id:
        query = query.join(TeamPokemon.team).join(Team.results).join(TournamentResult.tournament).join(Tournament.format).filter(Format.limitless_id == format_id)

    results = query.group_by(Species.id).order_by(desc('usage_count')).limit(10).all()
    return [{"species": r.name, "usage_count": r.usage_count} for r in results]

def get_pokemon_standard_build(db: Session, species_name: str, format_id: str = None):
    target_species = get_species_by_name(db, species_name)
    if not target_species:
        return {}

    from ..models import TournamentResult, Tournament, Format, Team
    # Base query for all instances of this species on teams
    query = db.query(TeamPokemon).filter(TeamPokemon.species_id == target_species.id)
    
    if format_id:
        query = query.join(Team).join(TournamentResult).join(Tournament).join(Format).filter(Format.limitless_id == format_id)

    # 1. Get Top Item
    top_item = (
        db.query(Item.name, func.count(TeamPokemon.item_id).label('count'))
        .join(TeamPokemon.item)
        .filter(TeamPokemon.id.in_(query.with_entities(TeamPokemon.id)))
        .group_by(Item.id)
        .order_by(desc('count'))
        .first()
    )

    # 2. Get Top Ability
    top_ability = (
        db.query(Ability.name, func.count(TeamPokemon.ability_id).label('count'))
        .join(TeamPokemon.ability)
        .filter(TeamPokemon.id.in_(query.with_entities(TeamPokemon.id)))
        .group_by(Ability.id)
        .order_by(desc('count'))
        .first()
    )

    # 3. Get Top Tera Type
    top_tera = (
        db.query(TeamPokemon.tera_type, func.count(TeamPokemon.tera_type).label('count'))
        .filter(TeamPokemon.id.in_(query.with_entities(TeamPokemon.id)))
        .group_by(TeamPokemon.tera_type)
        .order_by(desc('count'))
        .first()
    )

    # 4. Get Top 4 Moves
    top_moves = (
        db.query(Move.name, func.count(TeamPokemonMove.move_id).label('count'))
        .join(TeamPokemonMove.move)
        .filter(TeamPokemonMove.pokemon_id.in_(query.with_entities(TeamPokemon.id)))
        .group_by(Move.id)
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
