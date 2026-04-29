import pytest
from unittest.mock import MagicMock, patch
from requests.exceptions import HTTPError
from data_pipeline.scraper import VGCScraper

@pytest.fixture
def scraper():
    return VGCScraper()

def test_fetch_page_success(scraper):
    """Test successful fetch and return of HTML."""
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = "<html><body>Test</body></html>"
        
        result = scraper.fetch_page("http://test.com")
        assert result == "<html><body>Test</body></html>"
        mock_get.assert_called_once()

def test_fetch_page_retry_429(scraper):
    """Test tenacity retry on 429 error."""
    with patch('requests.get') as mock_get:
        # Mock 429 once, then 200
        response_429 = MagicMock()
        response_429.status_code = 429
        response_429.raise_for_status.side_effect = HTTPError(response=response_429)
        
        response_200 = MagicMock()
        response_200.status_code = 200
        response_200.text = "Success"
        
        mock_get.side_effect = [response_429, response_200]
        
        result = scraper.fetch_page("http://test.com")
        assert result == "Success"
        assert mock_get.call_count == 2

def test_parse_tournament_list_basic(scraper):
    """Test parsing a sample tournament list page."""
    html = """
    <table class="completed-tournaments">
        <tr data-date="2026-04-29" data-name="Test Tour" data-format="VGC" data-players="100" data-country="US">
            <td><a href="/tournaments/test-123">Link</a></td>
        </tr>
    </table>
    """
    data = scraper.parse_tournament_list(html)
    assert len(data['tournaments']) == 1
    assert data['tournaments'][0]['tournament_id'] == 'test-123'
    assert data['tournaments'][0]['players'] == 100
