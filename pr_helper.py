#!/usr/bin/env python3
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def current_branch(cwd: Path) -> str:
    proc = subprocess.run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], cwd=cwd, capture_output=True, text=True)
    return proc.stdout.strip() if proc.returncode == 0 else ''


def make_pr_instructions(task_id: str, title: str, cwd: Path) -> str:
    branch = current_branch(cwd)
    return f"Create a PR from branch `{branch}` for task `{task_id}` with title: {title}"
