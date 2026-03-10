import os
import requests
import time
import logging
from sqlalchemy.orm import sessionmaker

from config import Config
from database import Base, Species, SessionLocal, engine

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- TRANSLATION DICTIONARY ---
SLUG_OVERRIDES = {}

def get_clean_name(pokeapi_slug):
    """Converts a slug like 'flutter-mane' to 'Flutter Mane'."""
    words = pokeapi_slug.split('-')
    return ' '.join(word.capitalize() for word in words)

import os

def load_corrections_from_file(filename="corrections.txt"):
    """Reads the user's manual corrections from the text file reliably."""
    corrections = {}
    if not os.path.exists(filename):
        return corrections
        
    with open(filename, "r") as f:
        for line in f:
            if "->" in line:
                parts = line.split("->")
                
                # Left side looks like "PokeAPI: deoxys-normal "
                # Splitting by ":" and taking the last part ensures we just get "deoxys-normal"
                left_side = parts[0].split(":")[-1].strip()
                
                # Right side looks like " Attempted Limitless ID: deoxys" or just " IGNORE"
                right_side = parts[1].split(":")[-1].strip()
                
                # If you wrote something on the right side, save it to our dictionary
                if right_side:
                    corrections[left_side] = right_side
                    
    return corrections

def run_seeder():
    session = SessionLocal()
    logger.info("=== STARTING POKEAPI DATABASE SEEDER ===")
    
    # Load text file corrections from failed_slugs.txt
    file_overrides = load_corrections_from_file("data_pipeline/corrections.txt")
    SLUG_OVERRIDES.update(file_overrides) 
    # ---------------------------------------------
    
    # Initialize our failure log for the NEW run
    with open("data_pipeline/failed_slugs.txt", "w") as f:
        f.write("--- Failed Limitless Translations ---\n")
    url = "https://pokeapi.co/api/v2/pokemon?limit=100000&offset=0"
    response = requests.get(url)
    
    if response.status_code != 200:
        logger.error("Failed to connect to PokeAPI.")
        return

    pokemon_list = response.json().get('results', [])
    logger.info(f"Found {len(pokemon_list)} Pokémon/Forms to process.")

    count = 0
    for poke_ref in pokemon_list:
        pokeapi_slug = poke_ref['name']
        detail_url = poke_ref['url']
        
        limitless_id = SLUG_OVERRIDES.get(pokeapi_slug, pokeapi_slug)
        
        # Skips cosmetic/form changes marked as IGNORE
        if limitless_id == "IGNORE":
            continue

        # 1. Skip if already in DB
        existing = session.query(Species).filter_by(limitless_id=limitless_id).first()
        if existing and existing.type_1 != "Unknown":
            continue
            
        try:
            # Ping LimitlessVGC to see if the URL exists
            limitless_url = f"https://limitlessvgc.com/pokemon/{limitless_id}"
            verify_res = requests.get(limitless_url, headers={'User-Agent': 'Mozilla/5.0'})
            
            if verify_res.status_code == 404:
                logger.warning(f"❌ 404 Not Found: Limitless rejects '{limitless_id}' (PokeAPI: '{pokeapi_slug}')")
                # Log it to our text file for manual review later
                with open("data_pipeline/failed_slugs.txt", "a") as f:
                    f.write(f"PokeAPI: {pokeapi_slug} -> Limitless ID: {limitless_id}\n")
                
                # Polite delay before skipping to the next Pokemon
                time.sleep(0.5)
                continue
            
            elif verify_res.status_code != 200:
                logger.warning(f"⚠️ Unexpected status {verify_res.status_code} for {limitless_id}. Skipping.")
                time.sleep(0.5)
                continue
            # --------------------------------
            
            # 2. If Limitless returns 200 OK, fetch the actual stats from PokeAPI
            res = requests.get(detail_url)
            if res.status_code != 200:
                continue
                
            data = res.json()
            
            types = data.get('types', [])
            type_1 = types[0]['type']['name'].capitalize() if len(types) > 0 else "Normal"
            type_2 = types[1]['type']['name'].capitalize() if len(types) > 1 else None
            
            stats = {stat['stat']['name']: stat['base_stat'] for stat in data.get('stats', [])}

            if existing and existing.type_1 == "Unknown":
                # Update any existing skeleton
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
                
                logger.info(f"🦴 Upgraded Skeleton to Full Data: {limitless_id}")
            else:
                # INSERT BRAND NEW POKEMON
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
                logger.info(f"✅ Verified & Seeded: {limitless_id}")
            
            if count % 50 == 0:
                session.commit()
                
        except Exception as e:
            logger.error(f"Failed to process {pokeapi_slug}: {e}")
            
        # We are now hitting TWO APIs (PokeAPI and Limitless). 
        # A 1-second delay is highly recommended so neither site bans your IP.
        time.sleep(1)

    session.commit()
    session.close()
    logger.info(f"=== SEEDING COMPLETE: {count} Pokémon added. Check failed_slugs.txt for errors. ===")

if __name__ == "__main__":
    # Ensure tables exist before seeding
    Base.metadata.create_all(bind=engine)
    run_seeder()