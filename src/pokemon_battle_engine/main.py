# src/pokemon_battle/main.py

import random # <--- NECESARIO para la selección aleatoria

from pokemon_battle_engine.domain.models import (
    Pokemon, Move, 
    PhysicalDamageCalculator, SpecialDamageCalculator, 
    ModifyStage, ParalyzeEffect, StatusDamageCalculator
)
from pokemon_battle_engine.domain.constants import (
    ELECTRIC_TYPE, NORMAL_TYPE, FIRE_TYPE, ROCK_TYPE, FLYING_TYPE
)
from pokemon_battle_engine.domain.battle import Team, Trainer, Battle

def print_turn_result(result, move):
    """Helper para imprimir el estado de la batalla de forma legible"""
    print(f"  > {result.attacker_name} used {move.name}!") # <--- Mostramos qué movimiento salió
    print(f"  > Damage dealt: {result.damage}")
    
    # Imprimir mensajes internos (Críticos, Cambios de Estado)
    for msg in result.messages:
        print(f"  [!] {msg}")
        
    print(f"  > {result.defender_name} HP: {result.defender_hp}") # Mostramos HP actual

def main():
    print("=== RANDOM POKEMON BATTLE ENGINE v1.0 ===\n")

    # --- 1. Setup Pokemon ---
    zapdos = Pokemon(
        name="Zapdos", level=50, hp=200, max_hp=200,
        attack=90, defense=80, sp_attack=160, sp_defense=90, speed=120,
        primary_type=FLYING_TYPE, secondary_type= ELECTRIC_TYPE
    )

    charizard = Pokemon(
        name="Heat Rottom", level=50, hp=250, max_hp=250,
        attack=130, defense=100, sp_attack=150, sp_defense=100, speed=100,
        primary_type=FIRE_TYPE, secondary_type=ELECTRIC_TYPE
    )

    # --- 2. Setup Moves ---
    
    # Basic attack
    tackle = Move(
        name="Tackle", power=40, move_type=NORMAL_TYPE, 
        damage_calculator=PhysicalDamageCalculator()
    )

    # Attack with secondary effect
    thunderbolt = Move(
        name="Thunderbolt", power=90, move_type=ELECTRIC_TYPE, 
        damage_calculator=SpecialDamageCalculator(),
        secondary_effect=ParalyzeEffect(), 
        secondary_effect_chance=10
    )

    # Status move
    nasty_plot = Move(
        name="Nasty Plot", power=0, move_type=NORMAL_TYPE, 
        damage_calculator=StatusDamageCalculator(),
        stage_changes=[ModifyStage(["sp_attack"], 2, target="self")]
    )
    
    # Low precision high damage
    stone_edge = Move(
        name="Guillotine", power=1000, move_type=ROCK_TYPE, 
        damage_calculator=PhysicalDamageCalculator(),
        accuracy=30
    )

    # Lista de movimientos disponibles para ambos
    available_moves = [tackle, thunderbolt, nasty_plot, stone_edge]

    # --- 3. Setup de Batalla ---
    ash_team = Team(members=[zapdos], active_pokemon_index=0)
    rival_team = Team(members=[charizard], active_pokemon_index=0)

    ash = Trainer(name="Ash", team=ash_team)
    rival = Trainer(name="Rival", team=rival_team)

    battle = Battle(trainer1=ash, trainer2=rival)

    # --- 4. Loop de Combate ---
    print(f"¡{ash.name} vs {rival.name}!\n")

    turn_count = 0
    while True:
        turn_count += 1
        print(f"--- TURN {turn_count} ---")
        
        # Limpiamos mensajes al INICIO del turno para asegurar limpieza
        battle.messages.clear() 
        
        first_trainer = battle.pokemon_order(ash, rival)
        second_trainer = rival if first_trainer == ash else ash

        move1 = random.choice(available_moves)
        move2 = random.choice(available_moves)

        # 3. Turno del Atacante Rápido
        result1 = battle.execute_turn(attacker=first_trainer, defender=second_trainer, move=move1)
        print_turn_result(result1, move1)
        
        # LIMPIEZA 1: Borramos los mensajes de este ataque para que no se arrastren
        battle.messages.clear() 
        
        if result1.is_ko:
            print(f"\n{second_trainer.name}'s Pokemon fainted! {first_trainer.name} wins!")
            break

        # 4. Turno del Atacante Lento
        result2 = battle.execute_turn(attacker=second_trainer, defender=first_trainer, move=move2)
        print_turn_result(result2, move2)
        
        # LIMPIEZA 2: Borramos los mensajes del segundo ataque
        battle.messages.clear()

        if result2.is_ko:
            print(f"\n{first_trainer.name}'s Pokemon fainted! {second_trainer.name} wins!")
            break

        # 5. Fin de Turno (Daño residual)
        print("\n  [End of Turn Effects]")
        battle.process_end_of_turn() # Ahora SOLO agregará mensajes de quemadura/veneno
        for msg in battle.messages:
            print(f"  [!] {msg}")
        
        battle.messages.clear() # Limpiamos para el siguiente turno global
        print("\n" + "-"*30 + "\n")

if __name__ == "__main__":
    main()