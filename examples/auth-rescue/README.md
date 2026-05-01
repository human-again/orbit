# Auth Rescue

**What it demos:** Orbit detects a broken auth module, selects the repair task, runs the agent, turns failing tests green, and closes the orbit with a full evaluation artifact.

## Run it

```bash
# From the repo root — deterministic, no API key needed
MOCK=1 ./replay.sh auth-rescue

# Real agent
DEMO_ADAPTER=claude ./replay.sh auth-rescue
DEMO_ADAPTER=codex  ./replay.sh auth-rescue
```

## What happens

A small regression is introduced into `app/auth.py` so the mission starts red. Orbit selects the single task in `backlog.json`, hands it to the agent with the full mission context, and runs `pytest tests/auth -q` to validate the fix. The orbit closes only when tests pass and a structured evaluation scores the result.

## Artifacts written

`runtime/runs/<timestamp>/`
- `agent-result.json` — what the agent did and which files it changed
- `evaluation.json` — rubric scores for task focus, completion, and validation
- `review.json` — accept/iterate recommendation
- `validation-summary.json` — raw test output and pass/fail verdict
