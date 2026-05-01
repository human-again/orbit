# Mission: Auth Test Rescue

## Objective
Fix the failing auth tests in `tests/auth/` without changing the public API exposed by `app/auth.py`.

## In scope
- `app/auth.py` only.
- One task, one orbit.

## Out of scope
- Changes to tests.
- Changes to harness files.
- Refactors outside the auth module.

## Definition of done
- `pytest tests/auth -q` passes.
- The backlog task is marked `done` with `passes: true`.
- The run directory contains `agent-result.json`, `evaluation.json`, `review.json`, and `validation-summary.json`.
