# Phase 2 Notes

This phase adds:
- `orchestrator.py` to run the one-task-per-iteration loop.
- `validation_runner.py` to execute validation commands and persist outputs.
- `adapters/cli_json.py` as a generic wrapper for any CLI that reads stdin and emits JSON.
- Prompt templates for coding and research workers.
- A phase-2 config example and a sample research file.

## Expected JSON from a real CLI adapter
```json
{
  "status": "complete",
  "changed_files": ["src/app.py", "tests/test_app.py"],
  "notes": "Implemented token refresh and added tests.",
  "metadata": {"model": "example-agent"}
}
```
