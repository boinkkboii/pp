import pytest
from backend.models import Species, User
from backend.core.auth import create_access_token

def test_get_pokemon_endpoint(client, db_session, api_key_header):
    # Setup: Add a pokemon to the DB
    pikachu = Species(name="Pikachu", limitless_id="pikachu", type_1="Electric", 
                      base_hp=35, base_atk=55, base_def=40, base_spa=50, base_spd=50, base_spe=90)
    db_session.add(pikachu)
    db_session.commit()
    
    # Correct path prefix is /api/encyclopedia/pokemon/
    response = client.get("/api/encyclopedia/pokemon/Pikachu", headers=api_key_header)
    assert response.status_code == 200
    assert response.json()["name"] == "Pikachu"

def test_teambuilder_save(client, db_session, api_key_header):
    # 0. Setup: Create user and token
    user = User(username="teamuser", hashed_password="hashed_password")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    token = create_access_token({"sub": user.username})
    auth_headers = {"Authorization": f"Bearer {token}", **api_key_header}

    # Correct path for creating a team is POST /api/teambuilder/teams
    payload = {"name": "Test Team"}
    response = client.post("/api/teambuilder/teams", json=payload, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["name"] == "Test Team"
