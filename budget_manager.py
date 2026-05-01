#!/usr/bin/env python3
import json
from dataclasses import dataclass, asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
STATE_PATH = ROOT / 'runtime' / 'budget-state.json'

@dataclass
class BudgetState:
    max_runs: int = 50
    max_failures: int = 10
    max_validation_failures: int = 10
    max_estimated_cost_usd: float = 25.0
    used_runs: int = 0
    failures: int = 0
    validation_failures: int = 0
    estimated_cost_usd: float = 0.0


def load_state() -> BudgetState:
    if not STATE_PATH.exists():
        state = BudgetState()
        save_state(state)
        return state
    return BudgetState(**json.loads(STATE_PATH.read_text(encoding='utf-8')))


def save_state(state: BudgetState):
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(asdict(state), indent=2) + '\n', encoding='utf-8')


def can_run() -> tuple[bool, str]:
    state = load_state()
    if state.used_runs >= state.max_runs:
        return False, 'Run budget exhausted.'
    if state.failures >= state.max_failures:
        return False, 'Failure budget exhausted.'
    if state.validation_failures >= state.max_validation_failures:
        return False, 'Validation failure budget exhausted.'
    if state.estimated_cost_usd >= state.max_estimated_cost_usd:
        return False, 'Cost budget exhausted.'
    return True, 'ok'


def record_run(estimated_cost_usd: float = 0.0, failed: bool = False, validation_failed: bool = False):
    state = load_state()
    state.used_runs += 1
    state.estimated_cost_usd += estimated_cost_usd
    if failed:
        state.failures += 1
    if validation_failed:
        state.validation_failures += 1
    save_state(state)
