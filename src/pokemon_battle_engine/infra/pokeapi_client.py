# src/pokemon_battle_engine/infra/pokeapi_client.py

import httpx


class PokeAPIClient:
    async def get_pokemon(self, name: str):

        # Connection to the API
        pokemon_url = f"https://pokeapi.co/api/v2/pokemon/{name}/"

        # Making the get petition using await because it takes time
        async with httpx.AsyncClient() as client: 
            response = await client.get(pokemon_url)

            # Succesfull connection equals 200
            response.raise_for_status()

            data = response.json()
            return data

