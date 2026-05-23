# src/pokemon_battle/domain/battle.py

from .models import Pokemon, Move
from dataclasses import dataclass, field
import random
from .constants import STAGE_MULTIPLIERS
from typing import  Optional

# --- Pokemon Teams and methods ---
@dataclass
class Team():
    members: list[Pokemon]
    active_pokemon_index: int = 0

    def get_active(self)-> Pokemon:
        return self.members[self.active_pokemon_index]
    
    def switch_pokemon(self, index: int) -> Pokemon:
        if 0<= index < 6:
            self.active_pokemon_index = index
            new_pokemon = self.members[index]
            if new_pokemon.hp > 0:
                return new_pokemon
            else:
                raise ValueError(f"{new_pokemon.name} is fainted!!")
        else:
            raise ValueError(f"Invalid Pokemon index")
        
# --- Trainer class and methods ---
@dataclass
class Trainer():
    name: str
    team: Team

    def get_active_pokemon(self)-> Pokemon:
        return self.team.get_active() 

# ---  Main Battle class ---
@dataclass
class TurnResult:
    attacker_name: str
    defender_name: str
    attacker_hp: int
    defender_hp: int
    damage: int
    is_ko: bool
    messages: list[str] = field(default_factory=list)

@dataclass
class Battle():
    trainer1: Trainer
    trainer2: Trainer
    turn_count: int = 0
    messages: list[str] = field(default_factory=list)

    #### Scaffolding
    weather: Optional[str] = None
    terrain: Optional[str] = None
    
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
            
    # ---  Turn by Turn Logic---
    def execute_turn(self, attacker: Trainer, defender: Trainer, move: Move)->TurnResult:
        active_attacker = attacker.get_active_pokemon()
        active_defender = defender.get_active_pokemon()

        # --- 1. verify Status ---
        if active_attacker.current_status_effect:
            if active_attacker.current_status_effect.prevents_movement(active_attacker):
                fail_message = active_attacker.current_status_effect.get_fail_message(active_attacker)
                self.messages.append(fail_message)

                return TurnResult(
                    attacker_name=active_attacker.name,
                    defender_name=active_defender.name,
                    attacker_hp=active_attacker.hp,
                    defender_hp=active_defender.hp,
                    damage=0, 
                    is_ko=False,
                    messages=self.messages
                )
            
		# --- 2. Execute Move ---
        
        active_attacker.current_move = move

        damage = move.execute(active_attacker, active_defender)
        self.messages.extend(move.messages)
        active_defender.hp -= damage

        self.turn_count += 1

        # --- 3. Verify KO---
        if active_defender.hp <= 0:
            self.messages.append(f"{active_defender.name} fainted")
            return TurnResult(
                attacker_name=active_attacker.name,
                defender_name=active_defender.name,
                attacker_hp=active_attacker.hp,
                defender_hp=max(0, active_defender.hp),
                damage=damage,
                is_ko=True,
                messages=self.messages
            )

        # --- 4. Missed attack message ---
        elif damage == 0:            
            if move.power > 0:
                self.messages.append(f"{active_attacker.name} attack has missed!")
                
        return TurnResult(
            attacker_name=active_attacker.name,
            defender_name=active_defender.name,
            attacker_hp=active_attacker.hp,
            defender_hp=active_defender.hp,
            damage=damage,
            is_ko=False,
            messages=self.messages
        )
    
    # --- 5. Process status and such ---
    def process_end_of_turn(self)-> None:
        for trainer in [self.trainer1, self.trainer2]:
            pokemon = trainer.get_active_pokemon()

            if pokemon.hp > 0 and pokemon.current_status_effect:
                status_message = pokemon.current_status_effect.tick(pokemon)
                self.messages.append(status_message)

                if pokemon.hp <= 0:
                    self.messages.append(f"{pokemon.name} fainted")