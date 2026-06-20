# src/pokemon_battle_engine/domain/items_effects.py

from typing import Protocol, TYPE_CHECKING
from abc import abstractmethod

if TYPE_CHECKING:
    from .models import Pokemon, Move, ConfusionEffect
    from .battle import Battle

# src/pokemon_battle_engine/domain/item_effects.py

class ItemEffect(Protocol):
    """Strategy interface for items..."""
    
    def on_attack(self, attacker: 'Pokemon', defender: 'Pokemon', damage: int, battle: 'Battle') -> None:
        ...

    def on_being_hit(self, attacker: 'Pokemon', defender: 'Pokemon', damage: int, hp_before_damage: int, battle: 'Battle') -> None:
        ...

    def on_modify_damage(self, attacker: 'Pokemon', defender: 'Pokemon', move: 'Move', raw_damage: int) -> int:
        ...

# --- Concrete Strategies ---

class LifeOrbStrategy:
    """Applies recoil damage to the attacker after dealing damage."""
    
    def on_attack(self, attacker: 'Pokemon', defender: 'Pokemon', damage: int, battle: 'Battle') -> None:
        if damage > 0:
            recoil = int(attacker.max_hp * 0.10)
            attacker.hp -= recoil
            battle.messages.append(f"{attacker.name} lost HP due to Life Orb!")

    def on_being_hit(self, attacker: 'Pokemon', defender: 'Pokemon', damage: int, hp_before_damage: int, battle: 'Battle') -> None:
        ...

    def on_modify_damage(self, attacker: 'Pokemon', defender: 'Pokemon', move: 'Move', raw_damage: int) -> int:
        return raw_damage

class RockyHelmetStrategy:
    """Deals recoil damage to the attacker if the move makes contact."""
    
    def on_attack(self, attacker: 'Pokemon', defender: 'Pokemon', damage: int, battle: 'Battle') -> None:
        ...

    def on_being_hit(self, attacker: 'Pokemon', defender: 'Pokemon', damage: int, hp_before_damage: int, battle: 'Battle') -> None:
        current_move = attacker.current_move
        
        if current_move and current_move.makes_contact:
            # Check for Protective Pads
            if not (attacker.item and attacker.item.name == "Protective Pads"):
                recoil = int(defender.max_hp * 0.1667)
                attacker.hp -= recoil
                battle.messages.append(f"{attacker.name} was hurt by Rocky Helmet!")

    def on_modify_damage(self, attacker: 'Pokemon', defender: 'Pokemon', move: 'Move', raw_damage: int) -> int:
        return raw_damage
    

class ThroatSprayStrategy:
    """Boosts Sp. Atk if the user used a sound move."""
    
    def on_attack(self, attacker: 'Pokemon', defender: 'Pokemon', damage: int, battle: 'Battle') -> None:
        # Access the move used via the attacker
        current_move = attacker.current_move
        
        if current_move and current_move.is_sound:
            from .models import ModifyStage
            
            boost = ModifyStage(["sp_attack"], 1, target="self")
            boost.change_stage(attacker)
            
            # Consume the item
            attacker.item = None 
            
            # Log to battle messages
            battle.messages.append(f"{attacker.name}'s Sp. Atk rose!")

    def on_being_hit(self, attacker: 'Pokemon', defender: 'Pokemon', damage: int, hp_before_damage: int, battle: 'Battle') -> None:
        pass

    def on_modify_damage(self, attacker: 'Pokemon', defender: 'Pokemon', move: 'Move', raw_damage: int) -> int:
        return raw_damage
    
# --- Damage Modifiers ---

class ExpertBeltStrategy:
    """Boosts damage of supereffective moves."""
    
    def on_modify_damage(self, attacker: 'Pokemon', defender: 'Pokemon', move: 'Move', raw_damage: int) -> int:
        # Check if the move is supereffective against the defender
        # We access the calculated effectivity stored in the move object during execution
        if move.current_effectivity > 1.0:
            return int(raw_damage * 1.2) # 20% boost
        return raw_damage

    def on_attack(self, attacker: 'Pokemon', defender: 'Pokemon', damage: int,  battle: 'Battle') -> None:
        pass

    def on_being_hit(self, attacker: 'Pokemon', defender: 'Pokemon', damage: int, hp_before_damage: int, battle: 'Battle') -> None:
        pass

class TypeEnhancingStrategy:
    """Generic strategy for items that boost a specific type (e.g., Charcoal, Mystic Water)."""
    
    def on_modify_damage(self, attacker: 'Pokemon', defender: 'Pokemon', move: 'Move', raw_damage: int) -> int:
        # The item object has the 'associated_type' field defined in items_registry.py
        if attacker.item and move.move_type == attacker.item.associated_type:
            return int(raw_damage * 1.2) # 20% boost
        return raw_damage

    def on_attack(self, attacker: 'Pokemon', defender: 'Pokemon', damage: int, battle: 'Battle') -> None:
        pass

    def on_being_hit(self, attacker: 'Pokemon', defender: 'Pokemon', damage: int, hp_before_damage: int, battle: 'Battle') -> None:
        pass

# --- Survival/Reactive Items ---

class FocusSashStrategy:
    """Prevents KO if at full HP."""
    
    def on_being_hit(self, attacker: 'Pokemon', defender: 'Pokemon', damage: int, hp_before_damage: int, battle: 'Battle') -> None:
        # Condition: Was at full HP before hit AND current HP <= 0 after damage calculation
        if hp_before_damage == defender.max_hp and (defender.hp - damage) <= 0:
            defender.hp = 1
            defender.item = None # Consume item
            battle.messages.append(f"{defender.name} hung on using Focus Sash!")

    def on_attack(self, attacker: 'Pokemon', defender: 'Pokemon', damage: int, battle: 'Battle') -> None:
        pass

    def on_modify_damage(self, attacker: 'Pokemon', defender: 'Pokemon', move: 'Move', raw_damage: int) -> int:
        return raw_damage

class WeaknessPolicyStrategy:
    """Boosts Atk/SpAtk by 2 stages if hit by a supereffective move."""
    
    def on_being_hit(self, attacker: 'Pokemon', defender: 'Pokemon', damage: int, hp_before_damage: int, battle: 'Battle') -> None:
        # Get the move used by the attacker
        current_move = attacker.current_move
        
        if current_move and current_move.current_effectivity > 1.0 and damage > 0:
            from .models import ModifyStage
            
            boost = ModifyStage(["attack", "sp_attack"], 2, target="self")
            boost.change_stage(defender)
            
            defender.item = None # Consume item
            battle.messages.append(f"{defender.name}'s Weakness Policy raised its stats!")

    def on_attack(self, attacker: 'Pokemon', defender: 'Pokemon', damage: int, battle: 'Battle') -> None:
        pass

    def on_modify_damage(self, attacker: 'Pokemon', defender: 'Pokemon', move: 'Move', raw_damage: int) -> int:
        return raw_damage

# --- Passive / End-of-Turn Strategies ---

class LeftoversStrategy:
    """Heals 1/16 HP at end of turn."""
    
    def on_end_of_turn(self, pokemon: 'Pokemon', battle: 'Battle') -> None:
        if pokemon.hp > 0: # Only heal if alive
            heal = int(pokemon.max_hp * 0.0625) # 1/16
            pokemon.hp = min(pokemon.max_hp, pokemon.hp + heal)
            battle.messages.append(f"{pokemon.name} recovered HP using Leftovers!")

    def on_attack(self, attacker: 'Pokemon', defender: 'Pokemon', damage: int, battle: 'Battle') -> None:
        pass

    def on_being_hit(self, attacker: 'Pokemon', defender: 'Pokemon', damage: int, hp_before_damage: int, battle: 'Battle') -> None:
        pass

    def on_modify_damage(self, attacker: 'Pokemon', defender: 'Pokemon', move: 'Move', raw_damage: int) -> int:
        return raw_damage

class BlackSludgeStrategy:
    """Heals Poison types, hurts others."""
    
    def on_end_of_turn(self, pokemon: 'Pokemon', battle: 'Battle') -> None:
        if pokemon.hp > 0:
            from .constants import POISON_TYPE
            
            is_poison = pokemon.primary_type == POISON_TYPE or pokemon.secondary_type == POISON_TYPE
            amount = int(pokemon.max_hp * 0.0625)
            
            if is_poison:
                pokemon.hp = min(pokemon.max_hp, pokemon.hp + amount)
                battle.messages.append(f"{pokemon.name} recovered HP using Black Sludge!")
            else:
                pokemon.hp -= amount
                battle.messages.append(f"{pokemon.name} was hurt by Black Sludge!")

    # ... (implementar pass para los otros métodos obligatorios) ...
    def on_attack(self, attacker: 'Pokemon', defender: 'Pokemon', damage: int, battle: 'Battle') -> None:
        pass
    def on_being_hit(self, attacker: 'Pokemon', defender: 'Pokemon', damage: int, hp_before_damage: int, battle: 'Battle') -> None:
        pass
    def on_modify_damage(self, attacker: 'Pokemon', defender: 'Pokemon', move: 'Move', raw_damage: int) -> int:
        return raw_damage

class FlameOrbStrategy:
    """Inflicts Burn at end of turn."""
    
    def on_end_of_turn(self, pokemon: 'Pokemon', battle: 'Battle') -> None:
        if pokemon.hp > 0 and not pokemon.current_status_effect:
            from .models import BurnEffect
            pokemon.set_status(BurnEffect())
            battle.messages.append(f"{pokemon.name}'s Flame Orb burned it!")

    # ... (pass methods) ...
    def on_attack(self, attacker: 'Pokemon', defender: 'Pokemon', damage: int, battle: 'Battle') -> None:
        pass
    def on_being_hit(self, attacker: 'Pokemon', defender: 'Pokemon', damage: int, hp_before_damage: int, battle: 'Battle') -> None:
        pass
    def on_modify_damage(self, attacker: 'Pokemon', defender: 'Pokemon', move: 'Move', raw_damage: int) -> int:
        return raw_damage

class ToxicOrbStrategy:
    """Inflicts Bad Poison at end of turn."""
    
    def on_end_of_turn(self, pokemon: 'Pokemon', battle: 'Battle') -> None:
        if pokemon.hp > 0 and not pokemon.current_status_effect:
            from .models import BadlyPoisonedEffect
            pokemon.set_status(BadlyPoisonedEffect())
            battle.messages.append(f"{pokemon.name}'s Toxic Orb badly poisoned it!")

    # ... (pass methods) ...
    def on_attack(self, attacker: 'Pokemon', defender: 'Pokemon', damage: int, battle: 'Battle') -> None:
        pass
    def on_being_hit(self, attacker: 'Pokemon', defender: 'Pokemon', damage: int, hp_before_damage: int, battle: 'Battle') -> None:
        pass
    def on_modify_damage(self, attacker: 'Pokemon', defender: 'Pokemon', move: 'Move', raw_damage: int) -> int:
        return raw_damage

# --- Reactive Items (On Hit) ---

class SitrusBerryStrategy:
    """Heals when HP drops below 50%. Triggered on being hit."""
    
    def on_being_hit(self, attacker: 'Pokemon', defender: 'Pokemon', damage: int, hp_before_damage: int, battle: 'Battle') -> None:
        threshold = int(defender.max_hp * 0.5)
        # Check if we crossed the threshold
        if hp_before_damage > threshold and defender.hp <= threshold:
            heal = int(defender.max_hp * 0.25)
            defender.hp = min(defender.max_hp, defender.hp + heal)
            defender.item = None
            battle.messages.append(f"{defender.name}'s Sitrus Berry restored its HP!")

    # ... (pass methods) ...
    def on_attack(self, attacker: 'Pokemon', defender: 'Pokemon', damage: int, battle: 'Battle') -> None:
        pass
    def on_being_hit(self, attacker: 'Pokemon', defender: 'Pokemon', damage: int, hp_before_damage: int, battle: 'Battle') -> None:
        pass
    def on_modify_damage(self, attacker: 'Pokemon', defender: 'Pokemon', move: 'Move', raw_damage: int) -> int:
        return raw_damage

# --- End-of-Turn Items ---

class LumBerryStrategy:
    """Cures status at end of turn."""
    
    def on_end_of_turn(self, pokemon: 'Pokemon', battle: 'Battle') -> None:
        if pokemon.current_status_effect:
            pokemon.current_status_effect = None
            pokemon.item = None
            battle.messages.append(f"{pokemon.name}'s Lum Berry cured its status!")

    # ... (pass methods) ...
    def on_attack(self, attacker: 'Pokemon', defender: 'Pokemon', damage: int, battle: 'Battle') -> None:
        pass
    def on_being_hit(self, attacker: 'Pokemon', defender: 'Pokemon', damage: int, hp_before_damage: int, battle: 'Battle') -> None:
        pass
    def on_modify_damage(self, attacker: 'Pokemon', defender: 'Pokemon', move: 'Move', raw_damage: int) -> int:
        return raw_damage

class MentalHerbStrategy:
    """Cures volatile status (Taunt, Encore, Torment, Attraction, Confusion)."""
    
    def on_end_of_turn(self, pokemon: 'Pokemon', battle: 'Battle') -> None:
        cured = False
        
        if pokemon.is_taunted:
            pokemon.is_taunted = False
            pokemon.taunt_turns = 0
            cured = True
        if pokemon.is_tormented:
            pokemon.is_tormented = False
            cured = True
        if pokemon.is_encored:
            pokemon.is_encored = False
            pokemon.encore_turns_left = 0
            cured = True
        if pokemon.is_infatuated:
            pokemon.is_infatuated = False
            cured = True
        if isinstance(pokemon.current_status_effect, (ConfusionEffect)):
            # Note: Attraction/Confusion are often volatile or mixed. 
            # Here we treat Confusion as curable by Mental Herb
            pokemon.current_status_effect = None
            cured = True
            
        if cured:
            pokemon.item = None
            battle.messages.append(f"{pokemon.name}'s Mental Herb snapped it out of its funk!")

    def on_attack(self, attacker: 'Pokemon', defender: 'Pokemon', damage: int, battle: 'Battle') -> None:
        pass
    def on_being_hit(self, attacker: 'Pokemon', defender: 'Pokemon', damage: int, hp_before_damage: int, battle: 'Battle') -> None:
        pass
    def on_modify_damage(self, attacker: 'Pokemon', defender: 'Pokemon', move: 'Move', raw_damage: int) -> int:
        return raw_damage

class KingsRockStrategy:
    """Chance to flinch target on contact."""
    
    def on_attack(self, attacker: 'Pokemon', defender: 'Pokemon', damage: int, battle: 'Battle') -> None:
        # Check if move made contact (passed via move object usually, but we check current_move)
        if attacker.current_move and attacker.current_move.makes_contact:
            battle.messages.append(f"{attacker.name}'s King's Rock makes the target flinch!")
            # Apply flinch for next turn
            defender.flinch_chance = 100 

    def on_end_of_turn(self, pokemon: 'Pokemon', battle: 'Battle') -> None:
        pass
    def on_being_hit(self, attacker: 'Pokemon', defender: 'Pokemon', damage: int, hp_before_damage: int, battle: 'Battle') -> None:
        pass
    def on_modify_damage(self, attacker: 'Pokemon', defender: 'Pokemon', move: 'Move', raw_damage: int) -> int:
        return raw_damage