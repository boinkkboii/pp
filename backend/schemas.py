from pydantic import BaseModel
from typing import List, Optional

# --- FORMAT SCHEMAS ---
class FormatBase(BaseModel):
    id: int
    limitless_id: str
    name: str
    
    class Config:
        from_attributes = True

# --- TOURNAMENT SCHEMAS ---
class TournamentBase(BaseModel):
    id: int
    limitless_id: str
    name: str
    date: Optional[str] = None
    country_code: Optional[str] = None
    players_count: Optional[int] = None
    format: Optional[FormatBase] = None

class Tournament(TournamentBase):
    class Config:
        from_attributes = True

# --- ENCYCLOPEDIA SCHEMAS (The Small Pieces) ---
class MoveBase(BaseModel):
    id: int
    name: str
    type: Optional[str] = None
    category: Optional[str] = None
    base_power: Optional[int] = None
    accuracy: Optional[int] = None
    class Config: from_attributes = True

class ItemBase(BaseModel):
    id: int
    name: str
    class Config: from_attributes = True

class AbilityBase(BaseModel):
    id: int
    name: str
    class Config: from_attributes = True

class SpeciesBase(BaseModel):
    id: int
    name: str
    type_1: str
    type_2: Optional[str] = None
    base_spe: int # Just pulling Speed for the frontend, but you can add the rest!
    class Config: from_attributes = True

# --- TEAM DYNAMICS (The Middle Layer) ---
class TeamPokemonMoveBase(BaseModel):
    slot: int
    move: Optional[MoveBase] = None # Uses the SQLAlchemy relationship we just added!
    class Config: from_attributes = True

class TeamPokemonBase(BaseModel):
    id: int
    tera_type: Optional[str] = None
    species: Optional[SpeciesBase] = None
    item: Optional[ItemBase] = None       # Uses the new relationship!
    ability: Optional[AbilityBase] = None # Uses the new relationship!
    moves: List[TeamPokemonMoveBase] = []
    class Config: from_attributes = True

class TeamBase(BaseModel):
    id: int
    limitless_team_id: str
    pokemons: List[TeamPokemonBase] = []
    class Config: from_attributes = True

class PlayerBase(BaseModel):
    id: int
    name: str
    country_code: Optional[str] = None
    class Config: from_attributes = True


# --- THE GRAND FINALE (The Top Layer) ---
class TournamentResultBase(BaseModel):
    id: int
    rank: Optional[int] = None
    player: Optional[PlayerBase] = None
    team: Optional[TeamBase] = None
    class Config: from_attributes = True

class TournamentMetagameStatBase(BaseModel):
    id: int
    usage_rank: Optional[int] = None
    usage_count: Optional[int] = None
    usage_share_pct: Optional[float] = None
    species: Optional[SpeciesBase] = None

    class Config:
        from_attributes = True