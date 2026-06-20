# src/pokemon_battle_engine/services/battle_service.py

from pokemon_battle_engine.domain.battle import Battle, TurnResult
from pokemon_battle_engine.domain.errors import TrainerNotFoundError, IllegalMoveError


import asyncio

class BattleService:
    
    def __init__(self, battle: Battle):
        self.battle = battle
        # Lock to make sure if 2 HTTP came at the same time
        # One goes first then the other
        self._lock = asyncio.Lock()
    
    async def execute_turn(self, attacker_name: str, defender_name: str,move_name: str) -> TurnResult:
        # --- Search for trainers ---

        attacker = None
        defender = None

        # --- 1. Compare names to the ones on battle ---
        if self.battle.trainer1.name == attacker_name:
            attacker = self.battle.trainer1
            defender = self.battle.trainer2

        elif self.battle.trainer2.name == attacker_name:
            attacker = self.battle.trainer2
            defender = self.battle.trainer1

        if attacker is None:
            raise TrainerNotFoundError("Attack Trainer not found")
        
        # --- 2. Search the move used to execute the turn ---
        active_pokemon = attacker.get_active_pokemon()

        move_to_use = None
        for move in active_pokemon.move_pool:
            if move.name == move_name:
                move_to_use = move
                break
        
        if move_to_use is None:
            raise IllegalMoveError(f"{attacker.name} cannot learn {move_name}")

        # --- VALIDATION: Move Restrictions ---
        # 1. Taunt (Cannot use Status moves)
        if attacker.is_taunted and move_to_use.power == 0:
            raise IllegalMoveError(f"{attacker.name} is taunted! It can't use status moves!")
        # 2. Encore (Must use same move)
        if attacker.is_encored and move_to_use.name != attacker.encore_move_name:
            raise IllegalMoveError(f"{attacker.name} is encored! It must use {attacker.encore_move_name}!")
        # 3. Torment (Cannot use same move twice)
        if attacker.is_tormented and move_to_use.name == attacker.last_move_name:
            raise IllegalMoveError(f"{attacker.name} is tormented! It can't use {move_to_use.name}!")
    
        # --- 3. Lock and Deoegation ---
        # Nobody can touch the battle
        async with self._lock:
            result = await self.battle.execute_turn(attacker, defender, move_to_use)
        
        return result