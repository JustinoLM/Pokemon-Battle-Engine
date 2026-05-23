# src/pokemon_battle/domain/models.py

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import  Optional, Protocol, TYPE_CHECKING
from .constants import (
    TYPE_CHART, STAGE_MULTIPLIERS, Type,
	FAIRY_TYPE, FIRE_TYPE, FIGHTING_TYPE, FLYING_TYPE,
	BUG_TYPE, DARK_TYPE, DRAGON_TYPE, ELECTRIC_TYPE,
	GHOST_TYPE, GRASS_TYPE,GROUND_TYPE, ICE_TYPE,
	NORMAL_TYPE, POISON_TYPE, PSYCHIC_TYPE, ROCK_TYPE,
	STEEL_TYPE, WATER_TYPE, CRIT_CHANCE)
import random

if TYPE_CHECKING:
	...

# --- Main Pokemon class ---
@dataclass
class Pokemon():
	name: str
	level: int
	hp: int
	max_hp: int
	attack: int
	defense: int
	sp_attack: int
	sp_defense: int
	speed:int
	primary_type: Type
	secondary_type: Optional[Type] = None

	#Priority
	current_move: Optional['Move'] = None

	#Stages
	attack_stage: int = 0
	defense_stage: int = 0
	sp_attack_stage: int = 0
	sp_defense_stage: int = 0
	speed_stage: int = 0
	accuracy_stage: int = 0
	evasion_stage: int = 0
	crit_stage: int = 0

	#Status Conditions
	poison_turn_count: int = 0
	current_status_effect: Optional['StatusEffect'] = None
	status_turns_remaining: int = 0

	# --- Set status change like burns and so on ---
	def set_status(self, new_effect: 'StatusEffect')-> bool:
		if self.current_status_effect is None:
			self.current_status_effect = new_effect
			return True
		
		current_is_poison = isinstance(self.current_status_effect, PoisonEffect)
		new_effect_is_toxic = isinstance(new_effect, BadlyPoisonedEffect)
		if current_is_poison and new_effect_is_toxic:
			self.current_status_effect = new_effect
			return True
		
		return False


	#### Scaffolding
	item: Optional[str] = None
	ability: Optional[str] = None
	ivs: dict[str, int] = field(default_factory=lambda: {"hp": 0, "atk": 0, "def": 0, "spa": 0, "spd": 0, "spe": 0})
	move_pool: list['Move'] = field(default_factory=list)

# --- Changes to the attacks eg. swords dance ---
class StageChange(ABC):
	@abstractmethod
	def change_stage(self, pokemon: Pokemon)-> str:
		...

class ModifyStage(StageChange):
	def __init__(self, stats: list[str], amount: int, target: str = "self"):
		self.stats = stats
		self.amount = amount
		self.target = target

	def change_stage(self, target_pokemon: Pokemon) -> str:
		message_parts = []
		any_changed = False
        
		for stat in self.stats:
			current_stage = getattr(target_pokemon, f"{stat}_stage")
			new_stage_value = max(-6, min(6, current_stage + self.amount))
            
			if current_stage == new_stage_value:
				direction = "higher" if self.amount > 0 else "lower"
				message_parts.append(f"{stat} won't go {direction}!")
			else:
				message_parts.append(f"{stat}")
				setattr(target_pokemon, f"{stat}_stage", new_stage_value)
				any_changed = True
        
		stat_list = " and ".join(message_parts)
        
		if any_changed:
			verb = 'rose' if self.amount > 0 else 'fell'
			return f"{target_pokemon.name}'s {stat_list} {verb}!"
		else:
			return f"{target_pokemon.name}'s {stat_list}!"

# --- Damage Calculators ---
class DamageCalculator(Protocol):
	def calculate(self,attacker: Pokemon,defender: Pokemon,power: int, stab: float, effectivity: float, is_critical: bool)->int:
		...

class PhysicalDamageCalculator(DamageCalculator):
	def calculate(self,attacker: Pokemon,defender: Pokemon,power: int, stab: float, effectivity: float, is_critical: bool)->int:
		# --- Verify crit ---
		if is_critical:
			attack_multiplier = STAGE_MULTIPLIERS.get(max(0, attacker.attack_stage), 1.0)
			defense_multiplier = STAGE_MULTIPLIERS.get(min(0, defender.defense_stage), 1.0)
		else:
			attack_multiplier = STAGE_MULTIPLIERS.get(attacker.attack_stage, 1.0)
			defense_multiplier = STAGE_MULTIPLIERS.get(defender.defense_stage, 1.0)
		
		# --- Burnt penalization ---
		current_attacker_attack = attacker.attack
		if attacker.current_status_effect and "Burn" in str(type(attacker.current_status_effect)):
			current_attacker_attack = current_attacker_attack // 2
		
		# --- Variables ---
		level_factor = 0.2 * (attacker.level + 1)
		bonuses_factores = 0.01 * stab * 92 * effectivity

		final_attacker_attack = attack_multiplier * current_attacker_attack
		final_defender_defense = defense_multiplier * defender.defense

		final_raw_damage = power * level_factor * final_attacker_attack
		final_raw_defense = final_defender_defense * 25

		# --- Final Damage  and critical hit applier ---
		total_damage = bonuses_factores * (final_raw_damage/final_raw_defense) +2
		
		if is_critical:
			if attacker.ability == "Sniper":
				total_damage *= 2.25
			else:
				total_damage *= 1.5

		return int(total_damage)


class SpecialDamageCalculator(DamageCalculator):
	def calculate(self,attacker: Pokemon,defender: Pokemon,power: int, stab: float, effectivity: float, is_critical: bool)->int:
		# --- Verify crit ---
		if is_critical:
			sp_attack_multiplier = STAGE_MULTIPLIERS.get(max(0, attacker.sp_attack_stage), 1.0)
			sp_defense_multiplier = STAGE_MULTIPLIERS.get(min(0, defender.sp_defense_stage), 1.0)
		else:
			sp_attack_multiplier = STAGE_MULTIPLIERS.get(attacker.sp_attack_stage, 1.0)
			sp_defense_multiplier = STAGE_MULTIPLIERS.get(defender.sp_defense_stage, 1.0)
		
		# --- Variables ---
		level_factor = 0.2 * (attacker.level + 1)
		bonuses_factores = 0.01 * stab * 92 * effectivity

		final_attacker_sp_attack = sp_attack_multiplier * attacker.sp_attack
		final_defender_sp_defense = sp_defense_multiplier * defender.defense

		final_raw_sp_damage = power * level_factor * final_attacker_sp_attack
		final_raw_sp_defense = final_defender_sp_defense * 25

		# --- Final Damage  and critical hit applier ---
		total_damage = bonuses_factores * (final_raw_sp_damage/final_raw_sp_defense) +2
		
		if is_critical:
			if attacker.ability == "Sniper":
				total_damage *= 2.25
			else:
				total_damage *= 1.5
				
		return int(total_damage)

class StatusDamageCalculator(DamageCalculator):
	def calculate(self,attacker: Pokemon, defender: Pokemon, power: int, stab: float, effectivity: float, is_critical: bool)->int:
		return 0

# --- Main Status Effects appliers ---
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

# --- Main Move class ---
@dataclass
class Move():
	name: str
	power: int
	move_type: Type
	damage_calculator: DamageCalculator
	secondary_effect: Optional[StatusEffect] = None
	secondary_effect_chance: int = 0
	stage_changes: list[ModifyStage] = field(default_factory=list)
	accuracy: int = 100
	priority: int = 0
	messages: list[str] = field(default_factory=list)

	# --- What happens when a move is activated  ---
	def execute(self, attacker: Pokemon, defender: Pokemon) -> int:
		self.messages = [] 
		roll = random.randint(1,100)

		# --- Check if it miss  ---
		active_accuracy = self.accuracy * (STAGE_MULTIPLIERS.get(attacker.accuracy_stage, 1.0)/STAGE_MULTIPLIERS.get(defender.evasion_stage, 1.0))
		if roll > active_accuracy:
			return 0
		
		else:
			# --- Check for buffs or debuffs  ---
			if self.stage_changes:
				for change_strategy in self.stage_changes:
					effect_target = defender if change_strategy.target == "opponent" else attacker
					change_stage_message = change_strategy.change_stage(effect_target)
					self.messages.append(change_stage_message)

			# --- Critical hit logic ---
			current_crit_stage = max(0, min(4, attacker.crit_stage))
			critical_chance = CRIT_CHANCE.get(current_crit_stage, 4.17)

			is_critical = random.randint(1,100) <= critical_chance

			# ---  Same Type Attack Bonus ---
			if attacker.primary_type == self.move_type or attacker.secondary_type == self.move_type:
				stab = 1.5
			else:
				stab = 1.0

			# --- Calculate Resistances, Weaknesses and inmunities ---
			effectivity = self._calculate_effectivity(defender=defender)

			# ---  Main damage function and secondary effect applier ---
			damage_dealt = self.damage_calculator.calculate(
				attacker = attacker, 
				defender = defender, 
				power = self.power, 
				stab = stab, 
				effectivity=effectivity,
				is_critical=is_critical
				)

			if self.secondary_effect:
				if random.randint(1,100) <= self.secondary_effect_chance:
					defender.set_status(self.secondary_effect)
			
			# --- Apply critical hit ---
			if is_critical and self.power >0:
				self.messages.append("CRITICAL HIT !!!")

			return int(damage_dealt)
	
	# --- Function to calculare weakneasess, resistances and inmunities  ---
	def _calculate_effectivity(self, defender: Pokemon) -> float:
		move_type_name = self.move_type.name
		defender_type = defender.primary_type.name
		primary_effectiveness = TYPE_CHART.get(move_type_name,{}).get(defender_type,1.0)

		secondary_effectiveness = 1.0
		if defender.secondary_type is not None:
			defender_secondary_type = defender.secondary_type.name
			secondary_effectiveness = TYPE_CHART.get(move_type_name,{}).get(defender_secondary_type,1.0)

		return primary_effectiveness * secondary_effectiveness