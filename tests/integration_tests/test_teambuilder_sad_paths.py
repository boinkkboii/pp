import pytest
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from backend.crud import user as crud_user
from backend.models import UserTeam

def test_get_team_forbidden_access(db_session, setup_test_users):
    """Test retrieving a team owned by another user returns None."""
    # Assume user1 creates team, user2 tries to access it
    team = crud_user.create_user_team(db_session, user_id=setup_test_users["user1"].id, name="Test")
    result = crud_user.get_user_team(db_session, team.id, user_id=setup_test_users["user2"].id)
    assert result is None

def test_delete_team_forbidden_access(db_session, setup_test_users):
    """Test deleting a team owned by another user fails."""
    team = crud_user.create_user_team(db_session, user_id=setup_test_users["user1"].id, name="DeleteMe")
    success = crud_user.delete_user_team(db_session, team.id, user_id=setup_test_users["user2"].id)
    assert success is False
    # Team should still exist
    assert db_session.query(UserTeam).filter(UserTeam.id == team.id).first() is not None

def test_update_pokemon_forbidden_access(db_session, setup_test_users):
    """Test updating a Pokemon in a team owned by another user fails."""
    team = crud_user.create_user_team(db_session, user_id=setup_test_users["user1"].id, name="Team1")
    poke_id = team.pokemons[0].id
    result = crud_user.update_user_team_pokemon(db_session, poke_id, user_id=setup_test_users["user2"].id, updates={"tera_type": "Fire"})
    assert result is None

# Note: Testing Database IntegrityError usually requires a mock DB 
# or a specific test setup that tries to violate unique constraints.
