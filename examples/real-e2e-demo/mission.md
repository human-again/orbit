# Mission: Real E2E Demo

## Objective
Implement three missing methods in the in-memory TaskManager so all pytest tests pass.

## In scope
- `app/task_manager.py` — the only file the agent may modify.
- One method per task, in dependency order.

## Out of scope
- Changes to tests.
- Changes to harness files.
- External dependencies or persistence.

## Definition of done
- All pytest tests in `app/test_task_manager.py` pass.
- Each backlog task is marked `done` with `passes: true`.
- Progress log records what changed after each iteration.
