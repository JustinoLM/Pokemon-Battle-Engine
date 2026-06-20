# src/pokemon_battle_engine/api/main.py

from contextlib import asynccontextmanager

import uuid
from typing import Dict
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse

# Importing Functionality
from pokemon_battle_engine.domain.models import Pokemon, Move
from pokemon_battle_engine.domain.battle import Battle, Trainer, Team
from pokemon_battle_engine.domain.errors import BattleError, TrainerNotFoundError, IllegalMoveError, PokemonFaintedError
from pokemon_battle_engine.infra.pokeapi_client import PokeAPIClient
from pokemon_battle_engine.infra.pokemon_mapper import map_pokemon_from_api


# Importing Schemas
from .schemas import (
    BattleCreateRequest, 
    TurnSubmitRequest, 
    BattleStateResponse, 
    PokemonState
)

from pokemon_battle_engine.infra.logging import setup_logging, get_logger

from pokemon_battle_engine.domain.moves_registry import get_move_by_name

# ----- Initialize APP -----
app = FastAPI(title="Pokemong Battle Engine API")

# ---- Temporal Memory ----
active_battles: Dict[str, Battle] = {}

# --- Middleware for  LOGS ---
@app.middleware("http")
async def log_requests(request, call_next):
    import uuid
    request_id = str(uuid.uuid4())

    logger = get_logger()
    
    logger.info(
        "request_started",
        path=request.url.path,
        method=request.method,
        request_id=request_id
    )

    # -- Duration calculation --
    import time
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = (time.time() - start_time) * 1000
    response.headers["X-Request-ID"] = request_id # Devolver ID al cliente
    
    # -- Log output --
    logger.info(
        "request_completed",
        path=request.url.path,
        status_code=response.status_code,
        duration_ms=process_time,
        request_id=request_id
    )
    
    return response

# --- App Lifespan ---

@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    logger = get_logger()
    logger.info("Pokemon Battle API Started")
    yield

    logger.info("Pokemon Battle API Shutting down")

app = FastAPI(
    title="Pokemon Battle Engine API",
    lifespan=lifespan
)

# ----  HTTP Exceptions ----
@app.exception_handler(BattleError)
async def battle_error_handler(request, exc: BattleError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"message": exc.message},
    )

@app.exception_handler(TrainerNotFoundError)
async def trainer_not_found_handler(request, exc: TrainerNotFoundError):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"message": exc.message},
    )

@app.exception_handler(IllegalMoveError)
async def illegal_move_handler(request, exc: IllegalMoveError):
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"message": exc.message},
    )

@app.exception_handler(PokemonFaintedError)
async def pokemon_fainted_handler(request, exc: PokemonFaintedError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"message": exc.message},
    )

# --- Create the Trainers Teams ---
async def create_pokemon_team(name_list: list[str]) -> list[Pokemon]:
    client = PokeAPIClient()
    team = []
    for name in name_list:
        try:
            data = await client.get_pokemon(name)
            pkmn = map_pokemon_from_api(data)
            # Basics moves for now
            pkmn.move_pool = [get_move_by_name("tackle"), get_move_by_name("tackle")] 
            team.append(pkmn)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Could not fetch pokemon {name}: {str(e)}")
    return team

# --- ENDPOINTS ---

# -- Battle --
@app.post("/battles", response_model=BattleStateResponse, status_code=status.HTTP_201_CREATED)
async def create_battle(request: BattleCreateRequest):
    """
    New battle creation        
    """
    battle_id = str(uuid.uuid4())
    
    try:
        # 1. Obtain pokemon data (Async)
        team1_pokemon = await create_pokemon_team(request.trainer1.team)
        team2_pokemon = await create_pokemon_team(request.trainer2.team)
        
        # 2. Create domain objects
        t1_team_obj = Team(members=team1_pokemon, active_pokemon_index=0)
        t1_trainer = Trainer(name=request.trainer1.name, team=t1_team_obj)
        
        t2_team_obj = Team(members=team2_pokemon, active_pokemon_index=0)
        t2_trainer = Trainer(name=request.trainer2.name, team=t2_team_obj)
        
        # 3. Create battle
        battle = Battle(trainer1=t1_trainer, trainer2=t2_trainer)
        
        # 4. Save Battle 
        active_battles[battle_id] = battle
        
        # 5. Retornar estado inicial
        return map_battle_to_response(battle_id, battle)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# -- Turns --
@app.post("/battles/{battle_id}/turn", response_model=BattleStateResponse)
async def execute_turn(battle_id: str, turn_data: TurnSubmitRequest):
    """
    Execute a turn in a battle
    """
    if battle_id not in active_battles:
        raise HTTPException(status_code=404, detail="Battle not found")
    
    battle = active_battles[battle_id]
    
    # Identify Trainers
    attacker = None
    defender = None
    
    if battle.trainer1.name == turn_data.attacker_name:
        attacker = battle.trainer1
        defender = battle.trainer2
    elif battle.trainer2.name == turn_data.attacker_name:
        attacker = battle.trainer2
        defender = battle.trainer1
    else:
        raise HTTPException(status_code=400, detail="Attacker name not found in battle")

    move = get_move_by_name(turn_data.move_name)
    
    await battle.execute_turn(attacker, defender, move)
    
    battle.process_end_of_turn()
    battle.turn_count += 1
    
    return map_battle_to_response(battle_id, battle)

# -- Battle State --

@app.get("/battles/{battle_id}", response_model=BattleStateResponse)
async def get_battle_state(battle_id: str):
    """
    Obtiene el estado actual de la batalla.
    """
    if battle_id not in active_battles:
        raise HTTPException(status_code=404, detail="Battle not found")
    
    battle = active_battles[battle_id]
    return map_battle_to_response(battle_id, battle)

# --- Helper to Map Responses ---
def map_battle_to_response(battle_id: str, battle: Battle) -> BattleStateResponse:
    p1 = battle.trainer1.get_active_pokemon()
    p2 = battle.trainer2.get_active_pokemon()
    
    status1 = p1.current_status_effect.__class__.__name__ if p1.current_status_effect else None
    status2 = p2.current_status_effect.__class__.__name__ if p2.current_status_effect else None
    
    return BattleStateResponse(
        battle_id=battle_id,
        trainer1_name=battle.trainer1.name,
        trainer2_name=battle.trainer2.name,
        turn_count=battle.turn_count,
        current_turn_pokemon=PokemonState(name=p1.name, hp=p1.hp, max_hp=p1.max_hp, status=status1),
        opponent_pokemon=PokemonState(name=p2.name, hp=p2.hp, max_hp=p2.max_hp, status=status2),
        messages=battle.messages[-10:],
        weather=battle.weather,
        terrain=battle.terrain
    )