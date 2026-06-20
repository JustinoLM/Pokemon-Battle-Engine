# src/pokemon_battle_engine/main.py

import random

from pokemon_battle_engine.domain.models import (
    Move, 
    PhysicalDamageCalculator, SpecialDamageCalculator, 
    ModifyStage, ParalyzeEffect, StatusDamageCalculator
)
from pokemon_battle_engine.domain.constants import (
    ELECTRIC_TYPE, NORMAL_TYPE, ROCK_TYPE
)
from pokemon_battle_engine.domain.battle import Team, Trainer, Battle
from pokemon_battle_engine.services.battle_service import BattleService

import asyncio
from pokemon_battle_engine.infra.pokeapi_client import PokeAPIClient
from pokemon_battle_engine.infra.pokemon_mapper import map_pokemon_from_api


def print_turn_result(result, move):
    print(f"  > {result.attacker_name} used {move.name}!")
    print(f"  > Damage dealt: {result.damage}")
    
    for msg in result.messages:
        print(f"  [!] {msg}")
        
    print(f"  > {result.defender_name} HP: {result.defender_hp}") # Mostramos HP actual

async def main():
    print("=== RANDOM POKEMON BATTLE ENGINE v1.0 ===\n")

    # --- 1. Setup Pokemon ---
    client = PokeAPIClient()

    # -- Fetching data --
    zapdos_data = await client.get_pokemon("zapdos")
    charizard_data = await client.get_pokemon("charizard")

    # -- Map data to domain objects --
    zapdos = map_pokemon_from_api(zapdos_data)
    charizard = map_pokemon_from_api(charizard_data)

    zapdos.ivs = {"hp":31, "atk": 0, "def": 31, "spa": 31, "spd": 25, "spe":31}
    zapdos.__post_init__()

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

    zapdos.move_pool = available_moves
    charizard.move_pool = available_moves

    ash = Trainer(name="Ash", team=ash_team)
    rival = Trainer(name="Rival", team=rival_team)

    battle = Battle(trainer1=ash, trainer2=rival)
    battle_service = BattleService(battle)


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
        result1 = await battle_service.execute_turn(
            attacker_name =first_trainer.name,
            defender_name=second_trainer.name,
            move_name=move1.name
            )
        print_turn_result(result1, move1)
        
        # LIMPIEZA 1: Borramos los mensajes de este ataque para que no se arrastren
        battle.messages.clear() 
        
        if result1.is_ko:
            print(f"\n{second_trainer.name}'s Pokemon fainted! {first_trainer.name} wins!")
            break

        # 4. Turno del Atacante Lento
        result2 = await battle_service.execute_turn(
            attacker_name=second_trainer.name,
            defender_name=first_trainer.name,
            move_name=move2.name)
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

# Fast PokeAPIClient test
async def test_api():
    client = PokeAPIClient()
    data = await client.get_pokemon("pikachu")
    print(f"Nombre: {data['name']}")
    print(f"ID: {data['id']}")
    print(f"Movimientos disponibles: {len(data['moves'])}")

if __name__ == "__main__":
    #asyncio.run(test_api())
    asyncio.run(main())