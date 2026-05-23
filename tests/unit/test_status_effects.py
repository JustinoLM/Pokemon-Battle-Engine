# tests/unit/test_status_effects.py

from unittest.mock import patch

import pytest

from src.pokemon_battle_engine.domain.models import (
    BurnEffect, ParalyzeEffect, SleepEffect, FreezeEffect,
    PoisonEffect, BadlyPoisonedEffect,
    PhysicalDamageCalculator, Pokemon,
)
from src.pokemon_battle_engine.domain.constants import FIRE_TYPE


# --- tick(): immunity by type -------------------------------------------------
# Each effect is neutralised by one type. We assert no message lies AND no HP
# is lost, which folds the old separate "inmune"/"immune" duplicates into one.
@pytest.mark.parametrize("effect_cls, poke_fixture", [
    (BurnEffect, "charmander"),       # Fire
    (ParalyzeEffect, "pikachu"),      # Electric
    (PoisonEffect, "bulbasaur"),      # Poison
    (BadlyPoisonedEffect, "bulbasaur"),
    (FreezeEffect, "vanilux"),        # Ice
])
def test_effect_is_blocked_by_type_immunity(effect_cls, poke_fixture, request):
    pokemon = request.getfixturevalue(poke_fixture)
    old_hp = pokemon.hp

    message = effect_cls().tick(pokemon)

    assert "Immune" in message
    assert pokemon.hp == old_hp


# --- tick(): damaging effects on a non-immune target --------------------------
@pytest.mark.parametrize("effect_cls, keyword", [
    (BurnEffect, "damage"),
    (PoisonEffect, "poison"),
    (BadlyPoisonedEffect, "badly"),
])
def test_damaging_effect_hurts_target(effect_cls, keyword, squirtle):
    old_hp = squirtle.hp

    message = effect_cls().tick(squirtle)

    assert squirtle.hp < old_hp
    assert keyword in message


# --- tick(): non-damaging effects just announce the condition -----------------
@pytest.mark.parametrize("effect_cls, keyword", [
    (ParalyzeEffect, "paralyzed"),
    (SleepEffect, "asleep"),
    (FreezeEffect, "frozen"),
])
def test_status_effect_announces_condition(effect_cls, keyword, squirtle):
    message = effect_cls().tick(squirtle)
    assert keyword in message


# --- set_status() transitions -------------------------------------------------
def test_poison_can_be_upgraded_to_toxic(pikachu):
    assert pikachu.set_status(PoisonEffect()) is True
    assert isinstance(pikachu.current_status_effect, PoisonEffect)

    assert pikachu.set_status(BadlyPoisonedEffect()) is True
    assert isinstance(pikachu.current_status_effect, BadlyPoisonedEffect)


def test_set_status_fails_when_already_statused(squirtle):
    # First status sticks; a second, non-toxic upgrade is rejected (models.py:63).
    assert squirtle.set_status(SleepEffect()) is True
    assert squirtle.set_status(BurnEffect()) is False
    assert isinstance(squirtle.current_status_effect, SleepEffect)


# --- Burn halves physical attack ----------------------------------------------
def test_burn_halves_physical_damage(charmander, squirtle):
    calculator = PhysicalDamageCalculator()

    burned = Pokemon(
        name="Burned Charmander", level=5, hp=39, max_hp=39,
        attack=52, defense=43, sp_attack=60, sp_defense=50, speed=65,
        primary_type=FIRE_TYPE, secondary_type=None,
    )
    burned.current_status_effect = BurnEffect()

    normal_damage = calculator.calculate(charmander, squirtle, 40, 1.0, 1.0, False)
    burned_damage = calculator.calculate(burned, squirtle, 40, 1.0, 1.0, False)

    assert burned_damage < normal_damage


# --- prevents_movement() / get_fail_message() ---------------------------------
# Burn / Poison / BadlyPoisoned do not override the base methods, so this
# exercises StatusEffect.prevents_movement and .get_fail_message (models.py:192,195).
@pytest.mark.parametrize("effect_cls", [BurnEffect, PoisonEffect, BadlyPoisonedEffect])
def test_damaging_effects_never_block_movement(effect_cls, squirtle):
    effect = effect_cls()
    assert effect.prevents_movement(squirtle) is False
    assert "couldn't move" in effect.get_fail_message(squirtle)


def test_paralyze_electric_type_always_moves(pikachu):
    # Electric types ignore paralysis (models.py:213-214).
    assert ParalyzeEffect().prevents_movement(pikachu) is False


@pytest.mark.parametrize("roll, blocked", [(10, True), (50, False)])
def test_paralyze_random_block(squirtle, roll, blocked):
    # 25% chance to be fully paralysed (models.py:216).
    with patch("random.randint", return_value=roll):
        assert ParalyzeEffect().prevents_movement(squirtle) is blocked


def test_paralyze_fail_message(squirtle):
    assert "didn't move" in ParalyzeEffect().get_fail_message(squirtle)


@pytest.mark.parametrize("roll, blocked", [(50, True), (10, False)])
def test_sleep_random_block(squirtle, roll, blocked):
    # 33% chance to wake up and act (models.py:226-229).
    with patch("random.randint", return_value=roll):
        assert SleepEffect().prevents_movement(squirtle) is blocked


def test_sleep_fail_message(squirtle):
    assert "woke up" in SleepEffect().get_fail_message(squirtle)


@pytest.mark.parametrize("roll, blocked", [(50, True), (10, False)])
def test_freeze_random_block(squirtle, roll, blocked):
    # 20% chance to thaw and act (models.py:262-265).
    with patch("random.randint", return_value=roll):
        assert FreezeEffect().prevents_movement(squirtle) is blocked


def test_freeze_fail_message(squirtle):
    assert "defrost" in FreezeEffect().get_fail_message(squirtle)
