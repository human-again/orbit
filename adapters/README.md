# Adapters

Each adapter wraps a coding agent so the orchestrator can stay vendor-neutral.

Suggested files:
- `base.py` — shared interface and result model.
- `mock.py` — local mock adapter for testing the harness.
- `claude_cli.py`, `codex_cli.py`, `cursor_cli.py` — optional provider wrappers.
