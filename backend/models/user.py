from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from datetime import date
from .base import Base

class UserTeam(Base):
    __tablename__ = 'user_teams'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, default="Untitled Team")
    format_id = Column(Integer, ForeignKey('formats.id'), nullable=True)
    created_at = Column(Date, default=date.today)
    
    format = relationship("Format")
    pokemons = relationship("UserTeamPokemon", back_populates="team", cascade="all, delete-orphan")

class UserTeamPokemon(Base):
    __tablename__ = 'user_team_pokemon'
    id = Column(Integer, primary_key=True)
    team_id = Column(Integer, ForeignKey('user_teams.id'), nullable=False)
    species_id = Column(Integer, ForeignKey('species.id'), nullable=True)
    item_id = Column(Integer, ForeignKey('items.id'), nullable=True)
    ability_id = Column(Integer, ForeignKey('abilities.id'), nullable=True)
    tera_type = Column(String(20), nullable=True)
    
    # Stats (EVs)
    ev_hp = Column(Integer, default=0)
    ev_atk = Column(Integer, default=0)
    ev_def = Column(Integer, default=0)
    ev_spa = Column(Integer, default=0)
    ev_spd = Column(Integer, default=0)
    ev_spe = Column(Integer, default=0)
    
    # Nature & Level
    nature = Column(String(20), default="Serious")
    level = Column(Integer, default=50)
    
    # IVs
    iv_hp = Column(Integer, default=31)
    iv_atk = Column(Integer, default=31)
    iv_def = Column(Integer, default=31)
    iv_spa = Column(Integer, default=31)
    iv_spd = Column(Integer, default=31)
    iv_spe = Column(Integer, default=31)
    
    team = relationship("UserTeam", back_populates="pokemons")
    species = relationship("Species")
    item = relationship("Item")
    ability = relationship("Ability")
    moves = relationship("UserTeamPokemonMove", back_populates="pokemon", cascade="all, delete-orphan")

class UserTeamPokemonMove(Base):
    __tablename__ = 'user_team_pokemon_moves'
    id = Column(Integer, primary_key=True)
    pokemon_id = Column(Integer, ForeignKey('user_team_pokemon.id'), nullable=False)
    move_id = Column(Integer, ForeignKey('moves.id'), nullable=True)
    slot = Column(Integer, nullable=False) # 1-4
    
    pokemon = relationship("UserTeamPokemon", back_populates="moves")
    move = relationship("Move")
