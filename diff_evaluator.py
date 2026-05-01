#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def git_diff(cwd: Path) -> str:
    proc = subprocess.run(['git', 'diff', '--stat', '--', '.'], cwd=cwd, capture_output=True, text=True)
    if proc.returncode != 0:
        return ''
    return proc.stdout


def evaluate_diff(run_dir: Path, cwd: Path) -> dict:
    diffstat = git_diff(cwd)
    result = {
        'has_diff': bool(diffstat.strip()),
        'diffstat': diffstat,
        'files_changed_estimate': len([line for line in diffstat.splitlines() if '|' in line]),
    }
    (run_dir / 'diff-evaluation.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    return result
