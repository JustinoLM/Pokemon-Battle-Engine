#tests/conftest.py

import pytest
from src.pokemon_battle_engine.domain.models import Pokemon, Type
from src.pokemon_battle_engine.domain.battle import Team, Trainer, Battle
from src.pokemon_battle_engine.domain.repository import PokemonRepository


# Fixtures de Tipos
@pytest.fixture
def fire_type():
    return Type("Fire")

@pytest.fixture
def water_type():
    return Type("Water")

@pytest.fixture
def grass_type():
    return Type("Grass")

@pytest.fixture
def poison_type():
    return Type("Poison")

@pytest.fixture
def electric_type():
    return Type("Electric")

@pytest.fixture
def ice_type():
    return Type("Ice")


# Fixture: Bulbasaur
@pytest.fixture
def bulbasaur(grass_type, poison_type):
    return Pokemon(
        name="Bulbasaur", level=5, hp=45, max_hp=45,
        attack=49, defense=49, sp_attack=65, sp_defense=65, speed=45,
        primary_type=grass_type, secondary_type=poison_type
    )

# Fixture: Squirtle
@pytest.fixture
def squirtle(water_type):
    return Pokemon(
        name="Squirtle", level=5, hp=44, max_hp=44,
        attack=48, defense=65, sp_attack=50, sp_defense=64, speed=43,
        primary_type=water_type, secondary_type=None
    )

# Fixture: Charmander
@pytest.fixture
def charmander(fire_type):
    return Pokemon(
        name="Charmander", level=5, hp=39, max_hp=39,
        attack=52, defense=43, sp_attack=60, sp_defense=50, speed=65,
        primary_type=fire_type, secondary_type=None
    )

# Fixture: pikachu
@pytest.fixture
def pikachu(electric_type):
    return Pokemon(
        name="Pikachu", level=5, hp=39, max_hp=39,
        attack=52, defense=43, sp_attack=60, sp_defense=50, speed=65,
        primary_type=electric_type, secondary_type=None
    )

# Fixture: vanilux
@pytest.fixture
def vanilux(ice_type):
    return Pokemon(
        name="Vanilux", level=5, hp=39, max_hp=39,
        attack=52, defense=43, sp_attack=60, sp_defense=50, speed=65,
        primary_type=ice_type, secondary_type=None
    )

# Fixture: sniper vanilux
@pytest.fixture
def sniper_vanilux(ice_type):
    return Pokemon(
        name="Sniper Vanilux", level=5, hp=39, max_hp=39,
        attack=52, defense=43, sp_attack=60, sp_defense=50, speed=65,
        primary_type=ice_type, secondary_type=None,
        current_move=None,attack_stage=0,defense_stage=0,
        sp_attack_stage=0,sp_defense_stage=0, speed_stage=0,
        ability="Sniper"
    )

# Fixture: ultra boosted charmander
@pytest.fixture
def ultra_boosted_charmander(ice_type):
    return Pokemon(
        name="Ultra Boosted Charmander", level=5, hp=39, max_hp=39,
        attack=52, defense=43, sp_attack=60, sp_defense=50, speed=65,
        primary_type=ice_type, secondary_type=None,
        current_move=None,attack_stage=6,defense_stage=-5,
        sp_attack_stage=6,sp_defense_stage=-5, speed_stage=6,
        ability="Sniper"
    )


# Fixture: dead_pikachu
@pytest.fixture
def dead_pikachu(electric_type):
    return Pokemon(
        name="Pikachu", level=5, hp=0, max_hp=39,
        attack=52, defense=43, sp_attack=60, sp_defense=50, speed=65,
        primary_type=electric_type, secondary_type=None
    )

# Fixture: dead_team
@pytest.fixture
def dead_team(charmander, dead_pikachu):
    return Team(
        members=[charmander, dead_pikachu], active_pokemon_index=0
    )

# Fixture: Ash_team
@pytest.fixture
def ash_team(charmander):
    return Team(
        members=[charmander], active_pokemon_index=0
    )

# Fixture: Misty_team
@pytest.fixture
def misty_team(bulbasaur):
    return Team(
        members=[bulbasaur], active_pokemon_index=0
    )

# Fixture: Ash
@pytest.fixture
def ash(ash_team):
    return Trainer(
        name="Ash", 
        team=ash_team
    )

# Fixture: Misty
@pytest.fixture
def misty(misty_team):
    return Trainer(
        name="Misty", 
        team=misty_team
    )

# Fixture: Battle
@pytest.fixture
def battle(ash,misty):
    return Battle(
        trainer1=ash, 
        trainer2=misty
    )

# Fixture: Repository
@pytest.fixture
def poke_repository():
    return PokemonRepository()
