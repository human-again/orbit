# Mission: Codex Self-Heal Demo

## Objective
Repair Orbit's Codex integration plumbing in `orchestrator.py` so the harness gives Codex the exact validation context it will enforce and routes validation through the risk-gated command path.

## In scope
- `orchestrator.py` only.
- One task, one orbit.

## Out of scope
- Changes to tests.
- Changes to adapters, demo files, or documentation.
- New dependencies.

## Definition of done
- `tests/test_orchestrator.py` passes.
- The backlog task is marked `done` with `passes: true`.
- The run directory contains `agent-result.json`, `evaluation.json`, `review.json`, and `validation-summary.json`.
