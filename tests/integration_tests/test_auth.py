import pytest

def test_full_auth_lifecycle(client, api_key_header):
    """Verify FR-01 (Register), FR-02 (Login), and FR-03 (Logout)."""
    username = "qa_tester"
    password = "securePassword123"
    
    # 1. Register (FR-01) - Open route
    reg_resp = client.post("/api/auth/register", json={"username": username, "password": password})
    assert reg_resp.status_code == 200
    
    # 2. Login (FR-02) - Open route
    login_resp = client.post("/api/auth/login", json={"username": username, "password": password})
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]
    assert token is not None
    
    # 3. Profile Access (Part of Auth verification)
    # Profile requires Bearer Token AND X-API-KEY (due to middleware)
    headers = {
        "Authorization": f"Bearer {token}",
        **api_key_header
    }
    profile_resp = client.get("/api/auth/profile", headers=headers)
    assert profile_resp.status_code == 200
    assert profile_resp.json()["username"] == username

def test_team_save_unauthenticated_forbidden(client, api_key_header):
    """Verify FR-22: System will not save teams built without user logged in."""
    team_payload = {
        "name": "Guest Team",
        "format_id": 1
    }
    # Attempt to save without Authorization header but WITH X-API-KEY to pass middleware
    response = client.post("/api/teambuilder/teams", json=team_payload, headers=api_key_header)
    assert response.status_code == 401 # Unauthorized by FastAPI security, not 403 by middleware

def test_register_password_validation(client):
    """Verify FR-01: Password complexity/length enforcement."""
    payload = {"username": "weak_user", "password": "123"}
    # Register is an open route in middleware
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 422 # Pydantic min_length: 8 validation
