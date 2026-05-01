# Agent Rules (E2E Demo)

## Working directory
All paths are relative to `examples/real-e2e-demo/`.

## Execution rules
- Work on only one task per iteration.
- Prefer the smallest coherent change.
- Only modify `app/task_manager.py` — no other files.
- Stop and report if requirements are ambiguous.
- Do not redefine acceptance criteria.

## Research rules
- No external research is needed for this demo.
- All context is in the mission, backlog, and source file.

## Validation rules
- Run `../../.venv/bin/python -m pytest app/test_task_manager.py -v` before marking complete.
- If validation fails, fix it in-scope or mark blocked.
- Never claim success without recorded evidence.

## Escalation rules
Escalate when:
- The task conflicts with mission or scope.
- A change to tests or harness files would be required.
- The same failure repeats twice.
