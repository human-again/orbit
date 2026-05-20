import json
import subprocess

from .base import AgentResult, BaseAgentAdapter


def _extract_json(text: str) -> dict:
    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        pass

    for pos in range(len(text) - 1, -1, -1):
        if text[pos] == '{':
            try:
                return json.loads(text[pos:])
            except json.JSONDecodeError:
                continue

    raise ValueError("No valid JSON object found in Gemini output")


class GeminiCliAdapter(BaseAgentAdapter):
    def __init__(self, command='gemini', args=None):
        self.command = command
        self.args = args or ['-p']

    def prepare_prompt(self, task_bundle: str) -> str:
        instruction = (
            "\n\n## Required output format\n"
            "After completing all file edits, respond ONLY with this JSON "
            "(no markdown fences, no extra text):\n"
            '{"status": "complete", "changed_files": ["<path-to-modified-file>"], '
            '"notes": "One-line description of what was implemented", "metadata": {}}\n'
            'Use "blocked" if requirements are ambiguous, "failed" if you cannot implement.'
        )
        return task_bundle + instruction

    def run_agent(self, prompt: str, cwd: str, timeout_s: int) -> AgentResult:
        proc = subprocess.run(
            [self.command, *self.args, prompt],
            text=True,
            capture_output=True,
            cwd=cwd,
            timeout=timeout_s,
        )
        raw = (proc.stdout or '') + ('\n' + proc.stderr if proc.stderr else '')
        if proc.returncode != 0:
            return AgentResult(raw_output=raw, status='failed', notes='gemini CLI exited non-zero')

        try:
            payload = _extract_json(proc.stdout)
            return AgentResult(
                raw_output=raw,
                status=payload.get('status', 'failed'),
                changed_files=payload.get('changed_files', []),
                notes=payload.get('notes', ''),
                metadata=payload.get('metadata', {}),
            )
        except Exception as exc:
            return AgentResult(
                raw_output=raw,
                status='failed',
                notes=f'Could not parse Gemini output: {exc}',
            )
