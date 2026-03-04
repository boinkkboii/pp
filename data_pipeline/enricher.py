import logging
import time
import requests
import re
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Import your database configuration and models
from config import Config
from database import Base, Move, Item, Ability

# --- LOGGING SETUP ---
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# --- DATABASE SETUP ---
engine = create_engine(Config.SQLALCHEMY_DATABASE_URI, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def slugify_for_pokeapi(name):
    """
    Translates LimitlessVGC names into PokeAPI slugs.
    E.g., "Will-O-Wisp" -> "will-o-wisp"
    E.g., "King's Rock" -> "kings-rock"
    """
    if not name: return ""
    name = name.lower()
    name = name.replace("'", "") # Remove apostrophes
    name = re.sub(r'[^a-z0-9\-]', ' ', name) # Replace weird chars with spaces
    name = re.sub(r'\s+', '-', name.strip()) # Replace spaces with hyphens
    
    # Handle specific PokeAPI edge cases manually if needed
    overrides = {
        "as-one-glastrier": "as-one",
        "as-one-spectrier": "as-one",
        "protect": "protect" # Just ensuring standard moves work
    }
    return overrides.get(name, name)

def extract_english_flavor_text(entries):
    """Finds the first English description and cleans up the weird newline characters."""
    for entry in entries:
        if entry.get('language', {}).get('name') == 'en':
            text = entry.get('flavor_text', '')
            # PokeAPI flavor text is notorious for random \n and \f characters
            return text.replace('\n', ' ').replace('\f', ' ').strip()
    return "Description not found."

def enrich_moves(session):
    # Find all moves that haven't been enriched yet (assuming type is None if unenriched)
    # If your database model uses 'description' instead of 'type' to track this, change the filter!
    unenriched_moves = session.query(Move).filter(Move.type == None).all()
    logger.info(f"Found {len(unenriched_moves)} Moves to enrich...")
    
    for move in unenriched_moves:
        slug = slugify_for_pokeapi(move.name)
        url = f"https://pokeapi.co/api/v2/move/{slug}/"
        
        try:
            res = requests.get(url)
            if res.status_code == 200:
                data = res.json()
                
                # Update the database object
                move.type = data['type']['name'].capitalize()
                move.category = data['damage_class']['name'].capitalize()
                move.base_power = data.get('power') or 0
                move.accuracy = data.get('accuracy') or 0
                move.description = extract_english_flavor_text(data.get('flavor_text_entries', []))
                
                logger.info(f"✅ Enriched Move: {move.name}")
            else:
                logger.warning(f"❌ PokeAPI 404: Could not find Move '{slug}' (Original: {move.name})")
                
        except Exception as e:
            logger.error(f"Error processing move {move.name}: {e}")
            
        time.sleep(0.5) # Polite rate limiting
    
    session.commit()

def enrich_items(session):
    unenriched_items = session.query(Item).filter(Item.description == None).all()
    logger.info(f"Found {len(unenriched_items)} Items to enrich...")
    
    for item in unenriched_items:
        slug = slugify_for_pokeapi(item.name)
        url = f"https://pokeapi.co/api/v2/item/{slug}/"
        
        try:
            res = requests.get(url)
            if res.status_code == 200:
                data = res.json()
                item.description = extract_english_flavor_text(data.get('flavor_text_entries', []))
                logger.info(f"✅ Enriched Item: {item.name}")
            else:
                logger.warning(f"❌ PokeAPI 404: Could not find Item '{slug}'")
                
        except Exception as e:
            logger.error(f"Error processing item {item.name}: {e}")
            
        time.sleep(0.5)
        
    session.commit()

def enrich_abilities(session):
    unenriched_abilities = session.query(Ability).filter(Ability.description == None).all()
    logger.info(f"Found {len(unenriched_abilities)} Abilities to enrich...")
    
    for ability in unenriched_abilities:
        slug = slugify_for_pokeapi(ability.name)
        url = f"https://pokeapi.co/api/v2/ability/{slug}/"
        
        try:
            res = requests.get(url)
            if res.status_code == 200:
                data = res.json()
                ability.description = extract_english_flavor_text(data.get('flavor_text_entries', []))
                logger.info(f"✅ Enriched Ability: {ability.name}")
            else:
                logger.warning(f"❌ PokeAPI 404: Could not find Ability '{slug}'")
                
        except Exception as e:
            logger.error(f"Error processing ability {ability.name}: {e}")
            
        time.sleep(0.5)
        
    session.commit()

def run_enrichment_pipeline():
    logger.info("=== STARTING POKEAPI ENRICHMENT PIPELINE ===")
    session = SessionLocal()
    
    try:
        enrich_moves(session)
        enrich_items(session)
        enrich_abilities(session)
        logger.info("=== ENRICHMENT COMPLETE ===")
    except Exception as e:
        session.rollback()
        logger.error(f"Pipeline crashed. Rolled back changes. Error: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    run_enrichment_pipeline()