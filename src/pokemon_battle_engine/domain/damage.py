# src/pokemon_battle_engine/domain/damage.py
from __future__ import annotations

from typing import Protocol, TYPE_CHECKING, Optional
from .constants import STAGE_MULTIPLIERS, FIRE_TYPE, ICE_TYPE

if TYPE_CHECKING:
    from .models import Pokemon
    from .constants import Weather, Terrain

# --- Damage Calculators ---
class DamageCalculator(Protocol):
    def calculate(self,attacker: Pokemon,defender: Pokemon,power: int, stab: float, effectivity: float, is_critical: bool, weather: Optional['Weather']=None)->int:
        ...

class PhysicalDamageCalculator(DamageCalculator):
    def calculate(self,attacker: Pokemon,defender: Pokemon,power: int, stab: float, effectivity: float, is_critical: bool, weather: Optional['Weather']=None)->int:
        if is_critical:
            attack_multiplier = STAGE_MULTIPLIERS.get(max(0, attacker.attack_stage), 1.0)
            defense_multiplier = STAGE_MULTIPLIERS.get(min(0, defender.defense_stage), 1.0)
        else:
            attack_multiplier = STAGE_MULTIPLIERS.get(attacker.attack_stage, 1.0)
            defense_multiplier = STAGE_MULTIPLIERS.get(defender.defense_stage, 1.0)
        
        current_attacker_attack = attacker.attack
        if attacker.current_status_effect and "Burn" in str(type(attacker.current_status_effect)):
            current_attacker_attack = current_attacker_attack // 2
        
        level_factor = 0.2 * (attacker.level + 1)
        bonuses_factores = 0.01 * stab * 92 * effectivity

        final_attacker_attack = attack_multiplier * current_attacker_attack
        final_defender_defense = defense_multiplier * defender.defense

        final_raw_damage = power * level_factor * final_attacker_attack
        final_raw_defense = final_defender_defense * 25

        if weather:
            final_raw_damage *= weather.water_boost
            if weather.name == "rain" and attacker.primary_type == FIRE_TYPE:
                final_raw_damage = int(final_raw_damage * weather.fire_resist)
            if weather.name == "hail" and attacker.primary_type == ICE_TYPE:
                final_raw_damage = int(final_raw_damage * weather.ice_resist)

        total_damage = bonuses_factores * (final_raw_damage/final_raw_defense) +2
        
        if is_critical:
            total_damage *= 1.5

        return int(total_damage)

class SpecialDamageCalculator(DamageCalculator):
    def calculate(self,attacker: Pokemon,defender: Pokemon,power: int, stab: float, effectivity: float, is_critical: bool, weather: Optional['Weather']=None)->int:
        if is_critical:
            sp_attack_multiplier = STAGE_MULTIPLIERS.get(max(0, attacker.sp_attack_stage), 1.0)
            sp_defense_multiplier = STAGE_MULTIPLIERS.get(min(0, defender.sp_defense_stage), 1.0)
        else:
            sp_attack_multiplier = STAGE_MULTIPLIERS.get(attacker.sp_attack_stage, 1.0)
            sp_defense_multiplier = STAGE_MULTIPLIERS.get(defender.sp_defense_stage, 1.0)
        
        level_factor = 0.2 * (attacker.level + 1)
        bonuses_factores = 0.01 * stab * 92 * effectivity

        final_attacker_sp_attack = sp_attack_multiplier * attacker.sp_attack
        final_defender_sp_defense = sp_defense_multiplier * defender.defense

        final_raw_sp_damage = power * level_factor * final_attacker_sp_attack
        final_raw_sp_defense = final_defender_sp_defense * 25

        total_damage = bonuses_factores * (final_raw_sp_damage/final_raw_sp_defense) +2
        
        if is_critical:
            total_damage *= 1.5
                
        return int(total_damage)

class StatusDamageCalculator(DamageCalculator):
    def calculate(self,attacker: Pokemon,defender: Pokemon,power: int, stab: float, effectivity: float, is_critical: bool, weather: Optional['Weather']=None)->int:
        return 0