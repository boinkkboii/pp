import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session
from backend.crud import pokemon as crud_pokemon
from backend.models import Species, Move

def test_get_common_teammates_not_found(db_session):
    """Test get_common_teammates returns empty list if species not found."""
    assert crud_pokemon.get_common_teammates(db_session, "NonExistent") == []

def test_get_move_users_not_found(db_session):
    """Test get_move_users returns empty list if move not found."""
    assert crud_pokemon.get_move_users(db_session, "NonExistentMove") == []

@patch("httpx.AsyncClient.get")
@pytest.mark.asyncio
async def test_get_species_abilities_pokeapi_error(mock_get, client, api_key_header):
    """Test fallback to PokeAPI fails gracefully by calling the endpoint."""
    mock_get.return_value.status_code = 500
    
    # We call the endpoint through the client, which uses the DB fixture
    # This is a better integration test for the sad path
    response = client.get("/teambuilder/species/99999/abilities", headers=api_key_header)
    assert response.status_code == 404
    
def test_agent_tools_error_handling():
    """Test tools.py functions handle network/API errors."""
    from agent.tools import get_pokemon_stats
    with patch("requests.get") as mock_get:
        mock_get.side_effect = Exception("Network fail")
        result = get_pokemon_stats("Pikachu")
        assert "error" in result
        assert "Network fail" in result["error"]
