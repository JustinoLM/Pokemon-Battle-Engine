# src/pokemon_battle_engine/domain/models.py

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import  Optional, Protocol, TYPE_CHECKING
from .constants import (
    TYPE_CHART, STAGE_MULTIPLIERS, Type,
    FIRE_TYPE, FLYING_TYPE,
    DRAGON_TYPE, ELECTRIC_TYPE,
    GRASS_TYPE,ICE_TYPE,
    POISON_TYPE, PSYCHIC_TYPE, CRIT_CHANCE, Weather, Terrain
    )
import random

from .move_effects import MoveEffect
from .status import StatusEffect, PoisonEffect, BadlyPoisonedEffect
from .damage import  DamageCalculator

if TYPE_CHECKING:
    from .battle import Trainer, Battle

# --- Main Pokemon class ---
@dataclass
class Pokemon():
    # -- Pokemons identity --
    name: str
    level: int

    # -- Base Stats from API  --
    base_hp: int
    base_attack: int
    base_defense: int
    base_sp_attack: int
    base_sp_defense: int
    base_speed:int
    primary_type: Type
    secondary_type: Optional[Type] = None


    # -- Calculated stats --
    hp: int = field(init=False)
    max_hp: int = field(init=False)
    attack: int = field(init=False)
    defense: int = field(init=False)
    sp_attack: int = field(init=False)
    sp_defense: int = field(init=False)
    speed:int = field(init=False)

    # -- Battle State --
    current_move: Optional['Move'] = None
    pp_remaining: dict[str, int] = field(default_factory=dict)
    last_move_used: Optional['Move'] = None # For Encore/Torment tracking

    # - Stages -
    attack_stage: int = 0
    defense_stage: int = 0
    sp_attack_stage: int = 0
    sp_defense_stage: int = 0
    speed_stage: int = 0
    accuracy_stage: int = 0
    evasion_stage: int = 0
    crit_stage: int = 0

    # - Status -
    poison_turn_count: int = 0
    current_status_effect: Optional['StatusEffect'] = None
    status_turns_remaining: int = 0

    # - Effective Moves Flags -
    reflect_active: bool = field(init=False, default=False)
    light_screen_active: bool = field(init=False, default=False)

    # -  Protect Logic -
    protect_active: bool = field(init=False, default=False)
    protect_count: int = 0 # Para manejar el decay de probabilidad
    protect_chance: float = field(init=False, default=1.0)

    # --- NEW: Volatile Conditions Flags & Counters ---
    is_taunted: bool = False
    taunt_turns: int = 0
    
    is_encored: bool = False
    encore_move_name: Optional[str] = None
    encore_turns_left: int = 0
    
    is_tormented: bool = False
    torment_turns_left: int = 0 #

    is_infatuated: bool = False        
    attract_target: Optional['Trainer'] = None
    infatuate_turns_left: int = 0 

    is_trapped: bool = False          
    trap_damage_per_turn: int = 0
    trap_move_name: str = "trap"
    trap_turns_left: int = 0

    is_rooted: bool = False           
    rooted_turns_left: int = 0

    flinch_chance: int = 0

    # --- Substitute & Fake Out ---
    substitute_hp: int = 0 # 0 means no substitute
    turns_on_field: int = 0 

    # -- Customization --
    ivs: dict[str, int] = field(default_factory=lambda:{
        "hp":31, "atk": 31, "def": 31,
        "spa":31, "spd": 31, "spe": 31
    })

    # -- Use Item --
    item: Optional['Item'] = None
    move_pool: list['Move'] = field(default_factory=list)

    def __post_init__(self) -> None:
        # --- Helper to calculate stats ---
        def calculate_stats(base: int, iv_key: str)-> int:
            iv = self.ivs.get(iv_key,31)
            stat = ((2* base + iv) * self.level) / 105
            return int(stat)
        
        def calculate_hp(base: int, iv_key: str)-> int:
            iv = self.ivs.get(iv_key,31)
            hp_stat = ((2* base + iv) * self.level) / 110 + self.level
            return int(hp_stat)
        
        self.hp = calculate_hp(self.base_hp,"hp")
        self.max_hp = self.hp
        self.attack = calculate_stats(self.base_attack, "atk")
        self.defense = calculate_stats(self.base_defense, "def")
        self.sp_attack = calculate_stats(self.base_sp_attack, "spa")
        self.sp_defense = calculate_stats(self.base_sp_defense, "spd")
        self.speed = calculate_stats(self.base_speed, "spe")

    # --- Reset Volatile Status (Used on Switch) ---
    def clear_volatile_status(self) -> None:
        self.is_taunted = False
        self.taunt_turns = 0
        self.is_encored = False
        self.encore_move_name = None
        self.encore_turns_left = 0
        self.is_tormented = False
        self.torment_turns_left = 0
        self.is_infatuated = False
        self.attract_target = None
        self.infatuate_turns_left = 0
        self.is_trapped = False
        self.trap_turns_left = 0
        self.is_rooted = False
        self.rooted_turns_left = 0
        self.substitute_hp = 0
        self.protect_active = False
        self.protect_count = 0
        self.flinch_chance = 0

    def tick_volatile_status(self, messages: list[str]) -> None:
        """
        Reduces turn counters for volatile conditions (Taunt, Encore, etc.)
        Returns None, appends messages if needed.
        """
        if self.hp <= 0: return

        # Taunt
        if self.taunt_turns > 0:
            self.taunt_turns -= 1
            if self.taunt_turns <= 0:
                self.is_taunted = False
                
        # Encore
        if self.encore_turns_left > 0:
            self.encore_turns_left -= 1
            if self.encore_turns_left <= 0:
                self.is_encored = False
                self.encore_move_name = None
                
        # Torment
        if self.torment_turns_left > 0:
            self.torment_turns_left -= 1
            if self.torment_turns_left <= 0:
                self.is_tormented = False
                
        # Infatuation
        if self.infatuate_turns_left > 0:
            self.infatuate_turns_left -= 1
            if self.infatuate_turns_left <= 0:
                self.is_infatuated = False

    # --- Set status change ---
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

# --- Changes to the attacks ---
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
    max_pp: int = 10
    messages: list[str] = field(default_factory=list)

    is_protect: bool = False
    is_heal: bool = False
    heal_percentage : float = 0.5
    is_screen : bool = False

    is_sound: bool = False       
    makes_contact: bool = False  
    has_secondary_effect: bool = False 
    flinch_chance: int = 0       
    current_effectivity: float = 1.0 
    battle: Optional['Battle'] = None

    # --- Multi-Hit ---
    min_hits: int = 1
    max_hits: int = 1
    
    # --- Weather / Terrain ---
    sets_weather_to: Optional[Weather] = None
    sets_terrain_to: Optional[Terrain] = None

    # --- Item Interaction ---
    removes_item: bool = False 
    swaps_item: bool = False   

    # --- Hazards & Utility ---
    sets_hazard: Optional[str] = None # "spikes", "stealth_rock", "toxic_spikes"
    removes_hazards: bool = False     # Rapid Spin / Defog
    hazard_side: Optional[str] = None # "user" (Rapid Spin) or "target" (Defog)
    
    # --- Substitute ---
    is_substitute: bool = False

    # --- NEW: Special Effect Strategy
    special_effect: Optional['MoveEffect'] = None

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Move):
            return False
        return self.name == other.name

    def __hash__(self) -> int:
        return hash(self.name)

    def execute(self, attacker: Pokemon, defender: Pokemon, weather: Optional[Weather]=None, terrain: Optional[Terrain]=None) -> int:
        self.messages = [] 
        roll = random.randint(1,100)

        active_accuracy = self.accuracy * (STAGE_MULTIPLIERS.get(attacker.accuracy_stage, 1.0)/STAGE_MULTIPLIERS.get(defender.evasion_stage, 1.0))
        if roll > active_accuracy:
            return 0
        
        else:
            if self.stage_changes:
                for change_strategy in self.stage_changes:
                    effect_target = defender if change_strategy.target == "opponent" else attacker
                    change_stage_message = change_strategy.change_stage(effect_target)
                    self.messages.append(change_stage_message)

            current_crit_stage = max(0, min(4, attacker.crit_stage))
            critical_chance = CRIT_CHANCE.get(current_crit_stage, 4.17)
            is_critical = random.randint(1,100) <= critical_chance

            if attacker.primary_type == self.move_type or attacker.secondary_type == self.move_type:
                stab = 1.5
            else:
                stab = 1.0

            effectivity = self._calculate_effectivity(defender=defender)
            self.current_effectivity = effectivity

            terrain_multiplier = 1.0
            if terrain:
                is_grounded = attacker.primary_type != FLYING_TYPE and attacker.secondary_type != FLYING_TYPE
                if is_grounded:
                    if terrain.electric_boost and self.move_type == ELECTRIC_TYPE:
                        terrain_multiplier = 1.5
                    elif terrain.grassy_boost and self.move_type == GRASS_TYPE:
                        terrain_multiplier = 1.5
                    elif terrain.psychic_boost and self.move_type == PSYCHIC_TYPE:
                        terrain_multiplier = 1.5
                    elif terrain.misty_boost and self.move_type == DRAGON_TYPE:
                        terrain_multiplier = 0.5

            damage_dealt = self.damage_calculator.calculate(
                attacker = attacker, 
                defender = defender, 
                power = self.power, 
                stab = stab, 
                effectivity=effectivity * terrain_multiplier, 
                is_critical=is_critical,
                weather=weather
                )
            
            if is_critical and self.power >0:
                self.messages.append("CRITICAL HIT !!!")

            return int(damage_dealt)
    
    def _calculate_effectivity(self, defender: Pokemon) -> float:
        move_type_name = self.move_type.name
        defender_type = defender.primary_type.name
        primary_effectiveness = TYPE_CHART.get(move_type_name,{}).get(defender_type,1.0)

        secondary_effectiveness = 1.0
        if defender.secondary_type is not None:
            defender_secondary_type = defender.secondary_type.name
            secondary_effectiveness = TYPE_CHART.get(move_type_name,{}).get(defender_secondary_type,1.0)

        return primary_effectiveness * secondary_effectiveness

# --- Item Model ---
@dataclass
class Item:
    name: str
    is_stat_modifier: bool = False      
    is_passive_heal: bool = False       
    is_recoil_damage: bool = False     
    is_consumable: bool = False        
    is_self_status: bool = False
    is_protective: bool = False         

    stats_to_modify: list[str] = field(default_factory=list) 
    stat_multiplier: float = 1.0        
    stage_boost_amount: int = 0         

    type_boost_multiplier: float = 1.0  
    associated_type: Optional['Type'] = None 
    
    recoil_percent: float = 0.0         
    passive_heal_percent: float = 0.0   
    heal_threshold_percent: float = 0.5 
    
    makes_contact_recoil: bool = False 
    requires_sound_move: bool = False  
    requires_contact: bool = False     