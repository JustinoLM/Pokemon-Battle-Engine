# tests/unit/test_repository.py

from src.pokemon_battle_engine.domain.repository import PokemonRepository

def test_repository_can_save_and_retrieve(charmander):
    repo = PokemonRepository()
    
    repo.add(1, charmander)
    retrieved_pokemon = repo.get(1)
    
    # 3. Verificar (Dataclasses tiene __eq__ automático, esto compara campos uno a uno)
    assert retrieved_pokemon == charmander

def test_repository_returns_none_if_not_found():
    repo = PokemonRepository()
    pokemon = repo.get(999)
    assert pokemon is None

def test_repository_can_list_all_pokemons(charmander, squirtle):
    repo = PokemonRepository()
    repo.add(1, charmander)
    repo.add(2, squirtle)
    
    all_pokemons = repo.list()
    
    assert len(all_pokemons) == 2
    assert charmander in all_pokemons
    assert squirtle in all_pokemons