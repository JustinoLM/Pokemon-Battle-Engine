# src/pokemon_battle_engine/domain/items_registry.py

from .models import Item
from .constants import (
	FAIRY_TYPE, FIRE_TYPE, FIGHTING_TYPE, FLYING_TYPE,
	BUG_TYPE, DARK_TYPE, DRAGON_TYPE, ELECTRIC_TYPE,
	GHOST_TYPE, GRASS_TYPE,GROUND_TYPE, ICE_TYPE,
	NORMAL_TYPE, POISON_TYPE, PSYCHIC_TYPE, ROCK_TYPE,
	STEEL_TYPE, WATER_TYPE)

# --- Consumables ---
FOCUS_SASH = Item(
    name="Focus Sash",
    is_consumable=True,
    # check in the damage zone of the equation
    # Logic will be: if at full= hp and hit -> survive with 1 hp
)

SITRUS_BERRY = Item(
    name="Sitrus Berry",
    is_consumable=True,
    is_passive_heal=True,
    heal_threshold_percent=0.5, # Heals at 50% HP
    passive_heal_percent=0.25   # Heals 1/4 Max HP
)

LUM_BERRY = Item(
    name="Lum Berry",
    is_consumable=True,
    # Logic: Cures status
)

MENTAL_HERB = Item(
    name="Mental Herb",
    is_consumable=True,
    # Logic: Cures Taunt/Encore/Infatuation
)

WEAKNESS_POLICY = Item(
    name="Weakness Policy",
    is_stat_modifier=True,
    is_consumable=True,
    stats_to_modify=["attack", "sp_attack"],
    stage_boost_amount=2
)

THROAT_SPRAY = Item(
    name="Throat Spray",
    is_stat_modifier=True,
    is_consumable=True,
    stats_to_modify=["sp_attack"],
    stage_boost_amount=1,
    requires_sound_move=True
)

# --- Stat Boosters ---
CHOICE_BAND = Item(
    name="Choice Band",
    is_stat_modifier=True,
    stats_to_modify=["attack"],
    stat_multiplier=1.5
)

CHOICE_SPECS = Item(
    name="Choice Specs",
    is_stat_modifier=True,
    stats_to_modify=["sp_attack"],
    stat_multiplier=1.5
)

CHOICE_SCARF = Item(
    name="Choice Scarf",
    is_stat_modifier=True,
    stats_to_modify=["speed"],
    stat_multiplier=1.5
)

ASSAULT_VEST = Item(
    name="Assault Vest",
    is_stat_modifier=True,
    stats_to_modify=["sp_defense"],
    stat_multiplier=1.5
)

RAZOR_CLAW = Item(
    name="Razor Claw",
    is_stat_modifier=True,
    stats_to_modify=["crit_stage"],
    stage_boost_amount=1
)

# --- Complex Items ---
LIFE_ORB = Item(
    name="Life Orb",
    is_stat_modifier=True,      # Boosts damage slightly usually, but we can model as multiplier
    stats_to_modify=["attack"],     # Simplification: Apply to both for now
    stat_multiplier=1.3,         # 1.32x usually
    is_recoil_damage=True,
    recoil_percent=0.1
)

LEFTOVERS = Item(
    name="Leftovers",
    is_passive_heal=True,
    passive_heal_percent=0.0625 
)

EVIOLITE = Item(
    name="Eviolite",
    stats_to_modify=["sp_defense", "defense"],
    stat_multiplier=1.5,
)

ROCKY_HELMET = Item(
    name= "Rocky Helmet",
    is_recoil_damage=True,
    recoil_percent= 0.1667,
    makes_contact_recoil=True
)

BLACK_SLUDGE = Item(
    name="Black Sludge",
    is_passive_heal=True,
    is_self_status=True, # if pokemon is not poison type
    passive_heal_percent= 0.0625

)

FLAME_ORB = Item(
    name="Flame Orb",
    is_self_status=True
)

TOXIC_ORB = Item(
    name="Toxic Orb",
    is_self_status=True
)

COVERT_CLOAK = Item(
    name="Covert Cloak",
    is_protective=True
)

LOADED_DICE = Item(
    name="Loaded Dice",
    # check if held item is loaded dice in the multi hit check and modify there
)

KINGS_ROCK = Item(
    name="Kings Rock",
    requires_contact=True
    # when the move is physical check for flinch porcentange and add 10% to the base move
)

PROTECTIVE_PADS = Item(
    name="Protective Pads",
    # check for the item in rocky helmet and spiky shield logic
)

# --- Type-enhancing items ---

EXPERT_BELT = Item(
    name="Expert Belt",
    type_boost_multiplier=1.2
    # boost supereffective moves of the holder by 20%
    # check for item in effectiveness formula
)

BLACK_BELT = Item(
    name="Black Belt",
    type_boost_multiplier=1.2,
    associated_type=FIGHTING_TYPE
)

BLACK_GLASSES = Item(
    name="Black Glasses",
    type_boost_multiplier=1.2,
    associated_type=DARK_TYPE
)

CHARCOAL = Item(
    name="Charcoal",
    type_boost_multiplier=1.2,
    associated_type=FIRE_TYPE
)

DRAGON_FANG = Item(
    name="Dragon Fang",
    type_boost_multiplier=1.2,
    associated_type=DRAGON_TYPE
)

FAIRY_FEATHER = Item(
    name="Fairy Feather",
    type_boost_multiplier=1.2,
    associated_type=FAIRY_TYPE
)

HARD_STONE = Item(
    name="Hard Stone",
    type_boost_multiplier=1.2,
    associated_type=ROCK_TYPE
)

MAGNET = Item(
    name="Magnet",
    type_boost_multiplier=1.2,
    associated_type=ELECTRIC_TYPE
)

METAL_COAT = Item(
    name="Metal Coat",
    type_boost_multiplier=1.2,
    associated_type=STEEL_TYPE
)

MIRACLE_SEED = Item(
    name="Miracle Seed",
    type_boost_multiplier=1.2,
    associated_type=GRASS_TYPE
)

MYSTIC_WATER = Item(
    name="Mystic Water",
    type_boost_multiplier=1.2,
    associated_type=WATER_TYPE
)

NEVER_MET_ICE = Item(
    name="Never-Melt Ice",
    type_boost_multiplier=1.2,
    associated_type=ICE_TYPE
)

POISON_BARB = Item(
    name="Poison Barb",
    type_boost_multiplier=1.2,
    associated_type=POISON_TYPE
)

SHARP_BEAK = Item(
    name="Sharp Beak",
    type_boost_multiplier=1.2,
    associated_type=FLYING_TYPE
)

SILK_SCARF = Item(
    name="Silk Scarf",
    type_boost_multiplier=1.2,
    associated_type=NORMAL_TYPE
)

SILVER_POWDER = Item(
    name="Silver Powder",
    type_boost_multiplier=1.2,
    associated_type=BUG_TYPE
)

SOFT_SAND = Item(
    name="Soft Sand",
    type_boost_multiplier=1.2,
    associated_type=GROUND_TYPE
)

SPELL_TAG = Item(
    name="Spell Tag",
    type_boost_multiplier=1.2,
    associated_type=GHOST_TYPE
)

TWISTED_SPOON = Item(
    name="Twisted Spoon",
    type_boost_multiplier=1.2,
    associated_type=PSYCHIC_TYPE
)

