#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CHECKPOINTS = ROOT / 'runtime' / 'checkpoints'
LAST = CHECKPOINTS / 'last.json'


def save_checkpoint(payload: dict):
    CHECKPOINTS.mkdir(parents=True, exist_ok=True)
    LAST.write_text(json.dumps(payload, indent=2) + '\n', encoding='utf-8')


def load_checkpoint() -> dict:
    if LAST.exists():
        return json.loads(LAST.read_text(encoding='utf-8'))
    return {}
