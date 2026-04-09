from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from .base import Base

class Species(Base):
    """The fundamental stats and typings of a Pokemon."""
    __tablename__ = 'species'
    
    id = Column(Integer, primary_key=True) 
    pokedex_number = Column(Integer)
    name = Column(String(100), nullable=False) # e.g., "Flutter Mane"
    
    # CRITICAL: We keep a specific column for what Limitless calls it so the scraper can link to it
    limitless_id = Column(String(100), unique=True, index=True) # e.g., "flutter-mane"
    
    # Rich Data
    type_1 = Column(String(20), nullable=False)
    type_2 = Column(String(20), nullable=True) # Nullable for mono-type Pokemon
    
    # Base Stats
    base_hp = Column(Integer, nullable=False)
    base_atk = Column(Integer, nullable=False)
    base_def = Column(Integer, nullable=False)
    base_spa = Column(Integer, nullable=False)
    base_spd = Column(Integer, nullable=False)
    base_spe = Column(Integer, nullable=False)

    # Relationships
    team_appearances = relationship("TeamPokemon", back_populates="species")
    metagame_stats = relationship("TournamentMetagameStat", back_populates="species")

class Move(Base):
    __tablename__ = 'moves'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    type = Column(String(20)) # e.g., "Fairy"
    category = Column(String(20)) # "Physical", "Special", "Status"
    description = Column(String(500), nullable=True)
    base_power = Column(Integer, nullable=True)
    accuracy = Column(Integer, nullable=True)

class Ability(Base):
    __tablename__ = 'abilities'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(String(500))

class Item(Base):
    __tablename__ = 'items'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(String(500))
