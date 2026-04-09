from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .core.config import Config

# --- 1. THE CONNECTION SETUP ---
# For SQLite, we might need connect_args={"check_same_thread": False}
is_sqlite = Config.SQLALCHEMY_DATABASE_URI.startswith("sqlite")
connect_args = {"check_same_thread": False} if is_sqlite else {}

engine = create_engine(Config.SQLALCHEMY_DATABASE_URI, echo=False, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """
    Creates a new database session for a single request and closes it when the request is finished.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
