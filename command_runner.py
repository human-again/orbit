#!/usr/bin/env python3
import subprocess
from pathlib import Path
from risk_guard import classify
from observability import emit

ROOT = Path(__file__).resolve().parent

class CommandBlockedError(RuntimeError):
    pass


def run_command(command: str, cwd: Path, require_approval: bool = False) -> dict:
    decision = classify(command)
    emit('command_classified', {'command': command, 'level': decision.level, 'allowed': decision.allowed, 'reason': decision.reason})
    if not decision.allowed:
        if decision.level == 'high' and require_approval:
            emit('command_waiting_approval', {'command': command})
        raise CommandBlockedError(f'{decision.level}: {decision.reason} :: {command}')
    proc = subprocess.run(command, shell=True, cwd=cwd, capture_output=True, text=True)
    result = {
        'command': command,
        'returncode': proc.returncode,
        'stdout': proc.stdout,
        'stderr': proc.stderr,
        'risk_level': decision.level,
    }
    emit('command_finished', {'command': command, 'returncode': proc.returncode, 'risk_level': decision.level})
    return result
