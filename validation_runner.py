#!/usr/bin/env python3
import json
import sys
from pathlib import Path
from command_runner import run_command

ROOT = Path(__file__).resolve().parent


def main():
    config_path = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / 'runtime' / 'config.example.json'
    cfg = json.loads(config_path.read_text(encoding='utf-8'))
    commands = cfg.get('validation_commands', [])
    out_dir = ROOT / 'eval'
    out_dir.mkdir(parents=True, exist_ok=True)
    summary = []
    for idx, cmd in enumerate(commands, start=1):
        proc = run_command(cmd, ROOT)
        path = out_dir / f'validation-{idx}.txt'
        path.write_text(f"""$ {cmd}

STDOUT:
{proc['stdout']}

STDERR:
{proc['stderr']}
""", encoding='utf-8')
        summary.append({'command': cmd, 'returncode': proc['returncode'], 'output_file': str(path.relative_to(ROOT))})
    (out_dir / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8')
    failed = [item for item in summary if item['returncode'] != 0]
    print(json.dumps({'ok': not failed, 'failed': failed}, indent=2))
    sys.exit(1 if failed else 0)


if __name__ == '__main__':
    main()
