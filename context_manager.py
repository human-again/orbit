#!/usr/bin/env python3
from pathlib import Path

MAX_CHARS = 12000
HEAD_CHARS = 4000
TAIL_CHARS = 4000


def compact_text(text: str) -> str:
    if len(text) <= MAX_CHARS:
        return text
    head = text[:HEAD_CHARS]
    tail = text[-TAIL_CHARS:]
    omitted = len(text) - HEAD_CHARS - TAIL_CHARS
    return f"""{head}

...[omitted {omitted} chars]...

{tail}"""


def compact_file(path: Path) -> str:
    return compact_text(path.read_text(encoding='utf-8', errors='ignore'))
