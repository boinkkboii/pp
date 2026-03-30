from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import date

# --- FORMAT SCHEMAS ---
class FormatBase(BaseModel):
    id: int
    limitless_id: str
    name: str
    
    class Config:
        from_attributes = True

# --- DAMAGE CALC ---
class DamageCalcParams(BaseModel):
    attacker_name: str = Field(description="Name of attacking Pokemon, e.g., 'Ursaluna'")
    defender_name: str = Field(description="Name of defending Pokemon, e.g., 'Amoonguss'")
    move_name: str = Field(description="Name of the attack, e.g., 'Facade'")
    
    attacker_item: str = Field(default="", description="Item held by attacker, e.g., 'Choice Band'")
    attacker_ability: str = Field(default="", description="Ability of attacker, e.g., 'Guts'")
    attacker_status: str = Field(default="", description="Status of attacker. Use ONLY: 'brn', 'par', 'psn', 'slp', 'frz' or empty string")
    
    # --- NEW: DYNAMIC ATTACKER STATS ---
    attacker_nature: str = Field(default="Serious", description="Nature of attacker, e.g., 'Adamant', 'Jolly', 'Timid'")
    attacker_evs: Dict[str, int] = Field(
        default={"hp": 0, "atk": 0, "def": 0, "spa": 0, "spd": 0, "spe": 0}, 
        description="Dictionary of EVs, e.g., {'atk': 252, 'spe': 252}"
    )
    
    defender_item: str = Field(default="", description="Item held by defender, e.g., 'Sitrus Berry'")
    defender_ability: str = Field(default="", description="Ability of defender, e.g., 'Regenerator'")
    
    # --- NEW: DYNAMIC DEFENDER STATS ---
    defender_nature: str = Field(default="Serious", description="Nature of defender, e.g., 'Bold', 'Calm', 'Relaxed'")
    defender_evs: Dict[str, int] = Field(
        default={"hp": 0, "atk": 0, "def": 0, "spa": 0, "spd": 0, "spe": 0}, 
        description="Dictionary of EVs, e.g., {'hp': 252, 'def': 252}"
    )
    
    has_reflect: bool = Field(default=False, description="True if Reflect is active against a physical move")
    has_light_screen: bool = Field(default=False, description="True if Light Screen is active against a special move")

# --- TOURNAMENT SCHEMAS ---
class TournamentBase(BaseModel):
    id: int
    limitless_id: str
    name: str
    date: date
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
    limitless_id: str | None = None
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

# --- USER TEAM SCHEMAS (NEW) ---

class UserTeamPokemonMoveBase(BaseModel):
    slot: int
    move_id: Optional[int] = None
    move: Optional[MoveBase] = None
    class Config: from_attributes = True

class UserTeamPokemonBase(BaseModel):
    id: int
    team_id: int
    species_id: Optional[int] = None
    item_id: Optional[int] = None
    ability_id: Optional[int] = None
    tera_type: Optional[str] = None
    ev_hp: int = 0
    ev_atk: int = 0
    ev_def: int = 0
    ev_spa: int = 0
    ev_spd: int = 0
    ev_spe: int = 0
    nature: str = "Serious"
    level: int = 50
    iv_hp: int = 31
    iv_atk: int = 31
    iv_def: int = 31
    iv_spa: int = 31
    iv_spd: int = 31
    iv_spe: int = 31
    
    species: Optional[SpeciesBase] = None
    item: Optional[ItemBase] = None
    ability: Optional[AbilityBase] = None
    moves: List[UserTeamPokemonMoveBase] = []
    
    class Config: from_attributes = True

class UserTeamBase(BaseModel):
    id: int
    name: str
    format_id: Optional[int] = None
    created_at: date
    pokemons: List[UserTeamPokemonBase] = []
    
    class Config: from_attributes = True

class UserTeamCreate(BaseModel):
    name: str = "Untitled Team"
    format_id: Optional[int] = None

class UserTeamUpdate(BaseModel):
    name: Optional[str] = None
    format_id: Optional[int] = None

class UserTeamPokemonUpdate(BaseModel):
    species_id: Optional[int] = None
    item_id: Optional[int] = None
    ability_id: Optional[int] = None
    tera_type: Optional[str] = None
    ev_hp: Optional[int] = None
    ev_atk: Optional[int] = None
    ev_def: Optional[int] = None
    ev_spa: Optional[int] = None
    ev_spd: Optional[int] = None
    ev_spe: Optional[int] = None
    nature: Optional[str] = None
    level: Optional[int] = None
    iv_hp: Optional[int] = None
    iv_atk: Optional[int] = None
    iv_def: Optional[int] = None
    iv_spa: Optional[int] = None
    iv_spd: Optional[int] = None
    iv_spe: Optional[int] = None

class UserTeamPokemonMoveUpdate(BaseModel):
    move_id: Optional[int] = None