import requests
from bs4 import BeautifulSoup
import logging
import re
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type
from requests.exceptions import RequestException

logger = logging.getLogger(__name__)

class VGCScraper:
    def __init__(self):
        self.base_url = "https://limitlessvgc.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    # Added Tenacity retry logic to protect against LimitlessVGC Rate Limits (429s) or Server Drops
    @retry(
        wait=wait_exponential(multiplier=1, min=2, max=10), 
        stop=stop_after_attempt(5),
        retry=retry_if_exception_type(RequestException)
    )
    def fetch_page(self, url):
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status() # Force an error on 404, 500, or 429
            return response.text
        except requests.exceptions.HTTPError as e:
            # If the page genuinely doesn't exist (404), don't retry endlessly. Just return None.
            if e.response.status_code == 404:
                logger.warning(f"404 Not Found: {url}")
                return None
            raise e # Let Tenacity catch 500s and 429s and retry
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            raise e # Trigger the retry

    def _safe_int(self, value, default=0):
        if not value: return default
        try:
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
        
        pagination = soup.find('ul', class_='pagination')
        if pagination and pagination.has_attr('data-max'):
            data['pagination']['max_page'] = self._safe_int(pagination['data-max'], default=1)

        table = soup.find('table', class_='completed-tournaments')
        if not table:
            return data
            
        for row in table.find_all('tr'):
            if not row.has_attr('data-date'):
                continue
                
            try:
                link_tag = row.find('a', href=lambda h: h and '/tournaments/' in h)
                if not link_tag: continue
                
                t_id = link_tag['href'].split('/')[-1] 
                
                data['tournaments'].append({
                    'tournament_id': t_id,
                    'name': row.get('data-name', 'Unknown'),
                    'date': row.get('data-date'),
                    'format': row.get('data-format'),
                    'players': self._safe_int(row.get('data-players')),
                    'country': row.get('data-country')
                })
            except Exception as e:
                logger.warning(f"Failed to parse tournament row. Skipping row. Error: {e}")
                
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
            if not row.has_attr('data-rank'): 
                continue 
                
            try:
                rank = self._safe_int(row['data-rank'])
                player_name = row.get('data-name', 'Unknown')
                country_code = row.get('data-country')
                
                player_id = None
                player_link = row.find('a', href=lambda h: h and '/players/' in h)
                if player_link:
                    player_id = player_link['href'].split('/')[-1]
                    
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
                logger.warning(f"Failed to parse a standings row for {player_name}. Error: {e}")
                
        return standings_data

    # =========================================================================
    # LEVEL 3: TOURNAMENT TEAMS LIST
    # =========================================================================
    def parse_tournament_teams(self, html_content):
        if not html_content: return []
        soup = BeautifulSoup(html_content, 'html.parser')
        teams_list = []
        
        decklists = soup.find_all('div', class_='tournament-decklist')
        
        for deck in decklists:
            try:
                header = deck.find('div', class_='teamlist-toggle')
                if not header: continue
                
                rank_text = header.text.strip().split(' ')[0]
                rank = self._safe_int(rank_text)
                pokemon_list = []
                
                pokes = deck.find_all('div', class_='pkmn')
                for poke in pokes:
                    # INNER TRY/CATCH: Protects the team if a single Pokemon is malformed!
                    try:
                        poke_id = poke.get('data-id') 
                        name_tag = poke.find('div', class_='name')
                        poke_name = name_tag.text.strip() if name_tag else "Unknown"
                        
                        details = poke.find('div', class_='details')
                        item = None
                        ability = None
                        tera_type = None
                        
                        if details:
                            item_tag = details.find('div', class_='item')
                            if item_tag:
                                item = item_tag.text.strip()
                                if item == "Held Item:": item = None 
                                
                            ability_tag = details.find('div', class_='ability')
                            if ability_tag:
                                ability = ability_tag.text.replace('Ability:', '').strip()
                                
                            tera_tag = details.find('div', class_='tera')
                            if tera_tag:
                                tera_type = tera_tag.text.replace('Tera Type:', '').strip()
                                
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
                    except Exception as poke_error:
                        logger.warning(f"Skipped a malformed Pokemon in rank {rank}'s team: {poke_error}")
                        continue # Skip the broken pokemon, keep the rest of the team!
                    
                teams_list.append({
                    'rank': rank,
                    'pokemon': pokemon_list
                })
                
            except Exception as e:
                logger.warning(f"Failed to parse entire team block: {e}")
                
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
            if not row.has_attr('data-count'):
                continue
                
            try:
                cols = row.find_all('td')
                if len(cols) < 5: continue
                
                usage_rank = self._safe_int(cols[0].text)
                
                link_tag = cols[2].find('a')
                if not link_tag: continue
                
                # Added safe split check just in case href is malformed
                href_parts = link_tag['href'].split('/')
                pokemon_id = href_parts[-1] if len(href_parts) > 0 else "unknown"
                pokemon_name = link_tag.text.strip()
                
                usage_count = self._safe_int(row.get('data-count'))
                points = self._safe_int(row.get('data-points'))
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
                logger.warning(f"Failed to parse a statistics row. Error: {e}")
                
        return stats