# src/pokemon_battle_engine/domain/status.py
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
import random
from .constants import(
    FIRE_TYPE, ELECTRIC_TYPE, POISON_TYPE, ICE_TYPE
)

if TYPE_CHECKING:
    from .models import Pokemon
    from .constants import Type

# --- Main Status Effects ---
class StatusEffect(ABC):
    @abstractmethod
    def tick(self, pokemon: Pokemon)-> str:
        ...

    def prevents_movement(self, pokemon: Pokemon)-> bool:
        return False
    
    def get_fail_message(self, pokemon: Pokemon)-> str:
        return f"{pokemon.name} couldn't move"

class BurnEffect(StatusEffect):
    def tick(self, pokemon: Pokemon)-> str:
        if pokemon.primary_type == FIRE_TYPE or pokemon.secondary_type == FIRE_TYPE:
            return f"{pokemon.name} is Immune to burn"
        damage = pokemon.max_hp//16
        pokemon.hp -= damage
        return f"{pokemon.name} has taken {damage} damage and now has {pokemon.hp}"

class ParalyzeEffect(StatusEffect):
    def tick(self, pokemon: Pokemon)-> str:
        if pokemon.primary_type == ELECTRIC_TYPE or pokemon.secondary_type == ELECTRIC_TYPE:
            return f"{pokemon.name} is Immune to paralysis"
        return f"{pokemon.name} is paralyzed"

    def prevents_movement(self, pokemon: Pokemon)-> bool:
        if pokemon.primary_type == ELECTRIC_TYPE or pokemon.secondary_type == ELECTRIC_TYPE:
            return False
        return random.randint(1,100) <= 25
    
    def get_fail_message(self, pokemon: Pokemon)-> str:
        return f"{pokemon.name} didn't move"

class SleepEffect(StatusEffect):
    def tick(self, pokemon: Pokemon)-> str:
        return f"{pokemon.name} is fast asleep."
    
    def prevents_movement(self, pokemon: Pokemon)->bool:
            if random.randint(1, 100) <= 33:
                return False
            else:
                return True
            
    def get_fail_message(self, pokemon: Pokemon)-> str:
        return f"{pokemon.name} didn't woke up"	

class PoisonEffect(StatusEffect):
    def tick(self, pokemon: Pokemon) -> str:
        if pokemon.primary_type == POISON_TYPE or pokemon.secondary_type == POISON_TYPE:
            return f"{pokemon.name} is Immune to poison!"
        damage = pokemon.max_hp // 16
        pokemon.hp -= damage
        return f"{pokemon.name} is hurt by poison!"
    
class BadlyPoisonedEffect(StatusEffect):
    def tick(self, pokemon: Pokemon) -> str:
        if pokemon.primary_type == POISON_TYPE or pokemon.secondary_type == POISON_TYPE:
            return f"{pokemon.name} is Immune to poison!"
        pokemon.poison_turn_count += 1
        damage = (pokemon.poison_turn_count * pokemon.max_hp) / 16.0
        pokemon.hp -= int(damage)
        return f"{pokemon.name} is badly hurt by poison!"
    
class FreezeEffect(StatusEffect):
    def tick(self, pokemon: Pokemon) -> str:
        if pokemon.primary_type == ICE_TYPE or pokemon.secondary_type == ICE_TYPE:
            return f"{pokemon.name} is Immune to freeze!"
        return f"{pokemon.name} is frozen solid!"
    
    def prevents_movement(self, pokemon: Pokemon)->bool:
            if random.randint(1, 100) <= 20:
                return False
            else:
                return True
            
    def get_fail_message(self, pokemon: Pokemon)-> str:
        return f"{pokemon.name} didn't defrost"	

class ConfusionEffect(StatusEffect):
    def tick(self, pokemon: Pokemon) -> str:
        if random.randint(1, 100) <= 50:
            damage = int(pokemon.level * 2.5) 
            pokemon.hp -= damage
            return f"{pokemon.name} hurt itself in confusion! (-{damage} HP)"
        return f"{pokemon.name} is confused!"

    def prevents_movement(self, pokemon: Pokemon) -> bool:
        return False
    
    def get_fail_message(self, pokemon: Pokemon) -> str:
        return f"{pokemon.name} is confused!"
    
class AttractEffect(StatusEffect):
    def tick(self, pokemon: Pokemon) -> str:
        return f"{pokemon.name} is in love with the foe!"

    def prevents_movement(self, pokemon: Pokemon) -> bool:
        return random.randint(1, 100) <= 50
    
    def get_fail_message(self, pokemon: Pokemon) -> str:
        return f"{pokemon.name} is immobilized by love!"
    
class CurseEffect(StatusEffect):
    def tick(self, pokemon: Pokemon) -> str:
        drain = int(pokemon.max_hp * 0.25)
        pokemon.hp -= drain
        return f"{pokemon.name} was hurt by the curse! (-{drain} HP)"
    