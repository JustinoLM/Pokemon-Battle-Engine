# src/pokemon_battle_engine/domain/errors.py

class BattleError(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

class PokemonFaintedError(BattleError):
    ...

class IllegalMoveError(BattleError):
    ...

class TrainerNotFoundError(BattleError):
    ...
