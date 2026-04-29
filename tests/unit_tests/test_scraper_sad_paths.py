import pytest
from data_pipeline.scraper import VGCScraper

@pytest.fixture
def scraper():
    return VGCScraper()

def test_parse_tournament_standings_malformed(scraper):
    """Test handling of malformed standings table."""
    html = '<table class="data-table"><tr><td>No Data</td></tr></table>'
    data = scraper.parse_tournament_standings(html)
    assert data['standings'] == []

def test_parse_tournament_teams_missing_details(scraper):
    """Test team parsing when details (item/ability) are missing."""
    html = """
    <div class="tournament-decklist">
        <div class="teamlist-toggle">1st</div>
        <div class="pkmn" data-id="123">
            <div class="name">Pikachu</div>
            <div class="details"></div>
            <ul class="moves"><li>Volt Tackle</li></ul>
        </div>
    </div>
    """
    teams = scraper.parse_tournament_teams(html)
    assert len(teams) == 1
    assert teams[0]['pokemon'][0]['item'] is None
    assert teams[0]['pokemon'][0]['ability'] is None

def test_parse_tournament_statistics_malformed(scraper):
    """Test statistics parsing with insufficient columns."""
    html = '<table class="data-table"><tr data-count="10"><td>Rank1</td><td>Extra</td></tr></table>'
    stats = scraper.parse_tournament_statistics(html)
    assert stats == []
