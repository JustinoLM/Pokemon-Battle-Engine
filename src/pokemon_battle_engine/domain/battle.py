# src/pokemon_battle_engine/domain/battle.py

from .models import Pokemon, Move
from .status import ConfusionEffect, AttractEffect, BurnEffect, BadlyPoisonedEffect
from dataclasses import dataclass, field
import random
from .constants import STAGE_MULTIPLIERS, TERRAIN_MAP, WEATHER_MAP
from .constants import (
    POISON_TYPE, FLYING_TYPE, ROCK_TYPE, GROUND_TYPE, STEEL_TYPE, ICE_TYPE
)
from typing import Any, Optional, cast
from .errors import PokemonFaintedError, IllegalMoveError

from .items_effects import (
    LifeOrbStrategy, RockyHelmetStrategy, ThroatSprayStrategy, ExpertBeltStrategy,
    TypeEnhancingStrategy, WeaknessPolicyStrategy, FocusSashStrategy, LeftoversStrategy,
    BlackSludgeStrategy, FlameOrbStrategy, ToxicOrbStrategy, LumBerryStrategy,
    SitrusBerryStrategy
    )

from .field import FieldSide

from .field_conditions import BattleField

# --- Pokemon Teams and methods ---
@dataclass
class Team():
    members: list[Pokemon]
    active_pokemon_index: int = 0

    def get_active(self)-> Pokemon:
        return self.members[self.active_pokemon_index]
    
    def switch_pokemon(self, index: int) -> Pokemon:
        if 0 <= index < len(self.members):
            current_pokemon = self.members[self.active_pokemon_index]

            current_pokemon.clear_volatile_status()

            self.active_pokemon_index = index
            new_pokemon = self.members[index]
            
            if new_pokemon.hp > 0:
                return new_pokemon
            else:
                raise PokemonFaintedError(f"{new_pokemon.name} is fainted!!")
        else:
            raise IllegalMoveError("Invalid Pokemon index")

# --- Trainer class and methods ---
@dataclass
class Trainer():
    name: str
    team: Team

    def get_active_pokemon(self)-> Pokemon:
        return self.team.get_active() 

@dataclass
class TurnResult:
    attacker_name: str
    defender_name: str
    attacker_hp: int
    defender_hp: int
    damage: int
    is_ko: bool
    messages: list[str] = field(default_factory=list)
    effectivity: float = 1.0 

@dataclass
class Battle():
    trainer1: Trainer
    trainer2: Trainer
    turn_count: int = 0
    messages: list[str] = field(default_factory=list)

    # ---  Field Conditions (Weather/Terrain) ---
    conditions: BattleField = field(default_factory=BattleField)

    # ---  Field Sides ---
    side1: FieldSide = field(default_factory=FieldSide)
    side2: FieldSide = field(default_factory=FieldSide)

    # --- Helper: Apply Item Stat Modifiers ---
    def _get_stat_overrides(self, pokemon: Pokemon) -> dict[str, int]:
        overrides: dict[str, int] = {}
        if not pokemon.item:
            return overrides
        
        item = pokemon.item
        if item.is_stat_modifier:
            for stat_name in item.stats_to_modify:
                current_val = getattr(pokemon, stat_name)
                overrides[stat_name] = int(current_val * item.stat_multiplier)
    
        return overrides
    
    # --- Determine the order of the turns ---
    def pokemon_order(self, trainer1: Trainer, trainer2: Trainer)-> Trainer:
        trainer1_pokemon = trainer1.get_active_pokemon()
        trainer2_pokemon = trainer2.get_active_pokemon()

        trainer1_priority = trainer1_pokemon.current_move.priority if trainer1_pokemon.current_move else 0
        trainer2_priority = trainer2_pokemon.current_move.priority if trainer2_pokemon.current_move else 0
        
        # --- Priority Check ---
        if trainer1_priority > trainer2_priority:
            return trainer1
        elif trainer1_priority < trainer2_priority:
            return trainer2
        else:
            # ---  Speed Check ---
            trainer1_pokemon_speed = trainer1_pokemon.speed * STAGE_MULTIPLIERS.get(trainer1_pokemon.speed_stage, 1.0)
            trainer2_pokemon_speed = trainer2_pokemon.speed * STAGE_MULTIPLIERS.get(trainer2_pokemon.speed_stage, 1.0)

            if trainer1_pokemon_speed > trainer2_pokemon_speed:
                return trainer1
            elif trainer1_pokemon_speed < trainer2_pokemon_speed:
                return trainer2
            else:
                # --- Random Check ---
                return random.choice([trainer1, trainer2])
            
    # --- Helper for Confusion / Struggle Damage ---
    def _calculate_typeless_damage(self, attacker: Pokemon, power: int) -> int:
        # Fórmula simplificada Struggle/Confusion
        level_factor = 0.2 * (attacker.level + 1)
        bonuses = 0.01 * 1.0 * 92 * 1.0 # No STAB, No Effectivity
        
        # Usar Attack/SpAttack dependiendo de lo que sea mayor o fijo?
        # Struggle es física en gens antiguas, but usa el stat mas alto en modernas?
        # Vamos a asumir Física para simplificar "Struggle-like" behaviour
        atk = attacker.attack
        dfs = attacker.defense
        
        raw = power * level_factor * atk
        raw_def = dfs * 25
        
        dmg = bonuses * (raw/raw_def) + 2
        return int(dmg)

    # --- SWITCH METHOD ---
    async def execute_switch(self, trainer: Trainer, new_index: int) -> TurnResult:
        active_pokemon = trainer.get_active_pokemon()
        
        # Intentamos cambiar
        try:
            new_pokemon = trainer.team.switch_pokemon(new_index)
        except Exception as e:
            return TurnResult(
                attacker_name=trainer.name,
                defender_name="",
                attacker_hp=active_pokemon.hp,
                defender_hp=0,
                damage=0,
                is_ko=False,
                messages=[str(e)]
            )

        # Reset volatiles for the new pokemon (Turns on field = 0)
        new_pokemon.turns_on_field = 0
        
        # --- APPLY ENTRY HAZARDS ---
        # Determine which side the defender is coming in onto
        hazard_side = self.side2 if trainer == self.trainer1 else self.side1
    
        hazard_dmg, hazard_msgs = hazard_side.calculate_entry_hazard_damage(new_pokemon)
        hazard_damage = hazard_dmg
        self.messages.extend(hazard_msgs)

        return TurnResult(
            attacker_name=trainer.name,
            defender_name=new_pokemon.name,
            attacker_hp=active_pokemon.hp, # Old pokemon hp
            defender_hp=new_pokemon.hp,
            damage=hazard_damage,
            is_ko=(new_pokemon.hp <= 0),
            messages=self.messages
        )

    # ---  Turn by Turn Logic---
    async def execute_turn(self, attacker: Trainer, defender: Trainer, move: Move)->TurnResult:
        active_attacker = attacker.get_active_pokemon()
        active_defender = defender.get_active_pokemon()

        # 1. Validation
        self._validate_move_selection(active_attacker, move)

        # 2. Check Interruptions (Flinch, Status, Confusion)
        interruption = self._check_movement_interruptions(active_attacker, move)
        
        if interruption is True: # Failed to move
            return self._create_result(active_attacker, active_defender, 0, False)
        elif isinstance(interruption, int) and not isinstance(interruption, bool): # Confusion Self-Hit
            active_attacker.last_move_used = move
            return self._create_result(active_attacker, active_defender, interruption, active_attacker.hp <= 0)

        # 3. Handle Special/Non-Damaging Moves (Protect, Heal, Substitute)
        special_result = self._handle_special_moves(attacker, defender, move)
        if special_result:
            return special_result

        # --- SETUP FOR DAMAGING MOVES ---

        # Hazards & Environment
        if move.sets_hazard:
            target_side = self.side2 if attacker == self.trainer1 else self.side1
            target_side.add_hazard(move.sets_hazard)
            self.messages.append(f"{move.sets_hazard.capitalize()} were scattered on the ground!")

        if move.removes_hazards:
            if move.hazard_side == "user":
                user_side = self.side1 if attacker == self.trainer1 else self.side2
                user_side.clear_hazards()
                self.messages.append(f"{attacker.name} blew away hazards!")
            elif move.hazard_side == "target":
                target_side = self.side2 if attacker == self.trainer1 else self.side1
                target_side.clear_hazards()
                self.messages.append(f"{attacker.name} blew away hazards!")

        if move.sets_weather_to:
            msg = self.conditions.set_weather(move.sets_weather_to)
            self.messages.append(msg)
        if move.sets_terrain_to:
            msg = self.conditions.set_terrain(move.sets_terrain_to)
            self.messages.append(msg)
    
        # --- DAMAGE CALCULATION LOOP ---
        active_attacker.current_move = move

        # Proxies & Multi-hits
        attacker_overrides = self._get_stat_overrides(active_attacker)
        defender_overrides = self._get_stat_overrides(active_defender)
        proxy_attacker = _ModifiedPokemonView(active_attacker, attacker_overrides)
        proxy_defender = _ModifiedPokemonView(active_defender, defender_overrides)

        hits = 1
        if move.min_hits > 1:
            if active_attacker.item and active_attacker.item.name == "Loaded Dice":
                hits = move.max_hits
            else:
                hits = random.randint(move.min_hits, move.max_hits)
            self.messages.append(f"Hit {hits} time(s)!")

        # Calculate Loop
        total_damage = 0
        current_weather_obj = self.conditions.get_weather_object()
        current_terrain_obj = self.conditions.get_terrain_object()
        knock_off_multiplier = 1.5 if (move.removes_item and active_defender.item) else 1.0

        for _ in range(hits):
            hit_substitute = active_defender.substitute_hp > 0 and not move.is_sound
            
            hit_damage = move.execute(
                cast(Pokemon, proxy_attacker),
                cast(Pokemon, proxy_defender),
                weather=current_weather_obj,
                terrain=current_terrain_obj,
            )
            self.messages.extend(move.messages)
            
            if hit_substitute:
                damage_to_sub = min(hit_damage, active_defender.substitute_hp)
                active_defender.substitute_hp -= damage_to_sub
                total_damage += damage_to_sub
                self.messages.append("The substitute took damage!")
                if active_defender.substitute_hp == 0:
                    self.messages.append(f"{active_defender.name}'s substitute broke!")
                    hit_substitute = False 
            else:
                if move.removes_item and active_defender.item:
                    hit_damage = int(hit_damage * knock_off_multiplier)
                total_damage += hit_damage
            
            if active_defender.hp - total_damage <= 0 and active_defender.substitute_hp == 0:
                break

        # Check Miss
        if move.power > 0 and total_damage == 0:
            self.messages.append(f"{active_attacker.name}'s attack missed!")
            return self._create_result(active_attacker, active_defender, 0, False)

        # --- APPLY DAMAGE & REACTIONS ---
        
        # Modifiers
        attacker_modifier = ITEM_STRATEGIES.get(active_attacker.item.name) if active_attacker.item else None
        if attacker_modifier:
            total_damage = attacker_modifier.on_modify_damage(active_attacker, active_defender, move, total_damage)

        # Apply HP
        hp_before_damage = active_defender.hp
        if active_defender.substitute_hp > 0 and not move.is_sound:
            if active_defender.substitute_hp == 0:
                active_defender.hp -= total_damage
        else:
            active_defender.hp -= total_damage

        # Item Strategies (Life Orb, etc.)
        attacker_strategy = ITEM_STRATEGIES.get(active_attacker.item.name) if active_attacker.item else None
        if attacker_strategy:
            attacker_strategy.on_attack(active_attacker, active_defender, total_damage, self)

        defender_strategy = ITEM_STRATEGIES.get(active_defender.item.name) if active_defender.item else None
        if defender_strategy:
            defender_strategy.on_being_hit(active_attacker, active_defender, total_damage, hp_before_damage, self)
        
        # Razor Claw
        if active_attacker.item and active_attacker.item.name == "Razor Claw" and move.makes_contact:
             from .models import ModifyStage
             boost = ModifyStage(["crit_stage"], active_attacker.item.stage_boost_amount, target="self")
             boost.change_stage(active_attacker)

        # Secondary Effects (Status, Stat Changes)
        self._apply_secondary_effects(active_attacker, active_defender, move, total_damage)

        # Finalize
        active_attacker.last_move_used = move
        is_ko = active_defender.hp <= 0
        
        if is_ko:
            self.messages.append(f"{active_defender.name} fainted")
            active_defender.clear_volatile_status()

        return self._create_result(active_attacker, active_defender, total_damage, is_ko)


    # --- Validations and Interruptions ---
    def _validate_move_selection(self, attacker: Pokemon, move: Move) -> None:
        """Validates if the Pokemon can use the move (PP, legality)."""
        if attacker.move_pool and move not in attacker.move_pool:
            raise IllegalMoveError(f"{attacker.name} cannot learn {move.name}")

        if move.name not in attacker.pp_remaining:
            attacker.pp_remaining[move.name] = move.max_pp

        if attacker.pp_remaining[move.name] <= 0:
            # All PP exhausted for this move — caller should use Struggle instead
            raise IllegalMoveError(f"{move.name} has no PP left.")

        attacker.pp_remaining[move.name] -= 1

    def get_available_moves(self, pokemon: Pokemon) -> list[Move]:
        """Returns moves with PP remaining, or empty list if all PP exhausted (use Struggle)."""
        if not pokemon.move_pool:
            return []
        return [m for m in pokemon.move_pool if pokemon.pp_remaining.get(m.name, m.max_pp) > 0]

    def _check_movement_interruptions(self, attacker: Pokemon, move: Move) -> bool:
        """
        Checks if the Pokemon is prevented from moving (Flinch, Status, Confusion).
        Returns True if the turn should END immediately (failed move).
        """
        # 1. Flinch
        if attacker.flinch_chance >= 100:
            self.messages.append(f"{attacker.name} flinched!")
            attacker.flinch_chance = 0
            return True

        # 2. Major Status (Paralysis, Sleep, Freeze)
        if attacker.current_status_effect:
            if attacker.current_status_effect.prevents_movement(attacker):
                fail_message = attacker.current_status_effect.get_fail_message(attacker)
                self.messages.append(fail_message)
                return True

        # 3. Attraction
        if attacker.is_infatuated:
            if random.randint(1, 100) <= 50:
                self.messages.append(f"{attacker.name} is immobilized by love!")
                return True

        # 4. Confusion Self-Hit
        if isinstance(attacker.current_status_effect, ConfusionEffect):
            if random.randint(1, 100) <= 50:
                self.messages.append(f"{attacker.name} hurt itself in its confusion!")
                damage = self._calculate_typeless_damage(attacker, 40)
                attacker.hp -= damage
                # Note: We handle the return result in the main flow, 
                # but for this helper to work smoothly, we need access to defender.
                # Let's return a special "Self Damage" result or just handle logic here?
                # To keep it simple, let's return True (interrupt) and let main logic create result?
                # Better: Return the damage if self-hit, or None.
                return damage # Special return code for self-damage
        
        return False
    
    # --- Special Moves ---
    def _handle_special_moves(self, attacker: Trainer, defender: Trainer, move: Move) -> TurnResult | None:
        """
        Handles moves that don't deal standard damage (Heal, Substitute, Protect).
        Returns a TurnResult if the move was fully resolved here, None otherwise.
        """
        active_attacker = attacker.get_active_pokemon()
        active_defender = defender.get_active_pokemon()

        # Fake Out Check
        if move.name.lower() == "fake out":
            if active_attacker.turns_on_field > 0:
                self.messages.append(f"{active_attacker.name} used Fake Out! But it failed!")
                return self._create_result(active_attacker, active_defender, 0, False)
            move.priority = 1 # Fake Out logic

        # Apply Volatile Move Effects (Taunt, Encore, etc.)
        if move.special_effect:
            move.special_effect.apply(active_attacker, active_defender, self)

        # Protect
        if active_defender.protect_active:
            roll = random.randint(1, 100)
            success_threshold = active_defender.protect_chance * 100
            if roll <= success_threshold:
                self.messages.append(f"But {active_defender.name} protected itself! ")
                active_defender.protect_active = False
                return self._create_result(active_attacker, active_defender, 0, False)
            else:
                self.messages.append(f"{active_defender.name} protect failed! ")
                active_defender.protect_active = False

        # Healing Moves
        if move.is_heal:
            if active_attacker.hp == active_attacker.max_hp:
                self.messages.append(f"{active_attacker.name} is at full HP and didnt heal")
                return self._create_result(active_attacker, active_defender, 0, False)
            
            heal_amount = int(active_attacker.max_hp * move.heal_percentage)
            active_attacker.hp = min(active_attacker.max_hp, active_attacker.hp + heal_amount)
            self.messages.append(f"{active_attacker.name} recovered {heal_amount} HP")
            return self._create_result(active_attacker, active_defender, 0, False)

        # Substitute
        if move.is_substitute:
            cost = active_attacker.max_hp // 4
            if active_attacker.hp <= cost:
                self.messages.append(f"{active_attacker.name} doesn't have enough HP!")
                return self._create_result(active_attacker, active_defender, 0, False)
            
            active_attacker.hp -= cost
            active_attacker.substitute_hp = cost
            self.messages.append(f"{active_attacker.name} made a substitute!")
            active_attacker.last_move_used = move
            return self._create_result(active_attacker, active_defender, 0, False)

        # If none of the above triggered, return None to continue with damaging logic
        return None
    
    # --- Post Damages Effects ---
    def _apply_secondary_effects(self, attacker: Pokemon, defender: Pokemon, move: Move, total_damage: int) -> None:
        """Applies effects that happen after damage calculation (Knock Off, Status, Stat changes)."""
        
        # A. Knock Off (Remove Item)
        if move.removes_item and defender.item:
            self.messages.append(f"{attacker.name} knocked off {defender.name}'s {defender.item.name}!")
            defender.item = None

        # B. Trick / Switcheroo
        if move.swaps_item:
            temp_item = attacker.item
            attacker.item = defender.item
            defender.item = temp_item
            self.messages.append(f"{attacker.name} switched items with its foe!")

        # C. Status Infliction
        if move.secondary_effect and move.power > 0:
            has_covert_cloak = defender.item and defender.item.name == "Covert Cloak"
            if not has_covert_cloak:
                if random.randint(1,100) <= move.secondary_effect_chance:
                    defender.set_status(move.secondary_effect)
                    self.messages.append(f"{defender.name} was affected by the move's secondary effect!")
            else:
                self.messages.append(f"{defender.name}'s Covert Cloak protected it from the secondary effect!")

        # D. Stat Stage Changes are applied in Move.execute() for all moves.
        #    Here we only handle the Covert Cloak protection message.
        if move.stage_changes and move.power > 0:
            has_covert_cloak = defender.item and defender.item.name == "Covert Cloak"
            if has_covert_cloak:
                self.messages.append(f"{defender.name}'s Covert Cloak blocked the stat drop!")
    
    def _create_result(self, attacker: Pokemon, defender: Pokemon, damage: int, is_ko: bool) -> TurnResult:
        return TurnResult(
            attacker_name=attacker.name,
            defender_name=defender.name,
            attacker_hp=attacker.hp,
            defender_hp=max(0, defender.hp),
            damage=damage,
            is_ko=is_ko,
            messages=self.messages
        )
    
    # --- Battle End Checks ---
    def is_over(self) -> bool:
        t1_alive = any(p.hp > 0 for p in self.trainer1.team.members)
        t2_alive = any(p.hp > 0 for p in self.trainer2.team.members)
        return not t1_alive or not t2_alive

    def get_winner(self) -> Optional[Trainer]:
        t1_alive = any(p.hp > 0 for p in self.trainer1.team.members)
        t2_alive = any(p.hp > 0 for p in self.trainer2.team.members)
        if t1_alive and not t2_alive:
            return self.trainer1
        if t2_alive and not t1_alive:
            return self.trainer2
        return None

    # --- 13. Process status and such ---
    def process_end_of_turn(self) -> None:

        # Delegate Weather and Terrain logic to BattleField
        self.conditions.end_turn(self.messages, [self.trainer1, self.trainer2])

        # Pokemon Loop (Status, Volatile, Items)
        for trainer in [self.trainer1, self.trainer2]:
            p = trainer.get_active_pokemon()
            if p.hp <= 0:
                continue

            # --- VOLATILE STATUS DECAY ---
            p.tick_volatile_status(self.messages)

            # --- MAJOR STATUS EFFECTS ---
            if p.current_status_effect:
                msg = p.current_status_effect.tick(p)
                if msg:
                    self.messages.append(msg)
                if p.hp <= 0:
                    self.messages.append(f"{p.name} fainted!")

            # --- PASSIVE ITEMS ---
            item_strategy = ITEM_STRATEGIES.get(p.item.name) if p.item else None
            if item_strategy and hasattr(item_strategy, 'on_end_of_turn'):
                item_strategy.on_end_of_turn(p, self)

# --- Helper: Pokemon Proxy for Clean Stat Modification ---
class _ModifiedPokemonView:
    def __init__(self, pokemon: 'Pokemon', stat_overrides: dict[str, int]):
        self._pokemon = pokemon
        self._overrides = stat_overrides

    def __getattr__(self, name: str) -> Any:
        if name in self._overrides:
            return self._overrides[name]
        return getattr(self._pokemon, name)

    def __setattr__(self, name: str, value: Any) -> None:
        if name.startswith("_"):
            super().__setattr__(name, value)
        else:
            setattr(self._pokemon, name, value)

# Mapping Item Names to Strategies
ITEM_STRATEGIES = {
    "Life Orb": LifeOrbStrategy(),
    "Rocky Helmet": RockyHelmetStrategy(),
    "Throat Spray": ThroatSprayStrategy(),
    "Expert Belt": ExpertBeltStrategy(),
    "Focus Sash": FocusSashStrategy(),
    "Weakness Policy": WeaknessPolicyStrategy(),
    "Sitrus Berry": SitrusBerryStrategy(),
    "Lum Berry": LumBerryStrategy(),
    # Type Items (We use a single strategy class for all of them)
    "Black Belt": TypeEnhancingStrategy(),
    "Black Glasses": TypeEnhancingStrategy(),
    "Charcoal": TypeEnhancingStrategy(),
    "Dragon Fang": TypeEnhancingStrategy(),
    "Fairy Feather": TypeEnhancingStrategy(),
    "Hard Stone": TypeEnhancingStrategy(),
    "Magnet": TypeEnhancingStrategy(),
    "Metal Coat": TypeEnhancingStrategy(),
    "Miracle Seed": TypeEnhancingStrategy(),
    "Mystic Water":  TypeEnhancingStrategy(),
    "Never-Melt Ice": TypeEnhancingStrategy(),
    "Poison Barb": TypeEnhancingStrategy(),
    "Sharp Beak": TypeEnhancingStrategy(),
    "Silk Scarf": TypeEnhancingStrategy(),
    "Silver Powder": TypeEnhancingStrategy(),
    "Soft Sand": TypeEnhancingStrategy(),
    "Spell Tag": TypeEnhancingStrategy(),
    "Twisted Spoon": TypeEnhancingStrategy(),
    # End of turn objects
    "Leftovers": LeftoversStrategy(),
    "Black Sludge": BlackSludgeStrategy(),
    "Flame Orb": FlameOrbStrategy(),
    "Toxic Orb": ToxicOrbStrategy(),
}