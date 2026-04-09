import pytest
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.models import Base
from backend.database import get_db
from backend.main import app

# Use a separate test database (SQLite by default, can be overridden for MySQL parity)
TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL", "sqlite:///./test_vgc.db")

connect_args = {"check_same_thread": False} if TEST_DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(TEST_DATABASE_URL, connect_args=connect_args)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """
    Requirement 2.1: Schema Initialization
    Ensures that the database schema is correctly generated before any tests run.
    If this fails, it means your SQLAlchemy models are likely broken or have circular imports.
    """
    Base.metadata.create_all(bind=engine)
    yield
    try:
        if os.path.exists("./test_vgc.db"):
            os.remove("./test_vgc.db")
    except PermissionError:
        # On Windows, the file might still be locked by another process/thread
        pass

@pytest.fixture
def db_session():
    """Provides a clean database session for each test, rolling back changes after."""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(db_session):
    """
    FastAPI TestClient that overrides the get_db dependency to use the test database.
    This prevents tests from accidentally modifying production data.
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
