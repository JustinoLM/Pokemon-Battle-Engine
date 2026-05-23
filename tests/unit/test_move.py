#tests/unit/test_move.py

from src.pokemon_battle_engine.domain.models import (
    Type, Move, PhysicalDamageCalculator, 
    SpecialDamageCalculator, StatusDamageCalculator,
    SleepEffect
    )
from src.pokemon_battle_engine.domain.constants import (
    TYPE_CHART, STAGE_MULTIPLIERS,
	FAIRY_TYPE, FIRE_TYPE, FIGHTING_TYPE, FLYING_TYPE,
	BUG_TYPE, DARK_TYPE, DRAGON_TYPE, ELECTRIC_TYPE,
	GHOST_TYPE, GRASS_TYPE,GROUND_TYPE, ICE_TYPE,
	NORMAL_TYPE, POISON_TYPE, PSYCHIC_TYPE, ROCK_TYPE,
	STEEL_TYPE, WATER_TYPE
    )

from unittest.mock import MagicMock, ANY
import pytest

## Test normal
def test_tackle_does_damage(charmander,bulbasaur):
    tackle = Move("Tackle",40,Type("Normal"),PhysicalDamageCalculator())
    damage = tackle.execute(charmander,bulbasaur)
    assert damage > 0

def test_ember_does_damage(charmander,bulbasaur):
    ember = Move("Ember",40,Type("Fire"),SpecialDamageCalculator())
    damage = ember.execute(charmander,bulbasaur)
    assert damage > 0

def test_leer_do_0_damage(charmander,bulbasaur):
    leer = Move("Leer",0,Type("Normal"),StatusDamageCalculator())
    damage = leer.execute(charmander,bulbasaur)
    assert damage == 0

## Test con Magimock
def test_stab_passes_1_5_multiplier(charmander, bulbasaur):
    ember = Move("Ember",40,Type("Fire"),MagicMock())
    ember.execute(charmander,bulbasaur)
    assert ember.damage_calculator.calculate.call_args.kwargs["stab"] == 1.5
    

@pytest.mark.parametrize("effectivity", [2.0])
def test_effectivity_passed_to_calculator(charmander, bulbasaur, fire_type, effectivity):
    ember = Move("Ember",40,fire_type,MagicMock())
    ember.execute(charmander,bulbasaur)
    assert ember.damage_calculator.calculate.call_args.kwargs["effectivity"] == 2.0

def test_secondary_effect(battle):
    attacker = battle.trainer1.get_active_pokemon()
    defender = battle.trainer2.get_active_pokemon()

    dummy_move = Move(
        name="Tackle", 
        power=40, 
        move_type=NORMAL_TYPE, 
        damage_calculator=PhysicalDamageCalculator(),
        secondary_effect=SleepEffect(),
        secondary_effect_chance=100
    )

    result = battle.execute_turn(
        battle.trainer1,
        battle.trainer2,
        dummy_move  
    )
    assert isinstance(defender.current_status_effect, SleepEffect)