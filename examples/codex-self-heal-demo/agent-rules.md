# Agent Rules (Codex Self-Heal Demo)

## Working directory
All paths are relative to the repository root.

## Execution rules
- Work on only one task per iteration.
- Prefer the smallest coherent change.
- Only modify `orchestrator.py`.
- Stop and report if requirements are ambiguous.
- Do not redefine acceptance criteria.

## Research rules
- No external research is needed for this demo.
- All context is in the mission, backlog, tests, and source file.

## Validation rules
- Run `.venv/bin/python -m pytest tests/test_orchestrator.py -q` before marking complete.
- If validation fails, fix it in-scope or mark blocked.
- Never claim success without recorded evidence.

## Escalation rules
Escalate when:
- The task conflicts with mission or scope.
- A change outside `orchestrator.py` would be required.
- The same failure repeats twice.
