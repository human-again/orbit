# Mission: Python CLI Tool

## Objective
Build a well-tested Python CLI with argument parsing, helpful `--help` text, and correct exit codes.

## In scope
- Entry point registered in `pyproject.toml` (or `setup.py`)
- Argument parsing with `argparse` or `click`
- Subcommands if needed
- Unit tests for each command path
- Correct exit codes: 0 on success, non-zero on error

## Out of scope
- GUI or TUI (separate effort)
- Network or database calls (handle in a separate mission once the CLI skeleton exists)

## Definition of done
- `--help` prints useful, accurate output for all commands and flags
- All subcommands are tested (happy path + error path)
- Non-zero exit on any error condition with a human-readable message
- The backlog task is marked `done` with `passes: true`
