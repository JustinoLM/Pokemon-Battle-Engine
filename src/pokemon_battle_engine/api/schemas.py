# src/pokemon_battle_engine/api/schemas.py

from pydantic import BaseModel, Field
from typing import Optional



class PokemonCreate(BaseModel):
    name: str

class TrainerCreate(BaseModel):
    name: str = Field(..., description="Trainer Name")
    team: list=Field(..., description="Names of the pokemon in the trainer team ex. ['pikachu', 'charizard']")

class BattleCreateRequest(BaseModel):
    trainer1: TrainerCreate
    trainer2: TrainerCreate

class TurnSubmitRequest(BaseModel):
    attacker_name: str = Field(..., description="Name of the attacking trainer")
    move_name: str = Field(..., description="Name of the move used by the attacker")

class PokemonState(BaseModel):
    name: str
    hp: int
    max_hp: int
    status: Optional[str] = None # "burn", "poison"

class BattleStateResponse(BaseModel):
    battle_id: str
    trainer1_name: str
    trainer2_name: str
    turn_count: int
    current_turn_pokemon: PokemonState
    opponent_pokemon: PokemonState
    messages:list[str]
    weather: Optional[str]
    terrain: Optional[str]


