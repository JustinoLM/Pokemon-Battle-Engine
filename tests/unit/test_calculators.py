# tests/unit/test_calculators.py

import pytest

from src.pokemon_battle_engine.domain.models import (
    Move, PhysicalDamageCalculator, SpecialDamageCalculator,
)
from src.pokemon_battle_engine.domain.constants import NORMAL_TYPE


CALCULATORS = [PhysicalDamageCalculator, SpecialDamageCalculator]


@pytest.mark.parametrize("calc_cls", CALCULATORS)
def test_critical_hit_message(battle, calc_cls):
    attacker = battle.trainer1.get_active_pokemon()
    attacker.crit_stage = 4  # guarantees a critical hit

    move = Move(
        name="Tackle", power=40, move_type=NORMAL_TYPE,
        damage_calculator=calc_cls(),
        secondary_effect=None, secondary_effect_chance=0,
    )
    result = battle.execute_turn(battle.trainer1, battle.trainer2, move)

    assert any("CRITICAL" in msg for msg in result.messages)


@pytest.mark.parametrize("calc_cls", CALCULATORS)
def test_critical_multiplier_changes_damage(charmander, bulbasaur, calc_cls):
    calc = calc_cls()
    normal = calc.calculate(charmander, bulbasaur, 40, 1.0, 1.0, is_critical=False)
    critical = calc.calculate(charmander, bulbasaur, 40, 1.0, 1.0, is_critical=True)
    assert critical != normal


@pytest.mark.parametrize("calc_cls", CALCULATORS)
def test_sniper_ability_boosts_critical(sniper_vanilux, vanilux, calc_cls):
    calc = calc_cls()
    with_sniper = calc.calculate(sniper_vanilux, vanilux, 40, 1.0, 1.0, is_critical=True)
    without_sniper = calc.calculate(vanilux, sniper_vanilux, 40, 1.0, 1.0, is_critical=True)
    assert with_sniper != without_sniper
