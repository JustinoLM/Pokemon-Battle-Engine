# src/pokemon_battle_engine/domain/field.py
from dataclasses import dataclass, field
from typing import Optional
from .models import Pokemon
from .constants import POISON_TYPE, STEEL_TYPE, FLYING_TYPE, TYPE_CHART

@dataclass
class FieldSide:
    """Represents the conditions on one side of the battlefield (Trainer 1 or Trainer 2)."""
    
    # --- Hazard State ---
    spikes_layers: int = 0
    stealth_rock: bool = False
    toxic_spikes: int = 0
    # Future: Webs, Sticky Web, etc.

    # --- Hazard Logic ---

    def add_hazard(self, hazard_name: str) -> None:
        """Adds a layer of hazard."""
        if hazard_name == "spikes":
            if self.spikes_layers < 3:
                self.spikes_layers += 1
        elif hazard_name == "stealth_rock":
            self.stealth_rock = True
        elif hazard_name == "toxic_spikes":
            if self.toxic_spikes < 2:
                self.toxic_spikes += 1

    def clear_hazards(self) -> None:
        """Removes all hazards (Rapid Spin, Defog)."""
        self.spikes_layers = 0
        self.stealth_rock = False
        self.toxic_spikes = 0

    def calculate_entry_hazard_damage(self, pokemon: Pokemon) -> tuple[int, list[str]]:
        """
        Calculates damage and messages when a Pokemon switches in.
        Returns (total_damage, list_of_messages).
        """
        total_damage = 0
        messages = []

        # 1. Stealth Rock
        if self.stealth_rock:
            # Calculate type effectiveness
            eff_1 = TYPE_CHART.get("Rock", {}).get(pokemon.primary_type.name, 1.0)
            eff_2 = 1.0
            if pokemon.secondary_type:
                eff_2 = TYPE_CHART.get("Rock", {}).get(pokemon.secondary_type.name, 1.0)
            
            final_eff = eff_1 * eff_2
            dmg = int((pokemon.max_hp * final_eff) / 8)
            pokemon.hp -= dmg
            total_damage += dmg
            messages.append(f"Pointed stones dug into {pokemon.name}!")

        # 2. Spikes
        is_flying = pokemon.primary_type == FLYING_TYPE or pokemon.secondary_type == FLYING_TYPE
        if not is_flying and self.spikes_layers > 0:
            fractions = {1: 1/8, 2: 1/6, 3: 1/4}
            fraction = fractions.get(self.spikes_layers, 1/8)
            dmg = int(pokemon.max_hp * fraction)
            pokemon.hp -= dmg
            total_damage += dmg
            messages.append(f"{pokemon.name} was hurt by the spikes!")

        # 3. Toxic Spikes
        if not is_flying and self.toxic_spikes > 0 and not pokemon.current_status_effect:
            # Check absorption
            is_poison = pokemon.primary_type == POISON_TYPE or pokemon.secondary_type == POISON_TYPE
            is_steel = pokemon.primary_type == STEEL_TYPE or pokemon.secondary_type == STEEL_TYPE
            
            if is_poison or is_steel:
                # Remove the spikes
                self.toxic_spikes = 0
                messages.append(f"{pokemon.name} absorbed the Toxic Spikes!")
            else:
                # Apply Poison (1 layer = Poison, 2 layers = Badly Poisoned)
                from .models import BadlyPoisonedEffect # Import here to avoid circular dependency with models
                pokemon.set_status(BadlyPoisonedEffect())
                messages.append(f"{pokemon.name} was poisoned!")

        return total_damage, messages