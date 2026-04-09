import os
import requests
import time
import logging
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type
from backend.models import Species
from backend.database import SessionLocal, engine
from requests.exceptions import RequestException # Tenacity needs to know what errors to catch

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- TRANSLATION DICTIONARY ---
SLUG_OVERRIDES = {}

def get_clean_name(pokeapi_slug):
    """Converts a slug like 'flutter-mane' to 'Flutter Mane'."""
    words = pokeapi_slug.split('-')
    return ' '.join(word.capitalize() for word in words)

def load_corrections_from_file(filename="corrections.txt"):
    """Reads the user's manual corrections from the text file reliably."""
    corrections = {}
    
    # Use an absolute path if running from root, or relative if in the same folder
    filepath = os.path.join("data_pipeline", filename)
    if not os.path.exists(filepath):
        # Fallback in case script is run directly from inside the data_pipeline folder
        filepath = filename
        if not os.path.exists(filepath):
            return corrections
            
    with open(filepath, "r") as f:
        for line in f:
            if "->" in line:
                parts = line.split("->")
                left_side = parts[0].split(":")[-1].strip()
                right_side = parts[1].split(":")[-1].strip()
                if right_side:
                    corrections[left_side] = right_side
                    
    return corrections

# ====================================================================
# ISOLATED RETRY LOGIC
# We wrap the specific API calls, not the entire loop!
# ====================================================================
@retry(
    wait=wait_exponential(multiplier=1, min=2, max=10), 
    stop=stop_after_attempt(5),
    retry=retry_if_exception_type(RequestException) # Only retry on network errors!
)
def fetch_pokeapi_json(url):
    response = requests.get(url, timeout=10) # Added timeout to prevent hanging
    response.raise_for_status() # If 404/500/429, this throws RequestException, triggering a retry
    return response.json()

@retry(
    wait=wait_exponential(multiplier=1, min=2, max=10), 
    stop=stop_after_attempt(3),
    retry=retry_if_exception_type(RequestException)
)
def check_limitless_status(limitless_id):
    limitless_url = f"https://limitlessvgc.com/pokemon/{limitless_id}"
    verify_res = requests.get(limitless_url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
    
    # 404 is a VALID response from Limitless (it means they don't track that Pokemon).
    # We only want to retry on real server crashes (500s) or Rate Limits (429s).
    if verify_res.status_code in [429, 500, 502, 503, 504]:
        verify_res.raise_for_status() 
        
    return verify_res.status_code

# ====================================================================
# MAIN SCRIPT
# ====================================================================
def run_seeder():
    session = SessionLocal()
    logger.info("=== STARTING POKEAPI DATABASE SEEDER ===")
    
    file_overrides = load_corrections_from_file("corrections.txt")
    SLUG_OVERRIDES.update(file_overrides) 
    
    # Use a dynamic path so it doesn't crash based on where you run the command
    failed_slugs_path = os.path.join("data_pipeline", "failed_slugs.txt")
    if not os.path.exists("data_pipeline"): failed_slugs_path = "failed_slugs.txt"

    with open(failed_slugs_path, "w") as f:
        f.write("--- Failed Limitless Translations ---\n")
        
    url = "https://pokeapi.co/api/v2/pokemon?limit=5000&offset=0"
    
    try:
        data = fetch_pokeapi_json(url)
        pokemon_list = data.get('results', [])
    except Exception as e:
        logger.error(f"Failed to connect to PokeAPI completely. Aborting. {e}")
        return

    logger.info(f"Found {len(pokemon_list)} Pokémon/Forms to process.")

    count = 0
    for poke_ref in pokemon_list:
        pokeapi_slug = poke_ref['name']
        detail_url = poke_ref['url']
        limitless_id = SLUG_OVERRIDES.get(pokeapi_slug, pokeapi_slug)
        
        if limitless_id == "IGNORE":
            continue

        existing = session.query(Species).filter_by(limitless_id=limitless_id).first()
        if existing and existing.type_1 != "Unknown":
            continue
            
        try:
            # Safely ping Limitless with built-in retry logic
            status = check_limitless_status(limitless_id)
            
            if status == 404:
                logger.warning(f"❌ 404 Not Found: Limitless rejects '{limitless_id}'")
                with open(failed_slugs_path, "a") as f:
                    f.write(f"PokeAPI: {pokeapi_slug} -> Limitless ID: {limitless_id}\n")
                continue
            
            elif status != 200:
                logger.warning(f"⚠️ Unexpected status {status} for {limitless_id}. Skipping.")
                continue
            
            # Safely fetch PokeAPI stats with built-in retry logic
            data = fetch_pokeapi_json(detail_url)
            
            types = data.get('types', [])
            type_1 = types[0]['type']['name'].capitalize() if len(types) > 0 else "Normal"
            type_2 = types[1]['type']['name'].capitalize() if len(types) > 1 else None
            
            stats = {stat['stat']['name']: stat['base_stat'] for stat in data.get('stats', [])}

            if existing and existing.type_1 == "Unknown":
                existing.pokedex_number = data.get('id')
                existing.name = get_clean_name(limitless_id)
                existing.type_1 = type_1
                existing.type_2 = type_2
                existing.base_hp = stats.get('hp', 0)
                existing.base_atk = stats.get('attack', 0)
                existing.base_def = stats.get('defense', 0)
                existing.base_spa = stats.get('special-attack', 0)
                existing.base_spd = stats.get('special-defense', 0)
                existing.base_spe = stats.get('speed', 0)
                logger.info(f"🦴 Upgraded Skeleton: {limitless_id}")
            else:
                new_species = Species(
                    pokedex_number=data.get('id'),
                    limitless_id=limitless_id,
                    name=get_clean_name(limitless_id),
                    type_1=type_1, type_2=type_2,
                    base_hp=stats.get('hp', 0), base_atk=stats.get('attack', 0),
                    base_def=stats.get('defense', 0), base_spa=stats.get('special-attack', 0),
                    base_spd=stats.get('special-defense', 0), base_spe=stats.get('speed', 0)
                )
                session.add(new_species)
                logger.info(f"✅ Seeded: {limitless_id}")
                count += 1
            
            if count > 0 and count % 50 == 0:
                session.commit()
                
        except RequestException as e:
            # If Tenacity gives up after 5 tries, we catch it here and skip the pokemon
            logger.error(f"Network failure for {pokeapi_slug} after all retries. Skipping. Error: {e}")
        except Exception as e:
            logger.error(f"Database/Parsing logic failed for {pokeapi_slug}: {e}")
            
        time.sleep(1) # Keep the polite delay to avoid getting banned!

    session.commit()
    session.close()
    logger.info(f"=== SEEDING COMPLETE: {count} new Pokémon added. ===")

if __name__ == "__main__":
    run_seeder()