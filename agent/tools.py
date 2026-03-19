import requests
import logging

logger = logging.getLogger(__name__)
BASE_URL = "http://localhost:8000/api"

# =====================================================================
# CATEGORY 1: THE ENCYCLOPEDIA (Fact-Checking)
# =====================================================================

def get_pokemon_stats(species_name: str) -> dict:
    """
    Fetches the static encyclopedia data for a specific Pokémon.
    Use this to check a Pokémon's base stats (HP, Attack, Speed, etc.) and exact typings.
    
    Args:
        species_name: The name of the Pokémon (e.g., 'Flutter Mane', 'Incineroar').
    """
    logger.info(f"🔧 Tool: Fetching stats for {species_name}")
    try:
        response = requests.get(f"{BASE_URL}/encyclopedia/pokemon/{species_name}")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def get_move_details(move_name: str) -> dict:
    """
    Fetches the mechanical details of a specific Pokémon move.
    Use this to verify a move's Type, Category (Physical/Special/Status), Base Power, and Accuracy.
    
    Args:
        move_name: The name of the move (e.g., 'Extreme Speed', 'Astral Barrage').
    """
    logger.info(f"🔧 Tool: Fetching move details for {move_name}")
    try:
        response = requests.get(f"{BASE_URL}/encyclopedia/moves/{move_name}")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def get_item_ability_details(name: str, item_or_ability: str) -> dict:
    """
    Fetches the mechanical description of a specific Item or Ability.
    
    Args:
        name: The name of the item or ability (e.g., 'Choice Specs', 'Intimidate').
        item_or_ability: Must be exactly 'item' or 'ability'.
    """
    logger.info(f"🔧 Tool: Fetching {item_or_ability} details for {name}")
    try:
        response = requests.get(f"{BASE_URL}/encyclopedia/{item_or_ability}s/{name}")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}

# =====================================================================
# CATEGORY 2: EVENT DISCOVERY
# =====================================================================

def get_recent_tournaments(limit: int = 5) -> list:
    """
    Fetches a list of the most recent VGC tournaments stored in the database.
    Use this proactively when a user asks about the 'current meta' to find the latest tournament ID.
    
    Args:
        limit: The number of recent tournaments to retrieve. Defaults to 5.
    """
    logger.info(f"🔧 Tool: Fetching {limit} recent tournaments")
    try:
        response = requests.get(f"{BASE_URL}/tournaments/?limit={limit}")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return [{"error": str(e)}]

def search_tournaments(query: str) -> list:
    """
    Searches the database for tournaments matching a specific name or location.
    Use this to find the ID of a specific historical event.
    
    Args:
        query: The search term (e.g., 'Orlando', 'EUIC', 'World Championship').
    """
    logger.info(f"🔧 Tool: Searching tournaments for '{query}'")
    try:
        response = requests.get(f"{BASE_URL}/tournaments/search", params={"q": query})
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return [{"error": str(e)}]

def search_player_history(player_name: str) -> list:
    """
    Fetches the tournament history and placements for a specific human player.
    
    Args:
        player_name: The name of the player.
    """
    logger.info(f"🔧 Tool: Fetching history for player '{player_name}'")
    try:
        response = requests.get(f"{BASE_URL}/players/{player_name}/history")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return [{"error": str(e)}]

# =====================================================================
# CATEGORY 3: MICRO ANALYSIS (Specific Tournaments)
# =====================================================================

def get_tournament_meta(tournament_id: str) -> list:
    """
    Fetches the overall metagame statistics (usage percentages) for a single tournament.
    
    Args:
        tournament_id: The LimitlessVGC identifier for the tournament (e.g., '421').
    """
    logger.info(f"🔧 Tool: Fetching meta stats for tournament {tournament_id}")
    try:
        response = requests.get(f"{BASE_URL}/tournaments/{tournament_id}/meta")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return [{"error": str(e)}]

def get_tournament_teams(tournament_id: str) -> list:
    """
    Fetches the exact 6-Pokémon teams (including items, abilities, and moves) 
    used by the top-cut players at a specific tournament.
    
    Args:
        tournament_id: The LimitlessVGC identifier for the tournament.
    """
    logger.info(f"🔧 Tool: Fetching player teams for tournament {tournament_id}")
    try:
        response = requests.get(f"{BASE_URL}/tournaments/{tournament_id}/teams")
        response.raise_for_status()
        data = response.json()
        return data[:25]
    except Exception as e:
        return [{"error": str(e)}]

# =====================================================================
# CATEGORY 4: MACRO ANALYSIS (Time & Format Aggregation)
# =====================================================================

def get_format_meta(format_limitless_id: str) -> list:
    """
    Fetches the aggregated usage statistics across an entire ruleset/format, 
    combining data from all tournaments played under those rules.
    
    Args:
        format_limitless_id: The format identifier (e.g., 'svi', 'RegG', 'RegH').
    """
    logger.info(f"🔧 Tool: Fetching aggregated meta for format {format_limitless_id}")
    try:
        response = requests.get(f"{BASE_URL}/formats/{format_limitless_id}/meta")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return [{"error": str(e)}]

def get_historical_meta(months: int) -> list:
    """
    Fetches the aggregated usage statistics for the entire metagame over the last X months.
    
    Args:
        months: The number of recent months to aggregate (e.g., 3, 6, 12).
    """
    logger.info(f"🔧 Tool: Fetching historical meta for the last {months} months")
    try:
        response = requests.get(f"{BASE_URL}/meta/history", params={"months": months})
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return [{"error": str(e)}]

# =====================================================================
# CATEGORY 5: TEAMBUILDING & SYNERGY
# =====================================================================

def get_common_teammates(species_name: str, format_id: str = None) -> list:
    """
    Finds the most common teammates played alongside a specific Pokémon.
    Use this to analyze team synergy and build team cores.
    
    Args:
        species_name: The core Pokémon you are building around (e.g., 'Miraidon').
        format_id: (Optional) The specific format to filter by.
    """
    logger.info(f"🔧 Tool: Fetching common teammates for {species_name}")
    try:
        params = {"format": format_id} if format_id else {}
        response = requests.get(f"{BASE_URL}/synergy/{species_name}/teammates", params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return [{"error": str(e)}]

def get_pokemon_standard_build(species_name: str, format_id: str = None) -> dict:
    """
    Fetches the most commonly used Items, Abilities, Tera Types, and Moves 
    for a specific Pokémon to determine its 'standard' meta build.
    
    Args:
        species_name: The Pokémon to analyze.
        format_id: (Optional) The specific format to filter by.
    """
    logger.info(f"🔧 Tool: Fetching standard build for {species_name}")
    try:
        params = {"format": format_id} if format_id else {}
        response = requests.get(f"{BASE_URL}/synergy/{species_name}/build", params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def get_move_users(move_name: str, format_id: str = None) -> list:
    """
    Finds which Pokémon are most frequently running a specific move in the current meta.
    Use this when a team needs a specific utility move (like 'Wide Guard' or 'Tailwind').
    
    Args:
        move_name: The move to search for.
        format_id: (Optional) The specific format to filter by.
    """
    logger.info(f"🔧 Tool: Fetching top users of the move {move_name}")
    try:
        params = {"format": format_id} if format_id else {}
        response = requests.get(f"{BASE_URL}/synergy/moves/{move_name}/users", params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return [{"error": str(e)}]