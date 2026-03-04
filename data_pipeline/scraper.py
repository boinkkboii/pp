import requests
from bs4 import BeautifulSoup
import logging
import re

logger = logging.getLogger(__name__)

class VGCScraper:
    def __init__(self):
        self.base_url = "https://limitlessvgc.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def fetch_page(self, url):
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                return response.text
            else:
                logger.warning(f"Failed to fetch {url}. Status code: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            return None

    def _safe_int(self, value, default=0):
        if not value: return default
        try:
            # Removes any non-numeric characters (like '1st' -> 1)
            return int(re.sub(r'[^\d-]', '', str(value)))
        except ValueError:
            return default

    # =========================================================================
    # LEVEL 1: MASTER TOURNAMENT LIST
    # =========================================================================
    def parse_tournament_list(self, html_content):
        if not html_content: return {}
        soup = BeautifulSoup(html_content, 'html.parser')
        
        data = {'tournaments': [], 'pagination': {'max_page': 1}}
        
        # 1. Parse Max Page directly from the data-max attribute!
        pagination = soup.find('ul', class_='pagination')
        if pagination and pagination.has_attr('data-max'):
            data['pagination']['max_page'] = self._safe_int(pagination['data-max'], default=1)

        # 2. Parse Tournaments from the tr data-attributes
        table = soup.find('table', class_='completed-tournaments')
        if not table:
            return data
            
        for row in table.find_all('tr'):
            if not row.has_attr('data-date'): # Skip header rows
                continue
                
            try:
                link_tag = row.find('a', href=lambda h: h and '/tournaments/' in h)
                if not link_tag: continue
                
                t_id = link_tag['href'].split('/')[-1] # Extract ID from href
                
                data['tournaments'].append({
                    'tournament_id': t_id,
                    'name': row.get('data-name', 'Unknown'),
                    'date': row.get('data-date'),
                    'format': row.get('data-format'),
                    'players': self._safe_int(row.get('data-players')),
                    'country': row.get('data-country')
                })
            except Exception as e:
                logger.warning(f"Failed to parse tournament row: {e}")
                
        return data

    # =========================================================================
    # LEVEL 2: SPECIFIC TOURNAMENT STANDINGS
    # =========================================================================
    def parse_tournament_standings(self, html_content):
        if not html_content: return {}
        soup = BeautifulSoup(html_content, 'html.parser')
        
        standings_data = {'standings': []}
        table = soup.find('table', class_='data-table')
        
        if not table:
            return standings_data
            
        for row in table.find_all('tr'):
            # Valid player rows always have data-rank
            if not row.has_attr('data-rank'): 
                continue 
                
            try:
                rank = self._safe_int(row['data-rank'])
                player_name = row.get('data-name', 'Unknown')
                country_code = row.get('data-country')
                
                # ID extraction
                player_id = None
                player_link = row.find('a', href=lambda h: h and '/players/' in h)
                if player_link:
                    player_id = player_link['href'].split('/')[-1]
                    
                # Team ID extraction
                team_id = None
                team_link = row.find('a', href=lambda h: h and '/teams/' in h)
                if team_link:
                    team_id = team_link['href'].split('/')[-1]
                
                standings_data['standings'].append({
                    'rank': rank,
                    'player_name': player_name,
                    'player_id': player_id,
                    'country_code': country_code,
                    'team_id': team_id
                })
            except Exception as e:
                logger.warning(f"Failed to parse a standings row: {e}")
                
        return standings_data

    # =========================================================================
    # LEVEL 3: TOURNAMENT TEAMS LIST
    # =========================================================================
    def parse_tournament_teams(self, html_content):
        if not html_content: return []
        soup = BeautifulSoup(html_content, 'html.parser')
        teams_list = []
        
        # Limitless uses 'tournament-decklist' as the wrapper for each team
        decklists = soup.find_all('div', class_='tournament-decklist')
        
        for deck in decklists:
            try:
                # 1. Grab the rank (e.g., "1st Carson St Denis")
                header = deck.find('div', class_='teamlist-toggle')
                if not header: continue
                
                rank_text = header.text.strip().split(' ')[0]
                rank = self._safe_int(rank_text)
                
                pokemon_list = []
                
                # 2. Iterate through the 6 pokemon slots
                pokes = deck.find_all('div', class_='pkmn')
                for poke in pokes:
                    # Beautiful: Limitless puts the ID directly in a data tag!
                    poke_id = poke.get('data-id') 
                    
                    name_tag = poke.find('div', class_='name')
                    poke_name = name_tag.text.strip() if name_tag else "Unknown"
                    
                    details = poke.find('div', class_='details')
                    item = None
                    ability = None
                    tera_type = None
                    
                    if details:
                        # Item Check (handles empty items correctly)
                        item_tag = details.find('div', class_='item')
                        if item_tag:
                            item = item_tag.text.strip()
                            if item == "Held Item:": item = None 
                            
                        # Ability Check (Strips "Ability: " prefix)
                        ability_tag = details.find('div', class_='ability')
                        if ability_tag:
                            ability = ability_tag.text.replace('Ability:', '').strip()
                            
                        # Tera Check (Strips "Tera Type: " prefix)
                        tera_tag = details.find('div', class_='tera')
                        if tera_tag:
                            tera_type = tera_tag.text.replace('Tera Type:', '').strip()
                            
                    # Moves Check
                    moves = []
                    moves_list = poke.find('ul', class_='moves')
                    if moves_list:
                        for li in moves_list.find_all('li'):
                            move_name = li.text.strip()
                            if move_name:
                                moves.append(move_name)
                                
                    pokemon_list.append({
                        'id': poke_id,
                        'name': poke_name,
                        'item': item,
                        'ability': ability,
                        'tera_type': tera_type,
                        'moves': moves
                    })
                    
                teams_list.append({
                    'rank': rank,
                    'pokemon': pokemon_list
                })
                
            except Exception as e:
                logger.warning(f"Failed to parse a team block: {e}")
                
        return teams_list

    # =========================================================================
    # LEVEL 4: TOURNAMENT STATISTICS
    # =========================================================================
    def parse_tournament_statistics(self, html_content):
        if not html_content: return []
        soup = BeautifulSoup(html_content, 'html.parser')
        
        stats = []
        table = soup.find('table', class_='data-table')
        if not table:
            return stats
            
        for row in table.find_all('tr'):
            # Valid stats rows always have data-count
            if not row.has_attr('data-count'):
                continue
                
            try:
                cols = row.find_all('td')
                if len(cols) < 5: continue
                
                usage_rank = self._safe_int(cols[0].text)
                
                link_tag = cols[2].find('a')
                if not link_tag: continue
                
                pokemon_id = link_tag['href'].split('/')[-1]
                pokemon_name = link_tag.text.strip()
                
                # Safely get properties from data attributes where possible
                usage_count = self._safe_int(row.get('data-count'))
                points = self._safe_int(row.get('data-points'))
                
                # Landscape only table column holds the percentage
                share_text = cols[4].text.strip()
                
                stats.append({
                    'usage_rank': usage_rank,
                    'pokemon_id': pokemon_id,
                    'pokemon_name': pokemon_name,
                    'usage_count': usage_count,
                    'usage_share': share_text,
                    'points': points
                })
                
            except Exception as e:
                logger.warning(f"Failed to parse a statistics row: {e}")
                
        return stats