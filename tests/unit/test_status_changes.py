#tests/unit/test_status_changes.py

from src.pokemon_battle_engine.domain.models import (Type, Move, ModifyStage)
from src.pokemon_battle_engine.domain.damage import (
    PhysicalDamageCalculator, StatusDamageCalculator,
)

from src.pokemon_battle_engine.domain.constants import (
    NORMAL_TYPE
    )

def test_move_with_stage_change(charmander):
    boost_strategy = ModifyStage(["attack"], 2, target="self")

    swords_dance = Move("Swords Dance", 0, Type("Normal"), StatusDamageCalculator(), 
                        stage_changes=[boost_strategy])
    
    damage = swords_dance.execute(charmander, charmander)

    assert charmander.attack_stage == 2
    assert damage == 0

def test_modify_stage_self_increases_stat(pikachu):    
    booster = ModifyStage(["attack"], 2, target="self")
    msg = booster.change_stage(pikachu)
    
    assert "attack" in msg
    assert "rose" in msg
    assert pikachu.attack_stage == 2

def test_shell_smash_stats_trade_off(charmander, squirtle):
    defense_drop = ModifyStage(["defense", "sp_defense"], -1, target="self")
    offense_boost = ModifyStage(["attack", "sp_attack", "speed"], 2, target="self")
    
    shell_smash = Move("Shell Smash", 120, Type("Normal"), PhysicalDamageCalculator(),
                         stage_changes=[defense_drop, offense_boost])
    
    damage = shell_smash.execute(charmander, squirtle)
    

    assert charmander.defense_stage == -1
    assert charmander.attack_stage == 2
    assert damage > 0

def test_message_verbs_options(charmander, squirtle):
    defense_drop = ModifyStage(["defense", "sp_defense"], -1, target="self")
    offense_boost = ModifyStage(["attack", "sp_attack", "speed"], 2, target="self")
    
    shell_smash = Move("Shell Smash", 120, NORMAL_TYPE, PhysicalDamageCalculator(),
                         stage_changes=[defense_drop, offense_boost])
    
    shell_smash.execute(charmander, squirtle)

    assert any("rose" in msg for msg in shell_smash.messages)
    assert any("fell" in msg for msg in shell_smash.messages)

    assert charmander.attack_stage == 2
    assert charmander.defense_stage == -1
    assert charmander.sp_defense_stage == -1

def test_stat_cap_message_no_verb(ultra_boosted_charmander, squirtle):
    swords_dance = Move(
        "Swords Dance", 
        0, 
        NORMAL_TYPE, 
        PhysicalDamageCalculator(),
        stage_changes=[ModifyStage(["attack"], 2, target="self")]
    )
    
    swords_dance.execute(ultra_boosted_charmander, squirtle)
    assert not any("rose" in msg for msg in swords_dance.messages)
    assert any("won't go higher" in msg for msg in swords_dance.messages)
    assert ultra_boosted_charmander.attack_stage == 6

def test_limit_stage_changes(ultra_boosted_charmander, squirtle):
    defense_drop = ModifyStage(["defense", "sp_defense"], -1, target="self")
    offense_boost = ModifyStage(["attack", "sp_attack", "speed"], 2, target="self")
    
    shell_smash = Move("Shell Smash", 120, NORMAL_TYPE, PhysicalDamageCalculator(),
                         stage_changes=[defense_drop, offense_boost])
    
    shell_smash.execute(ultra_boosted_charmander, squirtle)

    assert any("higher" in msg for msg in shell_smash.messages)
    assert any("fell" in msg for msg in shell_smash.messages)

    assert ultra_boosted_charmander.attack_stage == 6
    assert ultra_boosted_charmander.defense_stage == -6
    assert ultra_boosted_charmander.sp_defense_stage == -6


def test_stat_floor_message(charmander):
    # Ponemos defensa al mínimo
    charmander.defense_stage = -6
    
    drop = ModifyStage(["defense"], -1, target="self")
    move = Move("Screech", 0, NORMAL_TYPE, PhysicalDamageCalculator(), stage_changes=[drop])
    
    move.execute(charmander, charmander)
    
    # Debe decir "won't go lower" y NO "fell"
    assert any("lower" in msg for msg in move.messages) 
    # (Nota: "lower" está en "won't go lower", así que esto pasa, pero para ser precisos:
    assert any("won't go lower" in msg for msg in move.messages)
    assert charmander.defense_stage == -6