# Pokemon Battle Engine

![Python](https://img.shields.io/badge/python-3.11-blue.svg)
![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)
![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen.svg)
![MyPy](https://img.shields.io/badge/mypy-strict-success.svg)

A professional Python implementation of the Pokemon battle system, evolved into a production-ready **REST API**. Built with strict typing, SOLID principles, async I/O, and comprehensive observability. This engine serves as a robust foundation for competitive battle simulation and backend services.

## Features

This engine implements a complete battle loop and exposes it via a modern API, with attention to mechanical detail and operational excellence:

### Core Battle Mechanics
- **Advanced Damage Calculation:**
  - Full damage formula including STAB, Type Effectiveness (18x18 matrix), and Critical Hits.
  - **Field Conditions:** Dynamic Weather (Rain, Sun, Sandstorm, Hail) and Terrain (Electric, Grassy, Psychic, Misty) affecting damage and status.
  - **Hazards:** Entry hazard layer logic (Spikes, Stealth Rock, Toxic Spikes) with switch-in damage calculation.
  - **Complex Items:** Logic for Knock Off, Trick, Covert Cloak, Loaded Dice, Weakness Policy, and Life Orb recoil.
  - **Substitute System:** Damage absorption, sound move piercing, and HP drain.
  - **Volatile Status:** Taunt, Encore, Torment, Confusion (self-damage), Attract, and Flinch logic with turn-based decay.

### Modern API & Infrastructure
- **FastAPI Backend:**
  - Async endpoints for Battle Creation (`POST /battles`), Turn Execution (`POST /battles/{id}/turn`), and State Retrieval (`GET /battles/{id}`).
  - **Pydantic Schemas:** Strict separation between Domain Models and API DTOs.
  - **Error Handling:** Custom exception hierarchy mapped to standard HTTP status codes (400, 404, 409).
- **External Integration:**
  - **PokeAPI Client:** Async client to fetch real-time Pokemon stats, types, and base data.
- **Observability (Ops Ready):**
  - **Structured Logging:** JSON-formatted logs using `structlog` for production monitoring and analysis.
  - **Request Tracing:** Unique Request IDs injected via Middleware for distributed tracing context.
  - **Operational Runbook:** Documented procedures for Tmux session management, process monitoring (`htop`), and troubleshooting (`lsof`, `curl`).

### Clean Architecture
- **Pure Domain:** Core logic is free of I/O (prints/files), relying on message passing and dependency injection.
- **SOLID Principles:** Strategy Pattern for Damage Calculators and Status Effects; Composition over Inheritance.
- **Type Safety:** 100% type-hinted code passing `mypy --strict`.

## Project Progress

### Week 1: Domain Model & Core Engine
* Pure Domain Model with Composition over Inheritance.
* Full Type Chart and Effectiveness Logic.
* Damage Calculation (Physical, Special, Status).
* Status Conditions (Burn, Poison, Paralysis, etc.) & End-of-Turn Ticks.
* Critical Hit Mechanics (w/ Stat Ignoring).
* Stage Changes (Swords Dance, etc.).
* Multi-hit Moves & Item Interactions.

### Week 2: API & Operational Excellence
* **FastAPI Server:** Creation of RESTful endpoints with Pydantic validation.
* **Async I/O:** Implementation of `PokeAPIClient` for non-blocking data fetching.
* **Structured Logging:** Configuration of `structlog` for JSON output and file rotation.

## Installation

This project uses `uv` for lightning-fast dependency management.

```bash
# Install dependencies
uv sync

# Run the API Server
uv run uvicorn pokemon_battle_engine.api.main:app --reload

# Run tests
make test

# Lint and Type Check
make lint
```

## Architecture

The project follows a strict `src` layout to enforce separation of concerns:

*   `src/pokemon_battle_engine/domain/models.py`: Core entities (`Pokemon`, `Move`, `Type`), Strategy patterns, and advanced mechanics (Hazards, Weather).
*   `src/pokemon_battle_engine/domain/constants.py`: Static data definitions (Type Charts, Weather/Terrain configurations).
*   `src/pokemon_battle_engine/domain/battle.py`: The Mediator pattern orchestrating the fight, turn order, and complex state transitions.
*   `src/pokemon_battle_engine/api/main.py`: FastAPI application, exception handlers, and middleware for logging.
*   `src/pokemon_battle_engine/infra/`: Infrastructure layer (PokeAPI client, Logging configuration).
*   `Deployment Runbook.md`: Operational guide for running and monitoring the server on Linux.

## Tech Stack

*   **Python 3.11+**
*   **Web Framework:** FastAPI (Async), Uvicorn.
*   **External Data:** PokeAPI (Async Client), httpx.
*   **Observability:** Structlog, Python Logging.
*   **Type Checking:** `mypy --strict`
*   **Testing:** `pytest` with fixtures and parametrize.
*   **Quality:** `ruff` for linting.
*   **Management:** `uv`

## Quick Start

### 1. Start the Server
```bash
uv run uvicorn pokemon_battle_engine.api.main:app --reload
```
Access the interactive documentation at **http://127.0.0.1:8000/docs**.

### 2. Create a Battle (via cURL)
```bash
curl -X POST http://127.0.0.1:8000/battles \
  -H "Content-Type: application/json" \
  -d '{
    "trainer1": {"name": "Ash", "team": ["pikachu"]},
    "trainer2": {"name": "Gary", "team": ["blastoise"]}
  }'
```

### 3. Monitor Logs
```bash
tail -f logs/battle.log
```

## Quality Assurance

This project adheres to strict engineering standards to ensure reliability and maintainability.

- **Strict Type Safety:** The entire domain layer passes `mypy --strict`, ensuring type correctness at compile time and preventing a wide class of runtime errors.
- **Clean Architecture:** clear separation between Domain (Business Logic), API (Interface), and Infrastructure (External I/O).
- **Operational Readiness:** Includes logging strategies and process management guides suitable for production environments.

**Running the Quality Suite:**

To verify the code quality yourself, run the following commands:

```bash
# Run the full test suite with coverage report
make test

# Run static type checking
make lint
```