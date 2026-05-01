# Agent Rules: Issue Search Demo

All paths are relative to `examples/issue-search/`.

## Execution rules
- Work on only this task.
- Keep the change limited to `app/dashboard.py`.
- Preserve the existing list view and add search without changing unrelated markup.
- Stop if you need a second file to make the tests pass.

## Validation rules
- Run `../../.venv/bin/python -m pytest tests -q` before claiming completion.
- The filtered results must match issue titles case-insensitively.
