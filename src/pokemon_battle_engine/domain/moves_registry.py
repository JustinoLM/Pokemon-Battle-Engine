# src/pokemon_battle_engine/domain/moves_registry.py

from .models import Move
from .damage import PhysicalDamageCalculator, SpecialDamageCalculator, StatusDamageCalculator
from .constants import NORMAL_TYPE, FIRE_TYPE, WATER_TYPE, ELECTRIC_TYPE, GRASS_TYPE
from pokemon_battle_engine.domain.move_effects import (
        TauntEffect, EncoreEffect, TormentEffect, 
        DisableEffect, AttractEffect, TrickEffect
    )

def get_move_by_name(move_name: str) -> Move:
    from pokemon_battle_engine.domain.models import (
        PhysicalDamageCalculator, SpecialDamageCalculator, StatusDamageCalculator,
        NORMAL_TYPE, FIRE_TYPE, WATER_TYPE, GRASS_TYPE, ELECTRIC_TYPE, PSYCHIC_TYPE,
        DARK_TYPE
    )
    
    moves_db = {
        "tackle": Move(name="Tackle", power=40, move_type=NORMAL_TYPE, damage_calculator=PhysicalDamageCalculator(), accuracy=100),
        "thunderbolt": Move(name="Thunderbolt", power=90, move_type=ELECTRIC_TYPE, damage_calculator=SpecialDamageCalculator(), accuracy=100),
        "flamethrower": Move(name="Flamethrower", power=90, move_type=FIRE_TYPE, damage_calculator=SpecialDamageCalculator(), accuracy=100),
        "watergun": Move(name="Water Gun", power=40, move_type=WATER_TYPE, damage_calculator=SpecialDamageCalculator(), accuracy=100),
        "razorleaf": Move(name="Razor Leaf", power=55, move_type=GRASS_TYPE, damage_calculator=PhysicalDamageCalculator(), accuracy=95),
        
        # Moves with Special Effects
        "taunt": Move(
            name="Taunt", 
            power=0, 
            move_type=DARK_TYPE,
            damage_calculator=StatusDamageCalculator(), 
            special_effect=TauntEffect()
        ),
        
        "encore": Move(
            name="Encore",
            power=0,
            move_type=NORMAL_TYPE,
            damage_calculator=StatusDamageCalculator(),
            special_effect=EncoreEffect()
        ),
        
        "trick": Move(
            name="Trick",
            power=0,
            move_type=PSYCHIC_TYPE,
            damage_calculator=StatusDamageCalculator(),
            special_effect=TrickEffect()
        ),
        
        # Agrega el resto: Torment, Disable, Attract, etc.

    }
    move_lower = move_name.lower()
    if move_lower in moves_db:
        return moves_db[move_lower]
    
    # Basic move for fallbacks
    
    return Move(name=move_name, power=50, move_type=NORMAL_TYPE, damage_calculator=PhysicalDamageCalculator(), accuracy=100)