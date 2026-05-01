# Mission: Issue Search Demo

## Objective
Add client-visible search to the tiny issues dashboard and prove it through tests and a browser preview.

## In scope
- `app/dashboard.py` only.
- One task, one orbit.

## Out of scope
- Changes to tests.
- New backend services.
- Refactors outside the dashboard rendering module.

## Definition of done
- `pytest tests -q` passes.
- The backlog task is marked `done` with `passes: true`.
- The run directory contains `agent-result.json`, `evaluation.json`, `review.json`, and `validation-summary.json`.
