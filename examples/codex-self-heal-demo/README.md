# Codex Self-Heal Demo

**What it demos:** Orbit uses its own Codex adapter to repair a real regression *inside a copy of Orbit itself* — proving the harness can direct a coding agent to fix the harness.

## Run it

```bash
# From the repo root
.venv/bin/python examples/codex-self-heal-demo/run_demo.py
```

> Requires the Codex CLI (`codex`) on your `$PATH` with a valid `OPENAI_API_KEY`. No `MOCK=1` shortcut — this demo runs a real agent.

## What happens

`run_demo.py` copies the Orbit repo into a temp workspace, reintroduces a known regression in `orchestrator.py`, then launches Orbit with the Codex adapter to fix it. The orbit completes when `tests/test_orchestrator.py` passes and evaluation confirms the diff is targeted and correct.

This is the deepest technical proof: the harness directing an agent to fix itself, with no human in the loop.

## Artifacts written

`runtime/runs/<timestamp>/`
- `agent-result.json` — what Codex changed
- `evaluation.json` — rubric scores
- `review.json` — accept/iterate recommendation
- `validation-summary.json` — test output confirming the fix
