#!/usr/bin/env python3
import shlex
from dataclasses import dataclass

@dataclass
class RiskDecision:
    level: str
    allowed: bool
    reason: str

BLOCKED_PATTERNS = ['rm -rf /', 'sudo rm', 'mkfs', ':(){ :|:& };:', 'shutdown', 'reboot']
HIGH_RISK_PATTERNS = ['git push --force', 'terraform apply', 'kubectl delete', 'drop table', 'npm publish', 'docker system prune -a']
LOW_RISK_PREFIXES = ['cat ', 'ls', 'pwd', 'grep ', 'find ', 'python -m py_compile', 'pytest', 'npm test', 'npm run lint', 'npm run typecheck']


def _is_python_validation_command(command: str) -> bool:
    try:
        parts = shlex.split(command)
    except ValueError:
        return False
    if len(parts) < 3:
        return False
    executable = parts[0]
    if not executable.endswith('python') and not executable.endswith('python3'):
        return False
    return parts[1:3] in (['-m', 'pytest'], ['-m', 'py_compile'])


def classify(command: str) -> RiskDecision:
    c = command.strip().lower()
    if any(p in c for p in BLOCKED_PATTERNS):
        return RiskDecision('blocked', False, 'Command matches blocked pattern.')
    if any(p in c for p in HIGH_RISK_PATTERNS):
        return RiskDecision('high', False, 'Command requires explicit human approval.')
    if _is_python_validation_command(command):
        return RiskDecision('low', True, 'Python validation command is allowlisted.')
    if any(c.startswith(p) for p in LOW_RISK_PREFIXES):
        return RiskDecision('low', True, 'Command is in low-risk allowlist.')
    return RiskDecision('medium', False, 'Command not allowlisted; require review.')
