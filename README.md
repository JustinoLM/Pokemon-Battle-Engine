
# Pokemon Battle Engine

![Python](https://img.shields.io/badge/python-3.11-blue.svg)
![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)
![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen.svg)
![MyPy](https://img.shields.io/badge/mypy-strict-success.svg)

A professional Python implementation of the Generation 1 Pokemon battle system, built with strict typing, SOLID principles, and test-driven development. This engine serves as a robust domain model for future expansion into competitive battle simulation.

##  Features

This engine implements a complete battle loop with attention to mechanical detail:

- **Advanced Damage Calculation:**
  - Damage formula including STAB (Same Type Attack Bonus) and Type Effectiveness.

  - Full 18x18 type chart matrix implementation.
  - **Critical Hits:** Implements logic to ignore negative user stat drops and positive opponent stat boosts. Includes support for the "Sniper" ability (2.25x damage).
  - Status penalties (e.g., Burn halves physical attack).

- **Comprehensive Battle System:**
  - **Turn Order:** Based on Move Priority and Speed stat.
  - **Stat Stages:** Full support for stat modifiers (Atk, Def, SpA, SpD, Spe, Acc, Eva) ranging from -6 to +6 with correct multipliers.
  - **End-of-Turn Processing:** Handles residual damage from Burns, Poison, and Badly Poisoned (Toxic).

- **Status Conditions:**
  - **Non-Volatile:** Burn, Paralysis, Sleep, Freeze, Poison, Badly Poisoned.
  - **Mechanics:** Includes type immunities (e.g., Fire immune to Burn), movement prevention (Paralysis, Sleep, Freeze), and wake-up/thaw probabilities.
  - **Secondary Effects:** Moves can trigger status conditions with configurable probabilities.

- **Clean Architecture:**
  - **Pure Domain:** Core logic is free of I/O (prints/files), relying on message passing for logging.
  - **SOLID Principles:** Uses Strategy Pattern for Damage Calculators and Status Effects.
  - **Type Safety:** 100% type-hinted code passing `mypy --strict`.
  
##  Week 1 Progress

* Pure Domain Model with Composition over Inheritance.
* Full Type Chart and Effectiveness Logic.
* Damage Calculation (Physical, Special, Status).
*  Status Conditions & End-of-Turn Ticks.
* Critical Hit Mechanics (w/ Stat Ignoring).
*  Stage Changes (Swords Dance, etc.).

## Future-Proofing (Scaffolding)

The data model is architected for seamless future expansion. The following structures are already in place to support upcoming features:
- **Abilities & Items:** Fields reserved for item and ability logic.
- **Movepools:** Support for assigning specific move lists to individual Pokemon.
- **Genetics:** IVs (Individual Values) structure ready for stat customization.

## Installation

This project uses `uv` for lightning-fast dependency management.

```bash
# Install dependencies
uv sync

# Run tests
make test

# Lint and Type Check
make lint

# Run a battle demo
make run
```

## Architecture

The project follows a strict `src` layout to enforce separation of concerns:

*   `src/pokemon_battle_engine/domain/models.py`: Core entities (`Pokemon`, `Move`, `Type`) and Strategy patterns (`DamageCalculator`, `StatusEffect`).

*   `src/pokemon_battle_engine/domain/constants.py`: Static data definitions (Type Charts, Multipliers, Type Singletons).

*   `src/pokemon_battle_engine/domain/battle.py`: The Mediator pattern orchestrating the fight, turn order, and state transitions.

*   `src/pokemon_battle_engine/main.py`: A simulation demo showing random combat scenarios.

## Tech Stack

*   **Python 3.11+**
*   **Type Checking:** `mypy --strict`
*   **Testing:** `pytest` with fixtures and parametrize.
*   **Quality:** `ruff` for linting.
*   **Management:** `uv`

## Run a Demo

To see a random battle simulation featuring mechanics like Critical Hits, Stat Boosts, and Status Effects:

```bash
uv run python src/pokemon_battle_engine/main.py
```

¡Increíble! Has alcanzado la **Cobertura del 100%** y el tipado estricto sin errores (`mypy --strict`). Eso es el estándar de oro para proyectos Python profesionales.

Para reflejar este logro en tu `README.md`, te sugiero agregar una sección de **"Quality Assurance" (Aseguramiento de Calidad)**. Esto demuestra a cualquier reclutador o usuario que el código no solo funciona, sino que es robusto y mantenible.

Agrega esta sección justo después de "Architecture" o antes de "Run a Demo".

## Quality Assurance

This project adheres to strict engineering standards to ensure reliability and maintainability.

- **100% Domain Test Coverage:** Every line of the domain logic (`models`, `battle`, `constants`) is covered by unit tests. This includes complex mechanics like critical hit stat ignoring, status effect immunities, and multi-stage stat modifications.

- **Strict Type Safety:** The entire domain layer passes `mypy --strict`, ensuring type correctness at compile time and preventing a wide class of runtime errors.

- **Comprehensive Testing Strategy:**
    - **Fixtures & Factories:** Reusable test data setup for consistent test environments.
    - **Mocking:** Used effectively to isolate randomness (e.g., critical hits, status proc chances) and test edge cases deterministically.
    - **TDD Approach:** Features are developed and tested incrementally.

**Running the Quality Suite:**

To verify the code quality yourself, run the following commands:

```bash
# Run the full test suite with coverage report
make test
# Expected: > 90% coverage (Currently 100%)

# Run static type checking
make lint
# Expected: Success: no issues found
```

