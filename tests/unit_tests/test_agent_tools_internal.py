import pytest
from unittest.mock import patch, MagicMock
from agent.tools import (
    get_pokemon_stats, get_move_details, get_item_ability_details,
    get_recent_tournaments, search_tournaments, search_player_history,
    get_tournament_meta, get_tournament_teams, get_format_meta,
    get_all_formats, get_historical_meta, get_common_teammates,
    get_pokemon_standard_build, get_move_users
)

def test_tools_success_paths():
    """Test that all tool functions correctly hit the API and return JSON."""
    with patch("requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "success"}
        mock_get.return_value = mock_response

        # Test Category 1
        assert get_pokemon_stats("Pikachu") == {"data": "success"}
        assert get_move_details("Tackle") == {"data": "success"}
        assert get_item_ability_details("Leftovers", "item") == {"data": "success"}

        # Test Category 2
        assert get_recent_tournaments() == {"data": "success"}
        assert search_tournaments("Orlando") == {"data": "success"}
        assert search_player_history("PlayerOne") == {"data": "success"}

        # Test Category 3 & 4
        assert get_tournament_meta("123") == {"data": "success"}
        # get_tournament_teams attempts a slice [:25] which works on list but fails on dict.
        # This function is logically broken if the return type isn't a list. 
        # Update test to expect the correct behavior.
        with patch("requests.get") as mock_get_teams:
            mock_resp_list = MagicMock()
            mock_resp_list.json.return_value = [{"poke": "data"}]
            mock_get_teams.return_value = mock_resp_list
            assert get_tournament_teams("123") == [{"poke": "data"}]

        assert get_format_meta("RegG") == {"data": "success"}
        assert get_all_formats() == {"data": "success"}
        assert get_historical_meta(3) == {"data": "success"}

        # Test Category 5
        assert get_common_teammates("Miraidon") == {"data": "success"}
        assert get_pokemon_standard_build("Miraidon") == {"data": "success"}
        assert get_move_users("Wide Guard") == {"data": "success"}
