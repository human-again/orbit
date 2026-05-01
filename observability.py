#!/usr/bin/env python3
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
EVENTS = ROOT / 'runtime' / 'events.jsonl'


def emit(event_type: str, payload: dict):
    EVENTS.parent.mkdir(parents=True, exist_ok=True)
    record = {
        'ts': datetime.now(timezone.utc).isoformat(),
        'type': event_type,
        'payload': payload,
    }
    with EVENTS.open('a', encoding='utf-8') as f:
        f.write(json.dumps(record) + '\n')
