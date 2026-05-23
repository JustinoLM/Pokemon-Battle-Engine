# src/pokemon_battle/domain/constants.py

from dataclasses import dataclass

# --- Types definititions ---
@dataclass(frozen=True)
class Type:
	name: str

NORMAL_TYPE = Type("Normal")
FIRE_TYPE = Type("Fire")
WATER_TYPE = Type("Water")
ELECTRIC_TYPE = Type("Electric")
GRASS_TYPE = Type("Grass")
ICE_TYPE = Type("Ice")
FIGHTING_TYPE = Type("Fighting")
POISON_TYPE = Type("Poison")
GROUND_TYPE = Type("Ground")
FLYING_TYPE = Type("Flying")
PSYCHIC_TYPE = Type("Psychic")
BUG_TYPE = Type("Bug")
ROCK_TYPE = Type("Rock")
GHOST_TYPE = Type("Ghost")
DRAGON_TYPE = Type("Dragon")
DARK_TYPE = Type("Dark")
STEEL_TYPE = Type("Steel")
FAIRY_TYPE = Type("Fairy")

TYPE_CHART = {
    "Normal": {
        "Rock": 0.5,
        "Ghost": 0.0,
        "Steel": 0.5,
    },

    "Fire": {
        "Fire": 0.5,
        "Water": 0.5,
        "Grass": 2.0,
        "Ice": 2.0,
        "Bug": 2.0,
        "Rock": 0.5,
        "Dragon": 0.5,
        "Steel": 2.0,
    },

    "Water": {
        "Fire": 2.0,
        "Water": 0.5,
        "Grass": 0.5,
        "Ground": 2.0,
        "Rock": 2.0,
        "Dragon": 0.5,
    },

    "Electric": {
        "Water": 2.0,
        "Electric": 0.5,
        "Grass": 0.5,
        "Ground": 0.0,
        "Flying": 2.0,
        "Dragon": 0.5,
    },

    "Grass": {
        "Fire": 0.5,
        "Water": 2.0,
        "Grass": 0.5,
        "Poison": 0.5,
        "Ground": 2.0,
        "Flying": 0.5,
        "Bug": 0.5,
        "Rock": 2.0,
        "Dragon": 0.5,
        "Steel": 0.5,
    },

    "Ice": {
        "Fire": 0.5,
        "Water": 0.5,
        "Grass": 2.0,
        "Ice": 0.5,
        "Ground": 2.0,
        "Flying": 2.0,
        "Dragon": 2.0,
        "Steel": 0.5,
    },

    "Fighting": {
        "Normal": 2.0,
        "Ice": 2.0,
        "Poison": 0.5,
        "Flying": 0.5,
        "Psychic": 0.5,
        "Bug": 0.5,
        "Rock": 2.0,
        "Ghost": 0.0,
        "Dark": 2.0,
        "Steel": 2.0,
        "Fairy": 0.5,
    },

    "Poison": {
        "Grass": 2.0,
        "Poison": 0.5,
        "Ground": 0.5,
        "Rock": 0.5,
        "Ghost": 0.5,
        "Steel": 0.0,
        "Fairy": 2.0,
    },

    "Ground": {
        "Fire": 2.0,
        "Electric": 2.0,
        "Grass": 0.5,
        "Poison": 2.0,
        "Flying": 0.0,
        "Bug": 0.5,
        "Rock": 2.0,
        "Steel": 2.0,
    },

    "Flying": {
        "Electric": 0.5,
        "Grass": 2.0,
        "Fighting": 2.0,
        "Bug": 2.0,
        "Rock": 0.5,
        "Steel": 0.5,
    },

    "Psychic": {
        "Fighting": 2.0,
        "Poison": 2.0,
        "Psychic": 0.5,
        "Dark": 0.0,
        "Steel": 0.5,
    },

    "Bug": {
        "Fire": 0.5,
        "Grass": 2.0,
        "Fighting": 0.5,
        "Poison": 0.5,
        "Flying": 0.5,
        "Psychic": 2.0,
        "Ghost": 0.5,
        "Dark": 2.0,
        "Steel": 0.5,
        "Fairy": 0.5,
    },

    "Rock": {
        "Fire": 2.0,
        "Ice": 2.0,
        "Fighting": 0.5,
        "Ground": 0.5,
        "Flying": 2.0,
        "Bug": 2.0,
        "Steel": 0.5,
    },

    "Ghost": {
        "Normal": 0.0,
        "Psychic": 2.0,
        "Ghost": 2.0,
        "Dark": 0.5,
    },

    "Dragon": {
        "Dragon": 2.0,
        "Steel": 0.5,
        "Fairy": 0.0,
    },

    "Dark": {
        "Fighting": 0.5,
        "Psychic": 2.0,
        "Ghost": 2.0,
        "Dark": 0.5,
        "Fairy": 0.5,
    },

    "Steel": {
        "Fire": 0.5,
        "Water": 0.5,
        "Electric": 0.5,
        "Ice": 2.0,
        "Rock": 2.0,
        "Steel": 0.5,
        "Fairy": 2.0,
    },

    "Fairy": {
        "Fire": 0.5,
        "Fighting": 2.0,
        "Poison": 0.5,
        "Dragon": 2.0,
        "Dark": 2.0,
        "Steel": 0.5,
    }
}

STAGE_MULTIPLIERS = {
    -6: 2/8,  -5: 2/7,  -4: 2/6,  -3: 2/5,  -2: 2/4,  -1: 2/3,
    0: 1.0,
    1: 3/2,   2: 2/1,   3: 5/2,   4: 3/1,   5: 7/2,   6: 4/1
}

CRIT_CHANCE = {
    0: 4.17,
    1: 12.5,
    2: 50.0,
    3: 100.0,
    4: 100.0
}