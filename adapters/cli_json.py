import json
import subprocess
from .base import BaseAgentAdapter, AgentResult

class CliJsonAdapter(BaseAgentAdapter):
    def __init__(self, command='python', args=None):
        self.command = command
        self.args = args or []

    def prepare_prompt(self, task_bundle: str) -> str:
        return task_bundle

    def run_agent(self, prompt: str, cwd: str, timeout_s: int) -> AgentResult:
        cmd = [self.command, *self.args]
        proc = subprocess.run(cmd, input=prompt, text=True, capture_output=True, cwd=cwd, timeout=timeout_s)
        if proc.returncode != 0:
            return AgentResult(raw_output=proc.stdout + proc.stderr, status='failed', notes='CLI exited non-zero')
        try:
            payload = json.loads(proc.stdout)
        except json.JSONDecodeError:
            return AgentResult(raw_output=proc.stdout, status='failed', notes='CLI did not return valid JSON')
        return AgentResult(
            raw_output=proc.stdout,
            status=payload.get('status', 'failed'),
            changed_files=payload.get('changed_files', []),
            notes=payload.get('notes', ''),
            metadata=payload.get('metadata', {}),
        )

    def supports_tools(self) -> bool:
        return True
