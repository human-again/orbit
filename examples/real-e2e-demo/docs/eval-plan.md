# Evaluation Plan: Real E2E Demo

## Classification Criteria

### success
- All 10 pytest tests pass.
- All 3 backlog tasks have `status: done` and `passes: true`.
- `progress.md` has at least 3 entries (one per task).
- Each `runtime/runs/<id>/evaluation.json` has `verdict: pass`.
- Each `runtime/runs/<id>/review.json` has `recommendation: accept`.

### partial_success
- At least 1 backlog task is `done` with `passes: true`.
- At least 1 pytest test passes.
- Harness did not crash — run artifacts exist.

### blocked
- Harness ran but agent could not complete a task due to an ambiguity or missing tool.
- At least one `runtime/runs/<id>/review.json` exists with `recommendation: iterate` or `blocked`.

### failure
- Harness crashed or produced no run artifacts.
- No backlog tasks advanced from `todo`.
- All pytest tests still fail after the run.

## Rubric Weights (used by evaluator.py)

| Dimension | Weight | Pass Condition |
|---|---|---|
| task_focus | 0.2 | Agent modified only `app/task_manager.py` |
| validation | 0.35 | Relevant pytest tests pass after the iteration |
| completion | 0.25 | Acceptance criteria explicitly satisfied |
| evidence | 0.1 | Changed files listed in agent result JSON |
| change_signal | 0.1 | `app/task_manager.py` diff is non-empty |

Pass threshold: **0.70**
