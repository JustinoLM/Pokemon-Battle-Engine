# src/pokemon_battle/domain/repository.py

from typing import TypeVar, Generic, Dict, Optional
from .models import Pokemon

T = TypeVar('T')

class Repository(Generic[T]):
	def __init__(self) -> None:
		self._storage: Dict[int, T] = {}

	def add(self, id:int, item:T) -> None:
		self._storage[id]= item

	def get(self, id:int) -> Optional[T]:
		return self._storage.get(id)

	def list(self) -> list[T]:
		return list(self._storage.values())


class PokemonRepository(Repository[Pokemon]):
	pass

