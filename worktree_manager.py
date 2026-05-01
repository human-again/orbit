#!/usr/bin/env python3
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
WORKTREES = ROOT / 'runtime' / 'worktrees'


def repo_has_git() -> bool:
    return (ROOT / '.git').exists()


def create_worktree(task_id: str) -> Path:
    WORKTREES.mkdir(parents=True, exist_ok=True)
    target = WORKTREES / task_id
    if target.exists():
        return target
    if repo_has_git():
        branch = f'agent/{task_id}'
        subprocess.run(['git', 'worktree', 'add', '-b', branch, str(target)], cwd=ROOT, check=True)
    else:
        shutil.copytree(ROOT, target, dirs_exist_ok=True, ignore=shutil.ignore_patterns('runtime/worktrees', 'eval', '__pycache__', '*.zip'))
    return target


def cleanup_worktree(task_id: str):
    target = WORKTREES / task_id
    if not target.exists():
        return
    if repo_has_git():
        subprocess.run(['git', 'worktree', 'remove', str(target), '--force'], cwd=ROOT, check=False)
    else:
        shutil.rmtree(target, ignore_errors=True)
