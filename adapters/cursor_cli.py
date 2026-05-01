import json
import subprocess
from .base import BaseAgentAdapter, AgentResult

class CursorCliAdapter(BaseAgentAdapter):
    def __init__(self, command='cursor-agent', args=None):
        self.command = command
        self.args = args or []

    def prepare_prompt(self, task_bundle: str) -> str:
        return task_bundle

    def run_agent(self, prompt: str, cwd: str, timeout_s: int) -> AgentResult:
        proc = subprocess.run([self.command, *self.args], input=prompt, text=True, capture_output=True, cwd=cwd, timeout=timeout_s)
        raw = (proc.stdout or '') + ('\n' + proc.stderr if proc.stderr else '')
        if proc.returncode != 0:
            return AgentResult(raw_output=raw, status='failed', notes='cursor CLI exited non-zero')
        try:
            payload = json.loads(proc.stdout)
            return AgentResult(
                raw_output=proc.stdout,
                status=payload.get('status', 'failed'),
                changed_files=payload.get('changed_files', []),
                notes=payload.get('notes', ''),
                metadata=payload.get('metadata', {}),
            )
        except Exception:
            return AgentResult(raw_output=raw, status='complete', notes='Non-JSON output; adapt parser for your CLI format.')
