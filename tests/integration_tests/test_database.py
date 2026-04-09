import pytest
from backend.crud import create_user_team, get_user_teams
from backend.models import UserTeam, UserTeamPokemon

"""
Requirement 2: Database & ORM Testing (Backend)
Ensures that the database schema exists and that basic CRUD operations work as expected.
"""

def test_schema_exists(db_session):
    """
    Requirement 2.1: Schema Initialization
    Attempts to query a core table. If this fails, the migrations or Base.metadata.create_all did not run.
    """
    count = db_session.query(UserTeam).count()
    assert count == 0 # Database should be empty at the start of the test

def test_get_user_teams_crud(db_session):
    """
    Requirement 2.2: CRUD Operations
    This test reproduces the fix for the 500 error on get_user_teams.
    It creates a team and asserts that the fetch function correctly handles it.
    
    Potential Fail: This will crash if the UserTeam model is missing a relationship 
    or if the table 'vgc_db.user_teams' truly doesn't exist.
    """
    # 1. Create a fake team in the test DB
    test_team = create_user_team(db_session, name="Victory Star")
    
    # 2. Call the function that was failing
    teams = get_user_teams(db_session)
    
    # 3. Assertions
    assert len(teams) == 1
    assert teams[0].name == "Victory Star"
    assert teams[0].id == test_team.id
    
    # Check if the 6 empty slots were also created
    assert len(teams[0].pokemons) == 6
    
    print(f"✅ CRUD Test Passed: Team ID {teams[0].id} found with name {teams[0].name}")
