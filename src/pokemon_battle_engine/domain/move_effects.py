# src/pokemon_battle_engine/domain/move_effects.py
from typing import Protocol, TYPE_CHECKING

if TYPE_CHECKING:
    from .models import Pokemon
    from .battle import Battle

class MoveEffect(Protocol):
    """Strategy interface for move-specific effects that aren't just damage."""
    
    def apply(self, user: 'Pokemon', target: 'Pokemon', battle: 'Battle') -> None:
        """
        Executes the special effect of the move.
        user: The Pokemon using the move.
        target: The opponent Pokemon.
        battle: The battle context (for messages, access to trainers, etc.).
        """
        ...

# --- Volatile Status Strategies ---

class TauntEffect:
    def apply(self, user: 'Pokemon', target: 'Pokemon', battle: 'Battle') -> None:
        target.is_taunted = True
        target.taunt_turns = 3
        battle.messages.append(f"{target.name} fell for the taunt!")

class EncoreEffect:
    def apply(self, user: 'Pokemon', target: 'Pokemon', battle: 'Battle') -> None:
        target.is_encored = True
        target.encore_move_name = target.current_move.name if target.current_move else ""
        target.encore_turns_left = 3
        battle.messages.append(f"{target.name} got trapped in an encore!")

class TormentEffect:
    def apply(self, user: 'Pokemon', target: 'Pokemon', battle: 'Battle') -> None:
        target.is_tormented = True
        battle.messages.append(f"{target.name} was tormented!")

class DisableEffect:
    def apply(self, user: 'Pokemon', target: 'Pokemon', battle: 'Battle') -> None:
        if target.current_move:
            target.last_move_used = target.current_move
        battle.messages.append(f"{target.name}'s move was disabled!")

class AttractEffect:
    def apply(self, user: 'Pokemon', target: 'Pokemon', battle: 'Battle') -> None:
        target.is_infatuated = True
        battle.messages.append(f"{target.name} fell in love!")

# --- Complex Interaction Strategies ---

class TrickEffect:
    """Swaps held items between user and target."""
    
    def apply(self, user: 'Pokemon', target: 'Pokemon', battle: 'Battle') -> None:
        if not user.item or not target.item:
            battle.messages.append("But it failed!")
        else:
            temp_item = user.item
            user.item = target.item
            target.item = temp_item
            battle.messages.append(f"{user.name} switched items with its foe!")