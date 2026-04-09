import logging
import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Import your custom modules
from backend.core.config import Config
from data_pipeline.scraper import VGCScraper
from backend.models import (
    Base, Species, Move, Item, Ability, Format, Tournament, 
    Player, Team, TournamentResult, TeamPokemon, TeamPokemonMove, TournamentMetagameStat
)
from backend.database import SessionLocal, engine

# --- LOGGING SETUP ---
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - [%(module)s] %(message)s'
)
logger = logging.getLogger(__name__)

# --- DATABASE SETUP ---
# (Using SessionLocal and engine imported from backend.database)

def get_or_create(session, model, defaults=None, **kwargs):
    """
    Safely retrieves a record or creates it if it doesn't exist.
    Uses flush() to get the primary key without committing the transaction.
    """
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance, False
    
    params = dict((k, v) for k, v in kwargs.items())
    params.update(defaults or {})
    instance = model(**params)
    session.add(instance)
    session.flush() 
    return instance, True

def get_or_create_species(session, limitless_id, fallback_name):
    """
    Specialized lookup for Species. If the seeder missed a Pokemon, 
    we create a 'Skeleton' record so the foreign key constraints don't crash.
    """
    if not limitless_id:
        limitless_id = fallback_name.lower().replace(" ", "-")
        
    species = session.query(Species).filter_by(limitless_id=limitless_id).first()
    if species:
        return species
        
    logger.warning(f"⚠️ Species '{limitless_id}' not found in Seeder DB! Creating skeleton record.")
    new_species = Species(
        limitless_id=limitless_id,
        name=fallback_name,
        type_1="Unknown", # Placeholder for missing data
        base_hp=0, base_atk=0, base_def=0, base_spa=0, base_spd=0, base_spe=0
    )
    session.add(new_species)
    session.flush()
    return new_species

def run_vgc_pipeline():
    logger.info("Initializing Database Schema...")
    session = SessionLocal()
    scraper = VGCScraper()
    
    logger.info("=== STARTING FULL VGC DATA PIPELINE ===")
    
    # ---------------------------------------------------------
    # LEVEL 1: MASTER TOURNAMENT INDEX
    # ---------------------------------------------------------
    all_tournaments = []
    current_page = 1
    
    logger.info(f"Fetching tournament list page {current_page}...")
    master_html = scraper.fetch_page(f"{scraper.base_url}/tournaments?show=100&page={current_page}")
    master_data = scraper.parse_tournament_list(master_html)
    
    if not master_data or not master_data.get("tournaments"):
        logger.error("No tournaments found on index page. Aborting.")
        return
        
    all_tournaments.extend(master_data["tournaments"])
    max_page = master_data["pagination"].get("max_page", 1)
    
    # Pagination Loop
    for page in range(2, max_page + 1):
        logger.info(f"Fetching tournament index page {page}/{max_page}...")
        page_html = scraper.fetch_page(f"{scraper.base_url}/tournaments?show=100&page={page}")
        page_data = scraper.parse_tournament_list(page_html)
        if page_data and page_data.get("tournaments"):
            all_tournaments.extend(page_data["tournaments"])

    valid_tournaments = [t for t in all_tournaments if t.get('tournament_id')]
    logger.info(f"Found {len(valid_tournaments)} total tournaments. Beginning deep scrape...")
    
    # ---------------------------------------------------------
    # LEVEL 2, 3 & 4: DEEP TOURNAMENT PROCESSING
    # ---------------------------------------------------------
    for tourney in valid_tournaments[:150]: 
        t_id = tourney['tournament_id']
        t_name = tourney['name']
        
        # 1. Check if we already have this tournament
        if session.query(Tournament).filter_by(limitless_id=t_id).first():
            logger.info(f"⏩ Skipping '{t_name}' (Already in DB)")
            continue
            
        logger.info(f"--- Processing: {t_name} ---")
        
        try:
            # 2. Setup Format & Tournament Core
            fmt_id = tourney.get('format', 'Unknown')
            db_format, _ = get_or_create(session, Format, limitless_id=fmt_id, defaults={'name': fmt_id.upper()})
            
            db_tourney, _ = get_or_create(
                session, Tournament, limitless_id=t_id,
                defaults={
                    'name': t_name, 
                    'date': tourney.get('date'), 
                    'country_code': tourney.get('country'), 
                    'players_count': tourney.get('players'),
                    'format_id': db_format.id
                }
            )

            # 3. Extract Teams (Level 3) & Map by Rank
            teams_html = scraper.fetch_page(f"{scraper.base_url}/tournaments/{t_id}/teams")
            teams_data = scraper.parse_tournament_teams(teams_html)
            rank_to_team_details = {t['rank']: t['pokemon'] for t in teams_data if t['rank'] is not None}

            # 4. Extract Standings (Level 2)
            standings_html = scraper.fetch_page(f"{scraper.base_url}/tournaments/{t_id}")
            standings_data = scraper.parse_tournament_standings(standings_html)
            
            if standings_data and standings_data.get('standings'):
                for player_row in standings_data['standings']:
                    rank = player_row['rank']
                    p_id = player_row['player_id']
                    
                    if not p_id: continue 
                    
                    # Create Player
                    db_player, _ = get_or_create(
                        session, Player, limitless_id=p_id, 
                        defaults={'name': player_row['player_name'], 'country_code': player_row['country_code']}
                    )
                    
                    db_team = None
                    team_limitless_id = player_row['team_id']
                    
                    # 5. The Merge: Link Standings to specific Team Pokemon
                    if team_limitless_id:
                        db_team, _ = get_or_create(session, Team, limitless_team_id=team_limitless_id)
                        
                        # Check if we already populated this team's Pokemon
                        has_pokemon = session.query(TeamPokemon).filter_by(team_id=db_team.id).first()
                        
                        if not has_pokemon and rank in rank_to_team_details:
                            for poke in rank_to_team_details[rank]:
                                # Use our safe lookup for Species
                                db_species = get_or_create_species(session, poke['id'], poke['name'])
                                
                                # Dynamic creation for Items and Abilities
                                db_item = get_or_create(session, Item, name=poke['item'])[0] if poke['item'] else None
                                db_ability = get_or_create(session, Ability, name=poke['ability'])[0] if poke['ability'] else None
                                
                                db_tp = TeamPokemon(
                                    team_id=db_team.id,
                                    species_id=db_species.id,
                                    item_id=db_item.id if db_item else None,
                                    ability_id=db_ability.id if db_ability else None,
                                    tera_type=poke['tera_type']
                                )
                                session.add(db_tp)
                                session.flush()
                                
                                # Process Moves
                                added_move_ids = set()
                                for idx, move_name in enumerate(poke['moves']):
                                    if not move_name: continue
                                        
                                    db_move, _ = get_or_create(session, Move, name=move_name)
                                    if db_move.id not in added_move_ids:
                                        session.add(TeamPokemonMove(pokemon_id=db_tp.id, move_id=db_move.id, slot=idx+1))
                                        added_move_ids.add(db_move.id)

                    # Create the final Result Link
                    session.add(TournamentResult(
                        tournament_id=db_tourney.id,
                        player_id=db_player.id,
                        team_id=db_team.id if db_team else None,
                        rank=rank
                    ))

            # 6. Extract Metagame Statistics (Level 4)
            stats_html = scraper.fetch_page(f"{scraper.base_url}/tournaments/{t_id}/statistics")
            stats_data = scraper.parse_tournament_statistics(stats_html)
            
            for stat in stats_data:
                if not stat['pokemon_id']: continue
                db_species = get_or_create_species(session, stat['pokemon_id'], stat['pokemon_name'])
                
                # Strip '%' and convert to float
                share_val = float(str(stat['usage_share']).replace('%', '')) if stat['usage_share'] else 0.0
                
                session.add(TournamentMetagameStat(
                    tournament_id=db_tourney.id,
                    species_id=db_species.id,
                    usage_rank=stat['usage_rank'],
                    usage_count=stat['usage_count'],
                    usage_share_pct=share_val
                ))
                
            # SUCCESS: Commit the entire tournament's data
            session.commit() 
            logger.info(f"✅ Successfully committed {t_name}")
            
        except Exception as e:
            # FAILURE: Roll back so we don't store half-finished data
            session.rollback()
            logger.error(f"❌ Failed to process {t_name}. Rolling back transaction. Error: {e}")
            
        # Polite delay to respect LimitlessVGC's servers
        time.sleep(1.5)

    session.close()
    logger.info("=== PIPELINE EXECUTION COMPLETE ===")

if __name__ == "__main__":
    run_vgc_pipeline()