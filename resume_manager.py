#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BACKLOG = ROOT / 'backlog.json'
CHECKPOINT = ROOT / 'runtime' / 'checkpoints' / 'last.json'


def first_incomplete_task():
    if not BACKLOG.exists():
        return None
    tasks = json.loads(BACKLOG.read_text(encoding='utf-8'))
    for task in tasks:
        if task.get('status') != 'done':
            return task
    return None


def resume_target():
    if CHECKPOINT.exists():
        cp = json.loads(CHECKPOINT.read_text(encoding='utf-8'))
        return {'mode': 'checkpoint', 'task_id': cp.get('task_id'), 'checkpoint': cp}
    task = first_incomplete_task()
    return {'mode': 'backlog', 'task_id': task.get('id') if task else None, 'checkpoint': None}
