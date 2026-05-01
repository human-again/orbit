# Issue Search

**What it demos:** Orbit adds a new feature (client-visible search) to a tiny issues dashboard, validates it with tests, and proves the orbit complete with a full artifact trail.

## Run it

```bash
# From the repo root — deterministic, no API key needed
MOCK=1 ./replay.sh issue-search

# Real agent
DEMO_ADAPTER=claude ./replay.sh issue-search
DEMO_ADAPTER=codex  ./replay.sh issue-search
```

## What happens

The mission asks for scoped search to be added to `app/dashboard.py`. Orbit selects the task, runs the agent, validates with `pytest tests -q`, and evaluates the result against the rubric. This is a feature-add orbit: the repo starts green, the agent adds the feature, and Orbit confirms the tests stay green after the change.

## Artifacts written

`runtime/runs/<timestamp>/`
- `agent-result.json` — what the agent did and which files it changed
- `evaluation.json` — rubric scores for task focus, completion, and validation
- `review.json` — accept/iterate recommendation
- `validation-summary.json` — raw test output and pass/fail verdict
