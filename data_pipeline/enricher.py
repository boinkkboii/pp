import logging
import time
import requests
import re
from sqlalchemy import create_engine, or_
from sqlalchemy.orm import sessionmaker
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type
from requests.exceptions import RequestException

# Import your database configuration and models
from backend.core.config import Config
from backend.models import Base, Move, Item, Ability, Species
from backend.database import SessionLocal, engine

# --- LOGGING SETUP ---
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

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
        "sword-dance": "swords-dance",     # Fix Limitless typo
        "roar-of-time": "roar-of-time",
        "as-one-glastrier": "as-one",
        "as-one-spectrier": "as-one",
    }
    return overrides.get(name, name)

def extract_competitive_effect(data):
    """
    Tries to find the hard mechanical description in 'effect_entries' first.
    If the item/move is too new (Gen 9), falls back to 'flavor_text_entries'.
    Returns "NA" if neither exists, enabling a Retry Queue.
    """
    # 1. First Priority: The hard mechanical effect
    for entry in data.get('effect_entries', []):
        if entry.get('language', {}).get('name') == 'en':
            effect = entry.get('short_effect') or entry.get('effect')
            if effect:
                return effect.replace('\n', ' ').replace('\f', ' ').strip()
                
    # 2. Second Priority: The Gen 9 Fallback (In-game text)
    for entry in data.get('flavor_text_entries', []):
        if entry.get('language', {}).get('name') == 'en':
            text = entry.get('flavor_text')
            if text:
                return text.replace('\n', ' ').replace('\f', ' ').strip()
                
    return "NA"

# ====================================================================
# ISOLATED RETRY LOGIC
# ====================================================================
@retry(
    wait=wait_exponential(multiplier=1, min=2, max=10), 
    stop=stop_after_attempt(5),
    retry=retry_if_exception_type(RequestException)
)
def fetch_pokeapi_enrichment(url):
    res = requests.get(url, timeout=10)
    res.raise_for_status() 
    return res.json()

# ====================================================================
# ENRICHMENT PIPELINE
# ====================================================================
def enrich_moves(session):
    unenriched_moves = session.query(Move).filter(
        or_(Move.type == None, Move.description == "NA")
    ).all()
    logger.info(f"Found {len(unenriched_moves)} Moves to enrich...")
    
    for move in unenriched_moves:
        slug = slugify_for_pokeapi(move.name)
        url = f"https://pokeapi.co/api/v2/move/{slug}/"
        
        try:
            data = fetch_pokeapi_enrichment(url)
            
            # Update the database object
            move.type = data['type']['name'].capitalize()
            move.category = data['damage_class']['name'].capitalize()
            move.base_power = data.get('power') or 0
            move.accuracy = data.get('accuracy') or 0
            move.description = extract_competitive_effect(data)
            
            logger.info(f"✅ Enriched Move: {move.name}")
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                logger.warning(f"❌ PokeAPI 404: Could not find Move '{slug}' (Original: {move.name})")
            else:
                logger.error(f"HTTP Error processing move {move.name}: {e}")
        except RequestException as e:
            logger.error(f"Network failure for move {move.name} after retries: {e}")
        except Exception as e:
            logger.error(f"Logic Error processing move {move.name}: {e}")
            
        time.sleep(0.5) 
    
    session.commit()

def enrich_items(session):
    unenriched_items = session.query(Item).filter(
        or_(Item.description == None, Item.description == "NA")
    ).all()
    logger.info(f"Found {len(unenriched_items)} Items to enrich...")
    
    for item in unenriched_items:
        slug = slugify_for_pokeapi(item.name)
        url = f"https://pokeapi.co/api/v2/item/{slug}/"
        
        try:
            data = fetch_pokeapi_enrichment(url)
            item.description = extract_competitive_effect(data)
            logger.info(f"✅ Enriched Item: {item.name}")
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                logger.warning(f"❌ PokeAPI 404: Could not find Item '{slug}'")
            else:
                logger.error(f"HTTP Error processing item {item.name}: {e}")
        except RequestException as e:
            logger.error(f"Network failure for item {item.name} after retries: {e}")
        except Exception as e:
            logger.error(f"Logic Error processing item {item.name}: {e}")
            
        time.sleep(0.5)
        
    session.commit()

def enrich_abilities(session):
    unenriched_abilities = session.query(Ability).filter(
        or_(Ability.description == None, Ability.description == "NA")
    ).all()
    logger.info(f"Found {len(unenriched_abilities)} Abilities to enrich...")
    
    for ability in unenriched_abilities:
        slug = slugify_for_pokeapi(ability.name)
        url = f"https://pokeapi.co/api/v2/ability/{slug}/"
        
        try:
            data = fetch_pokeapi_enrichment(url)
            ability.description = extract_competitive_effect(data)
            logger.info(f"✅ Enriched Ability: {ability.name}")
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                logger.warning(f"❌ PokeAPI 404: Could not find Ability '{slug}'")
            else:
                logger.error(f"HTTP Error processing ability {ability.name}: {e}")
        except RequestException as e:
            logger.error(f"Network failure for ability {ability.name} after retries: {e}")
        except Exception as e:
            logger.error(f"Logic Error processing ability {ability.name}: {e}")
            
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