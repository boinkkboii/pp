import pytest
from pydantic import ValidationError
from backend.schemas import UserTeamPokemonBase, UserTeamPokemonUpdate

def test_ev_single_stat_limit():
    """Test that a single stat EV cannot exceed 252."""
    # This should work
    UserTeamPokemonBase(id=1, team_id=1, ev_hp=252)
    
    # This should fail
    with pytest.raises(ValidationError) as excinfo:
        UserTeamPokemonBase(id=1, team_id=1, ev_hp=253)
    assert "Single stat EV must be between 0 and 252" in str(excinfo.value)

def test_ev_total_limit():
    """Test that total EVs cannot exceed 510."""
    # This should work (252 + 252 + 4 = 508)
    UserTeamPokemonBase(id=1, team_id=1, ev_hp=252, ev_atk=252, ev_def=4)
    
    # This should fail (252 + 252 + 10 = 514)
    with pytest.raises(ValidationError) as excinfo:
        UserTeamPokemonBase(id=1, team_id=1, ev_hp=252, ev_atk=252, ev_def=10)
    assert "Total EVs cannot exceed 510" in str(excinfo.value)

def test_ev_update_validation():
    """Test that UserTeamPokemonUpdate also validates single stat limits."""
    # This should work
    UserTeamPokemonUpdate(ev_hp=252)
    
    # This should fail
    with pytest.raises(ValidationError) as excinfo:
        UserTeamPokemonUpdate(ev_hp=253)
    assert "Single stat EV must be between 0 and 252" in str(excinfo.value)
