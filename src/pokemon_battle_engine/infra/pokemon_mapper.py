# src/pokemon_battle_engine/infra/pokemon_mapper.py

from typing import Dict
from pokemon_battle_engine.domain.models import Pokemon
from pokemon_battle_engine.domain.constants import (
    BUG_TYPE, DARK_TYPE, DRAGON_TYPE, ELECTRIC_TYPE, FIGHTING_TYPE, 
    FAIRY_TYPE, FLYING_TYPE, FIRE_TYPE, GHOST_TYPE, GROUND_TYPE, 
    GRASS_TYPE, ICE_TYPE, NORMAL_TYPE, POISON_TYPE, PSYCHIC_TYPE, ROCK_TYPE,
    STEEL_TYPE, WATER_TYPE
)

# --- Helper to map string API to Type Object ---
def _get_type(type_name: str)-> Dict:
    type_map = {
        "bug" : BUG_TYPE,
        "dark": DARK_TYPE,
        "dragon" : DRAGON_TYPE,
        "electric" : ELECTRIC_TYPE,
        "fighting" : FIGHTING_TYPE,
        "fairy": FAIRY_TYPE,
        "flying" : FLYING_TYPE,
        "fire": FIRE_TYPE,
        "ghost": GHOST_TYPE,
        "ground": GROUND_TYPE,
        "grass": GRASS_TYPE,
        "ice": ICE_TYPE,
        "normal": NORMAL_TYPE,
        "poison": POISON_TYPE,
        "psychic": PSYCHIC_TYPE,
        "rock": ROCK_TYPE,
        "steel": STEEL_TYPE,
        "water": WATER_TYPE

    }
    return type_map.get(type_name, NORMAL_TYPE)

# --- Main Mapper Function ---
def map_pokemon_from_api(data:dict)->Pokemon:
    # --- Extract basic data ---
    name = data['name']
    level = 50 #default level for battles

    # --- Stats ---
    stats = data['stats']
    hp = next(s['base_stat'] for s in stats if s['stat']['name']=='hp')
    attack = next(s['base_stat'] for s in stats if s['stat']['name']=='attack')
    defense = next(s['base_stat'] for s in stats if s['stat']['name']=='defense')
    sp_attack = next(s['base_stat'] for s in stats if s['stat']['name']=='special-attack')
    sp_defense = next(s['base_stat'] for s in stats if s['stat']['name']=='special-defense')
    speed = next(s['base_stat'] for s in stats if s['stat']['name']=='speed')

    # --- Types ---
    types_data = data['types']
    primary_type_name = types_data[0]['type']['name']
    primary_type = _get_type(primary_type_name)

    secondary_type = None
    if len(types_data)>1:
        secondary_type_name = types_data[1]['type']['name']
        secondary_type = _get_type(secondary_type_name)

    # --- Return the pokemon ---

    return Pokemon(
        name= name,
        level= level,
        base_hp= hp,
        base_attack= attack,
        base_defense= defense,
        base_sp_attack= sp_attack,
        base_sp_defense= sp_defense,
        base_speed= speed,
        primary_type= primary_type,
        secondary_type= secondary_type
    )
    
    





