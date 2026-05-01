import json
import subprocess
from .base import BaseAgentAdapter, AgentResult


def _extract_json(text: str) -> dict:
    """Extract the last valid JSON object from text that may include natural language."""
    # Try the whole text first (handles clean JSON output)
    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        pass
    # Scan for { positions from right to left and try each as a JSON start
    for pos in range(len(text) - 1, -1, -1):
        if text[pos] == '{':
            try:
                return json.loads(text[pos:])
            except json.JSONDecodeError:
                continue
    raise ValueError("No valid JSON object found in text")


class ClaudeCliAdapter(BaseAgentAdapter):
    def __init__(self, command='claude', args=None):
        self.command = command
        self.args = args or ['--print']

    def prepare_prompt(self, task_bundle: str) -> str:
        instruction = (
            "\n\n## Required output format\n"
            "After completing all file edits, respond ONLY with this JSON "
            "(no markdown fences, no extra text):\n"
            '{"status": "complete", "changed_files": ["<path-to-modified-file>"], '
            '"notes": "One-line description of what was implemented"}\n'
            'Use "blocked" if requirements are ambiguous, "failed" if you cannot implement.'
        )
        return task_bundle + instruction

    def run_agent(self, prompt: str, cwd: str, timeout_s: int) -> AgentResult:
        proc = subprocess.run(
            [self.command, *self.args],
            input=prompt,
            text=True,
            capture_output=True,
            cwd=cwd,
            timeout=timeout_s,
        )
        raw = (proc.stdout or '') + ('\n' + proc.stderr if proc.stderr else '')
        if proc.returncode != 0:
            return AgentResult(raw_output=raw, status='failed', notes='claude CLI exited non-zero')
        try:
            # --output-format json wraps Claude's response in an outer envelope
            envelope = json.loads(proc.stdout)
            inner = envelope.get('result', proc.stdout)  # Claude's actual response text
            payload = _extract_json(inner)               # handles mixed text + JSON output
            return AgentResult(
                raw_output=proc.stdout,
                status=payload.get('status', 'failed'),
                changed_files=payload.get('changed_files', []),
                notes=payload.get('notes', ''),
                metadata=payload.get('metadata', {}),
            )
        except Exception as exc:
            return AgentResult(
                raw_output=raw,
                status='failed',
                notes=f'Could not parse adapter output: {exc}',
            )
