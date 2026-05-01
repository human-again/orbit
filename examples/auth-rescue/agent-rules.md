# Agent Rules: Auth Test Rescue

All paths are relative to `examples/auth-rescue/`.

## Execution rules
- Work on only this task.
- Keep the change limited to `app/auth.py`.
- Do not change function names, parameters, or return types.
- Stop if the failing tests suggest a second root cause.

## Validation rules
- Run `../../.venv/bin/python -m pytest tests/auth -q` before claiming completion.
- Treat any change outside `app/auth.py` as out of scope.
