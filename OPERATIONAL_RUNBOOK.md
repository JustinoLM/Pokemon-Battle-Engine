
# Pokemon Battle Engine - Operational Runbook

## 1. How to Start the Server

```bash
#  Run the server (host 0.0.0.0 makes it accessible externally)
uv run uvicorn pokemon_battle_engine.api.main:app --reload --host 0.0.0.0 --port 8000
```

**Recommended Tmux Layout:**
*   Split the window into 3 panes (`Ctrl+b` then `%` for vertical, `"` for horizontal).
*   Pane 1: Run Uvicorn.
*   Pane 2: Run `tail -f logs/battle.log`.
*   Pane 3: Run `htop` (monitor resources).


## 2. How to Monitor Logs
The system uses **Structured Logging** (JSON format). Monitor battle events and errors in real-time.

```bash
# View all logs in real-time
tail -f logs/battle.log
```

**Filtering Logs (Useful for debugging):**
```bash
# Only see HTTP requests
tail -f logs/battle.log | grep "request"

# Only see Errors
tail -f logs/battle.log | grep "level\":\"error\""
```

## 3. How to Test the API (CLI)
Use `curl` to interact with the API endpoints directly from the command line, which is useful for automation and testing without the browser.

**Create a Battle:**
```bash
curl -X POST http://localhost:8000/battles \
  -H "Content-Type: application/json" \
  -d '{
    "trainer1": {"name": "Red", "team": ["pikachu"]},
    "trainer2": {"name": "Blue", "team": ["charizard"]}
  }'
```

**Execute a Turn:**
```bash
# Replace <BATTLE_ID> with the ID from the previous response
curl -X POST http://localhost:8000/battles/<BATTLE_ID>/turn \
  -H "Content-Type: application/json" \
  -d '{"attacker_name": "Red", "move_name": "tackle"}'
```