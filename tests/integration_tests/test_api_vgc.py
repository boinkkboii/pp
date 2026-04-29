import pytest
from datetime import date
from fastapi import HTTPException
from backend.models import Species, Move, Item, Ability, Tournament, Format

def test_encyclopedia_endpoints(client, db_session, api_key_header):
    # Setup
    s = Species(name="Calyrex-Shadow", limitless_id="calyrex-shadow", type_1="Psychic", type_2="Ghost",
                base_hp=100, base_atk=85, base_def=80, base_spa=165, base_spd=100, base_spe=150)
    m = Move(name="Astral Barrage", type="Ghost", category="Special", base_power=120)
    i = Item(name="Life Orb")
    a = Ability(name="As One")
    db_session.add_all([s, m, i, a])
    db_session.commit()

    # Test Pokemon
    resp = client.get("/api/encyclopedia/pokemon/Calyrex-Shadow", headers=api_key_header)
    assert resp.status_code == 200
    assert resp.json()["name"] == "Calyrex-Shadow"

    # Test Move
    resp = client.get("/api/encyclopedia/moves/Astral Barrage", headers=api_key_header)
    assert resp.status_code == 200
    assert resp.json()["name"] == "Astral Barrage"

    # Test Item
    resp = client.get("/api/encyclopedia/items/Life Orb", headers=api_key_header)
    assert resp.status_code == 200
    assert resp.json()["name"] == "Life Orb"

    # Test Ability
    resp = client.get("/api/encyclopedia/abilitys/As One", headers=api_key_header)
    assert resp.status_code == 200
    assert resp.json()["name"] == "As One"

def test_tournament_endpoints(client, db_session, api_key_header):
    # Setup
    fmt = Format(limitless_id="vgc2024regG", name="VGC 2024 Reg G")
    db_session.add(fmt)
    db_session.commit()
    db_session.refresh(fmt)

    t = Tournament(limitless_id="t1", name="Worlds 2024", format_id=fmt.id, date=date(2024, 8, 16))
    db_session.add(t)
    db_session.commit()
    db_session.refresh(t)

    # Search
    resp = client.get("/api/tournaments/search?q=Worlds", headers=api_key_header)
    assert resp.status_code == 200
    assert len(resp.json()) > 0
    assert resp.json()[0]["name"] == "Worlds 2024"

    # Single Tournament
    resp = client.get("/api/tournaments/t1", headers=api_key_header)
    assert resp.status_code == 200
    assert resp.json()["name"] == "Worlds 2024"

def test_api_key_missing(client):
    with pytest.raises(HTTPException) as excinfo:
        client.get("/api/encyclopedia/pokemon/Pikachu")
    assert excinfo.value.status_code == 403

def test_api_key_invalid(client):
    with pytest.raises(HTTPException) as excinfo:
        client.get("/api/encyclopedia/pokemon/Pikachu", headers={"X-API-KEY": "wrong_key"})
    assert excinfo.value.status_code == 403
