from .base import BaseAgentAdapter, AgentResult

class MockAgentAdapter(BaseAgentAdapter):
    def prepare_prompt(self, task_bundle: str) -> str:
        return task_bundle

    def run_agent(self, prompt: str, cwd: str, timeout_s: int) -> AgentResult:
        return AgentResult(
            raw_output=prompt,
            status="complete",
            changed_files=[],
            notes="Mock run completed. Replace with a real adapter.",
            metadata={"timeout_s": str(timeout_s), "cwd": cwd},
        )
