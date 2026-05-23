# Pokemon Battle Engine - Operational Runbook

## 1. How to Start the Server
Start the battle engine in the background with auto-reload enabled.

```bash
# Using the Makefile
make run
```

## 2. How to Check Status
Verify the `uvicorn` process is running.

```bash
# Find the Process ID (PID)
ps aux | grep uvicorn
```

## 3. How to Monitor Logs
Tail the log file in real-time to see battle events.

```bash
# Follow the file
tail -f logs/battle.log
```
*(Note: Logging is not implemented yet).*

## 4. How to Stop the Server
Gracefully stop the service.

```bash
# 1. Find the PID
ps aux | grep uvicorn

# 2. Kill the process
kill <PID>
```

## 5. Troubleshooting: Port Already in Use
If you see `OSError: [Errno 48] Address already in use`:

```bash
# Find what is using port 8000
lsof -i :8000
```