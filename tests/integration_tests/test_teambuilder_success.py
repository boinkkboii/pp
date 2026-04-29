import pytest
from backend.models import UserTeam
from backend.crud import user as crud_user

def test_update_team_success(client, db_session, setup_test_users, api_key_header):
    """Test successful team update (200 OK)."""
    # Create team
    team = crud_user.create_user_team(db_session, user_id=setup_test_users["user1"].id, name="OriginalName")
    
    # Login
    response = client.post("/api/auth/login", json={"username": "user1", "password": "hashedpassword"}, headers=api_key_header)
    token = response.json()["access_token"]
    
    # Update team
    response = client.put(
        f"/api/teambuilder/teams/{team.id}",
        json={"name": "NewName"},
        headers={**api_key_header, "Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    assert response.json()["name"] == "NewName"

def test_delete_team_success(client, db_session, setup_test_users, api_key_header):
    """Test successful team deletion (200 OK)."""
    # Create team
    team = crud_user.create_user_team(db_session, user_id=setup_test_users["user1"].id, name="DeleteMe")
    
    # Login
    response = client.post("/api/auth/login", json={"username": "user1", "password": "hashedpassword"}, headers=api_key_header)
    token = response.json()["access_token"]
    
    # Delete team
    response = client.delete(
        f"/api/teambuilder/teams/{team.id}",
        headers={**api_key_header, "Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    assert response.json()["message"] == "Team deleted"
    
    # Verify it's gone
    assert crud_user.get_user_team(db_session, team.id, setup_test_users["user1"].id) is None
