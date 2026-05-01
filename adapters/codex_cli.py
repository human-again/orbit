import json
import subprocess
from .base import BaseAgentAdapter, AgentResult


def _extract_final_agent_message(stdout: str) -> str:
    last_message = None
    for line in stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        item = event.get("item") or {}
        if event.get("type") == "item.completed" and item.get("type") == "agent_message":
            last_message = item.get("text", "")
    if last_message is None:
        raise ValueError("No final agent message found in Codex JSONL output")
    return last_message


class CodexCliAdapter(BaseAgentAdapter):
    def __init__(self, command='codex', args=None):
        self.command = command
        self.args = args or ['exec', '--skip-git-repo-check', '--json']

    def prepare_prompt(self, task_bundle: str) -> str:
        instruction = (
            "\n\n## Required output format\n"
            'Return ONLY JSON with keys "status", "changed_files", "notes", "metadata".\n'
            'Use one of these statuses: "complete", "blocked", "needs_human", "failed".\n'
            "Do not wrap the JSON in markdown fences or add surrounding commentary."
        )
        return task_bundle + instruction

    def run_agent(self, prompt: str, cwd: str, timeout_s: int) -> AgentResult:
        proc = subprocess.run([self.command, *self.args], input=prompt, text=True, capture_output=True, cwd=cwd, timeout=timeout_s)
        raw = (proc.stdout or '') + ('\n' + proc.stderr if proc.stderr else '')
        if proc.returncode != 0:
            return AgentResult(raw_output=raw, status='failed', notes='codex CLI exited non-zero')
        try:
            payload = json.loads(_extract_final_agent_message(proc.stdout))
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
                notes=f'Could not parse Codex output: {exc}',
            )
