# tests/unit/test_battle.py

import asyncio
from unittest.mock import patch, MagicMock, ANY

import pytest

from src.pokemon_battle_engine.domain.models import (
    Type, Move, StatusEffect,
)
from src.pokemon_battle_engine.domain.damage import PhysicalDamageCalculator
from src.pokemon_battle_engine.domain.errors import IllegalMoveError
from src.pokemon_battle_engine.domain.constants import NORMAL_TYPE


def test_team_switch_pokemon(dead_team):
    team = dead_team

    pkmn = team.switch_pokemon(0)
    assert pkmn.name == "Charmander"

    with pytest.raises(IllegalMoveError):
        team.switch_pokemon(999)

    with pytest.raises(Exception):
        team.switch_pokemon(1)  # index 1 is dead_pikachu → PokemonFaintedError


def test_get_active_pokemon(ash):
    assert ash.get_active_pokemon().name == "Charmander"


def test_battle_executes_turn_and_updates_hp(battle):
    tackle = Move("Tackle", 40, NORMAL_TYPE, PhysicalDamageCalculator())
    defender = battle.trainer2.get_active_pokemon()
    old_hp = defender.hp

    result = asyncio.run(battle.execute_turn(battle.trainer1, battle.trainer2, tackle))

    assert defender.hp < old_hp


def test_battle_pokemon_fainted(battle):
    tackle = Move("Tackle", 9000, NORMAL_TYPE, PhysicalDamageCalculator())
    result = asyncio.run(battle.execute_turn(battle.trainer1, battle.trainer2, tackle))
    assert any("fainted" in msg for msg in result.messages)


# --- Turn order: speed and priority -------------------------------------------
@pytest.mark.parametrize("speed1, speed2, prio1, prio2, winner", [
    (100, 50, 0, 0, "t1"),   # faster speed wins
    (50, 100, 0, 0, "t2"),
    (50, 100, 10, 0, "t1"),  # higher priority overrides slower speed
    (50, 100, 0, 10, "t2"),
])
def test_pokemon_order(battle, speed1, speed2, prio1, prio2, winner):
    p1 = battle.trainer1.get_active_pokemon()
    p2 = battle.trainer2.get_active_pokemon()

    p1.speed, p2.speed = speed1, speed2
    p1.current_move = Move("Tackle", 40, NORMAL_TYPE,
                           PhysicalDamageCalculator(), priority=prio1)
    p2.current_move = Move("Tackle", 40, NORMAL_TYPE,
                           PhysicalDamageCalculator(), priority=prio2)

    first = battle.pokemon_order(battle.trainer1, battle.trainer2)
    expected = battle.trainer1 if winner == "t1" else battle.trainer2
    assert first == expected


def test_speed_tie_broken_randomly(battle):
    p1 = battle.trainer1.get_active_pokemon()
    p2 = battle.trainer2.get_active_pokemon()
    p1.speed = p2.speed = 50

    tackle = Move("Tackle", 40, NORMAL_TYPE, PhysicalDamageCalculator())
    p1.current_move = tackle
    p2.current_move = tackle

    with patch("random.choice", return_value=battle.trainer1):
        first = battle.pokemon_order(battle.trainer1, battle.trainer2)

    assert first == battle.trainer1


# --- Status interactions during a turn ----------------------------------------
def test_status_prevents_movement(battle):
    attacker = battle.trainer1.get_active_pokemon()

    status = MagicMock()
    status.prevents_movement.return_value = True
    status.get_fail_message.return_value = f"{attacker.name} is paralyzed!"
    attacker.current_status_effect = status

    move = Move("Tackle", 40, Type("Normal"), PhysicalDamageCalculator())
    result = asyncio.run(battle.execute_turn(battle.trainer1, battle.trainer2, move))

    assert result.damage == 0
    assert f"{attacker.name} is paralyzed!" in result.messages
    status.prevents_movement.assert_called_once_with(attacker)
    status.get_fail_message.assert_called_once_with(attacker)


def test_missing_attack(battle):
    attacker = battle.trainer1.get_active_pokemon()

    move = Move(
        name="Tackle", power=40, move_type=Type("Normal"),
        damage_calculator=PhysicalDamageCalculator(),
        secondary_effect=ANY, secondary_effect_chance=ANY,
        stage_changes=ANY, accuracy=0,
    )
    result = asyncio.run(battle.execute_turn(battle.trainer1, battle.trainer2, move))

    assert result.damage == 0
    assert f"{attacker.name}'s attack missed!" in result.messages


def test_process_end_of_turn_calls_tick(battle):
    mock_status = MagicMock()
    mock_status.tick.return_value = "Taking damage!"
    active = battle.trainer1.get_active_pokemon()
    active.current_status_effect = mock_status

    battle.process_end_of_turn()

    mock_status.tick.assert_called_once_with(active)
    assert "Taking damage!" in battle.messages


def test_process_end_of_turn_fainted_by_status(battle):
    active = battle.trainer1.get_active_pokemon()
    active.hp = 1

    class InstantKillEffect(StatusEffect):
        def tick(self, pokemon):
            pokemon.hp = 0
            return "Killed instantly"

    active.current_status_effect = InstantKillEffect()
    battle.process_end_of_turn()

    assert active.hp == 0
    assert "fainted" in battle.messages[-1].lower()


def test_process_end_of_turn_ignores_dead_pokemon(battle):
    dead = battle.trainer1.get_active_pokemon()
    dead.hp = 0
    dead.current_status_effect = MagicMock()

    battle.process_end_of_turn()

    dead.current_status_effect.tick.assert_not_called()
