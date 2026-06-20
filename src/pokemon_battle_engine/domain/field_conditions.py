# src/pokemon_battle_engine/domain/field_conditions.py
from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Optional, List, TYPE_CHECKING
from .constants import (
    WEATHER_MAP, TERRAIN_MAP,
    RAIN, SUN, SANDSTORM, HAIL,
    ROCK_TYPE, GROUND_TYPE, STEEL_TYPE, ICE_TYPE, FLYING_TYPE,
    GRASS_TYPE, ELECTRIC_TYPE, PSYCHIC_TYPE, DRAGON_TYPE
)

if TYPE_CHECKING:
    from .battle import Trainer

@dataclass
class BattleField:
    """Manages global environmental conditions (Weather and Terrain)."""
    
    # --- State ---
    weather_name: Optional[str] = None
    weather_turns_left: int = 0
    
    terrain_name: Optional[str] = None
    terrain_turns_left: int = 0

    # --- Setup ---
    def set_weather(self, weather_obj) -> None:
        """Sets a new weather condition."""
        self.weather_name = weather_obj.name
        self.weather_turns_left = random.randint(3, 5)
        # Return a message for the battle log
        return f"{weather_obj.name.capitalize()} started!"

    def set_terrain(self, terrain_obj) -> None:
        """Sets a new terrain condition."""
        self.terrain_name = terrain_obj.name
        self.terrain_turns_left = random.randint(3, 5)
        return f"{terrain_obj.name.capitalize()} formed!"

    # --- Turn Logic ---
    def end_turn(self, messages: List[str], trainers: List['Trainer']) -> None:
        """
        Processes end-of-turn effects: Decay counters, apply passive damage/heals.
        """
        # 1. Weather Decay & Damage
        if self.weather_turns_left > 0:
            self.weather_turns_left -= 1
            if self.weather_turns_left == 0:
                messages.append(f"The {self.weather_name} ended.")
                self.weather_name = None
            else:
                self._apply_weather_effects(messages, trainers)

        # 2. Terrain Decay & Effects
        if self.terrain_turns_left > 0:
            self.terrain_turns_left -= 1
            if self.terrain_turns_left == 0:
                messages.append(f"The {self.terrain_name} faded.")
                self.terrain_name = None
            else:
                self._apply_terrain_effects(messages, trainers)

    def _apply_weather_effects(self, messages: List[str], trainers: List['Trainer']) -> None:
        """Applies damage from Sandstorm or Hail."""
        if self.weather_name in ["sandstorm", "hail"]:
            weather_obj = WEATHER_MAP.get(self.weather_name)
            
            for trainer in trainers:
                pokemon = trainer.get_active_pokemon()
                if pokemon.hp <= 0: continue

                is_immune = False
                if self.weather_name == "sandstorm":
                    if pokemon.primary_type in [ROCK_TYPE, GROUND_TYPE, STEEL_TYPE]:
                        is_immune = True
                elif self.weather_name == "hail":
                    if pokemon.primary_type == ICE_TYPE:
                        is_immune = True
                
                if not is_immune:
                    dmg = pokemon.max_hp // 16
                    pokemon.hp -= dmg
                    messages.append(f"{pokemon.name} was buffeted by the {self.weather_name}!")

    def _apply_terrain_effects(self, messages: List[str], trainers: List['Trainer']) -> None:
        """Applies healing from Grassy Terrain."""
        if self.terrain_name == "grassy":
            for trainer in trainers:
                pokemon = trainer.get_active_pokemon()
                if pokemon.hp <= 0: continue

                # Check if grounded (not Flying type or holding Air Balloon - simplifed to type for now)
                is_grounded = pokemon.primary_type != FLYING_TYPE and pokemon.secondary_type != FLYING_TYPE
                
                if is_grounded:
                    heal = pokemon.max_hp // 16
                    pokemon.hp = min(pokemon.max_hp, pokemon.hp + heal)
                    messages.append(f"{pokemon.name} recovered some HP due to Grassy Terrain!")

    # --- Helpers for Damage Calculation ---
    def get_weather_object(self):
        return WEATHER_MAP.get(self.weather_name)
    
    def get_terrain_object(self):
        return TERRAIN_MAP.get(self.terrain_name)