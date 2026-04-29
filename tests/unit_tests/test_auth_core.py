import pytest
from datetime import timedelta
from backend.core.auth import get_password_hash, verify_password, create_access_token, ALGORITHM, SECRET_KEY
from jose import jwt

def test_password_hashing():
    password = "secret_password"
    hashed = get_password_hash(password)
    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("wrong_password", hashed) is False

def test_create_access_token():
    data = {"sub": "testuser"}
    token = create_access_token(data)
    
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert payload["sub"] == "testuser"
    assert "exp" in payload

def test_create_access_token_with_expiry():
    data = {"sub": "testuser"}
    expires_delta = timedelta(minutes=5)
    token = create_access_token(data, expires_delta=expires_delta)
    
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert payload["sub"] == "testuser"
    assert "exp" in payload
