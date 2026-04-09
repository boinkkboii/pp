import pytest
from backend.models import Species

def test_get_pokemon_endpoint(client, db_session):
    # Setup: Add a pokemon to the DB
    pikachu = Species(name="Pikachu", limitless_id="pikachu", type_1="Electric", base_hp=35, base_atk=55, base_def=40, base_spa=50, base_spd=50, base_spe=90)
    db_session.add(pikachu)
    db_session.commit()
    
    # Correct path prefix is /api/encyclopedia/pokemon/
    response = client.get("/api/encyclopedia/pokemon/Pikachu")
    assert response.status_code == 200
    assert response.json()["name"] == "Pikachu"

def test_teambuilder_save(client):
    # Correct path for creating a team is POST /api/teambuilder/teams
    payload = {"name": "Test Team"}
    response = client.post("/api/teambuilder/teams", json=payload)
    assert response.status_code == 200 # crud.create_user_team returns the object, FastAPI default is 200 unless set to 201
    assert response.json()["name"] == "Test Team"
