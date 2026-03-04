from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean, CheckConstraint
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

# =====================================================================
# PART 1: THE STATIC ENCYCLOPEDIA (Sourced from PokeAPI)
# This data is absolute. It is seeded once and rarely changes.
# =====================================================================

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


# =====================================================================
# PART 2: THE DYNAMIC JOURNAL (Sourced from LimitlessVGC Scraper)
# This data represents historical events and human choices.
# =====================================================================

class Format(Base):
    __tablename__ = 'formats'
    id = Column(Integer, primary_key=True)
    limitless_id = Column(String(20), unique=True, nullable=False) # e.g., "svi"
    name = Column(String(100), nullable=False) 
    
    tournaments = relationship("Tournament", back_populates="format")

class Tournament(Base):
    __tablename__ = 'tournaments'
    id = Column(Integer, primary_key=True)
    limitless_id = Column(String(100), unique=True, nullable=False) # e.g., "420"
    name = Column(String(255), nullable=False)
    date = Column(String(50))
    country_code = Column(String(10))
    players_count = Column(Integer)
    
    format_id = Column(Integer, ForeignKey('formats.id'))
    format = relationship("Format", back_populates="tournaments")
    
    results = relationship("TournamentResult", back_populates="tournament")
    metagame_stats = relationship("TournamentMetagameStat", back_populates="tournament")

class Player(Base):
    __tablename__ = 'players'
    id = Column(Integer, primary_key=True)
    limitless_id = Column(String(100), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    country_code = Column(String(10))

    results = relationship("TournamentResult", back_populates="player")

class Team(Base):
    __tablename__ = 'teams'
    id = Column(Integer, primary_key=True)
    limitless_team_id = Column(String(100), unique=True, nullable=False) 
    
    results = relationship("TournamentResult", back_populates="team")
    pokemons = relationship("TeamPokemon", back_populates="team", cascade="all, delete-orphan")

class TournamentResult(Base):
    """Bridge table mapping Who played Where, What Rank they got, and What Team they used."""
    __tablename__ = 'tournament_results'
    id = Column(Integer, primary_key=True)
    tournament_id = Column(Integer, ForeignKey('tournaments.id'), nullable=False)
    player_id = Column(Integer, ForeignKey('players.id'), nullable=False)
    team_id = Column(Integer, ForeignKey('teams.id'), nullable=True) # Sometimes teams are hidden
    
    rank = Column(Integer)

    tournament = relationship("Tournament", back_populates="results")
    player = relationship("Player", back_populates="results")
    team = relationship("Team", back_populates="results")

class TeamPokemon(Base):
    """A specific instance of a Pokemon on a human player's team."""
    __tablename__ = 'team_pokemon'
    id = Column(Integer, primary_key=True)
    team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    species_id = Column(Integer, ForeignKey('species.id'), nullable=False)
    
    # These are dynamic choices the player made
    item_id = Column(Integer, ForeignKey('items.id'), nullable=True) 
    ability_id = Column(Integer, ForeignKey('abilities.id'), nullable=True) 
    tera_type = Column(String(20), nullable=True)
    
    team = relationship("Team", back_populates="pokemons")
    species = relationship("Species", back_populates="team_appearances")
    
    # Using lazy="joined" so when we load a team, we instantly get its moves
    moves = relationship("TeamPokemonMove", back_populates="pokemon", cascade="all, delete-orphan", lazy="joined")

class TeamPokemonMove(Base):
    """The 4 move slots for a specific Pokemon on a team."""
    __tablename__ = 'team_pokemon_moves'
    pokemon_id = Column(Integer, ForeignKey('team_pokemon.id'), primary_key=True)
    move_id = Column(Integer, ForeignKey('moves.id'), primary_key=True)
    slot = Column(Integer, CheckConstraint('slot >= 1 AND slot <= 4'), nullable=False)
    
    pokemon = relationship("TeamPokemon", back_populates="moves")

class TournamentMetagameStat(Base):
    """The overall usage metrics (e.g. Incineroar was on 50% of teams at EUIC)."""
    __tablename__ = 'tournament_metagame_stats'
    id = Column(Integer, primary_key=True)
    tournament_id = Column(Integer, ForeignKey('tournaments.id'), nullable=False)
    species_id = Column(Integer, ForeignKey('species.id'), nullable=False)
    
    usage_rank = Column(Integer)
    usage_count = Column(Integer)
    usage_share_pct = Column(Float)
    
    tournament = relationship("Tournament", back_populates="metagame_stats")
    species = relationship("Species", back_populates="metagame_stats")