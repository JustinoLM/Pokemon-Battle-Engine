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


# Fixture: Bulbasaur (base stats from Bulbasaur lvl 5)
@pytest.fixture
def bulbasaur(grass_type, poison_type):
    return Pokemon(
        name="Bulbasaur", level=5,
        base_hp=45, base_attack=49, base_defense=49,
        base_sp_attack=65, base_sp_defense=65, base_speed=45,
        primary_type=grass_type, secondary_type=poison_type
    )

# Fixture: Squirtle
@pytest.fixture
def squirtle(water_type):
    return Pokemon(
        name="Squirtle", level=5,
        base_hp=44, base_attack=48, base_defense=65,
        base_sp_attack=50, base_sp_defense=64, base_speed=43,
        primary_type=water_type, secondary_type=None
    )

# Fixture: Charmander
@pytest.fixture
def charmander(fire_type):
    return Pokemon(
        name="Charmander", level=5,
        base_hp=39, base_attack=52, base_defense=43,
        base_sp_attack=60, base_sp_defense=50, base_speed=65,
        primary_type=fire_type, secondary_type=None
    )

# Fixture: pikachu
@pytest.fixture
def pikachu(electric_type):
    return Pokemon(
        name="Pikachu", level=5,
        base_hp=35, base_attack=55, base_defense=40,
        base_sp_attack=50, base_sp_defense=50, base_speed=90,
        primary_type=electric_type, secondary_type=None
    )

# Fixture: vanilux
@pytest.fixture
def vanilux(ice_type):
    return Pokemon(
        name="Vanilux", level=5,
        base_hp=71, base_attack=95, base_defense=85,
        base_sp_attack=110, base_sp_defense=95, base_speed=79,
        primary_type=ice_type, secondary_type=None
    )

# Fixture: sniper vanilux
@pytest.fixture
def sniper_vanilux(ice_type):
    return Pokemon(
        name="Sniper Vanilux", level=5,
        base_hp=71, base_attack=95, base_defense=85,
        base_sp_attack=110, base_sp_defense=95, base_speed=79,
        primary_type=ice_type, secondary_type=None,
        current_move=None, attack_stage=0, defense_stage=0,
        sp_attack_stage=0, sp_defense_stage=0, speed_stage=0,
    )

# Fixture: ultra boosted charmander
@pytest.fixture
def ultra_boosted_charmander(ice_type):
    return Pokemon(
        name="Ultra Boosted Charmander", level=5,
        base_hp=39, base_attack=52, base_defense=43,
        base_sp_attack=60, base_sp_defense=50, base_speed=65,
        primary_type=ice_type, secondary_type=None,
        current_move=None, attack_stage=6, defense_stage=-5,
        sp_attack_stage=6, sp_defense_stage=-5, speed_stage=6,
    )


# Fixture: dead_pikachu
@pytest.fixture
def dead_pikachu(electric_type):
    p = Pokemon(
        name="Pikachu", level=5,
        base_hp=35, base_attack=55, base_defense=40,
        base_sp_attack=50, base_sp_defense=50, base_speed=90,
        primary_type=electric_type, secondary_type=None
    )
    p.hp = 0
    return p

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
def battle(ash, misty):
    return Battle(
        trainer1=ash,
        trainer2=misty
    )

# Fixture: Repository
@pytest.fixture
def poke_repository():
    return PokemonRepository()
