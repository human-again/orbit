from __future__ import annotations

from pathlib import Path

from .base import BaseAgentAdapter, AgentResult
from demo_fixtures import SCENARIOS


def _extract_task_id(task_bundle: str) -> str | None:
    for line in task_bundle.splitlines():
        if line.startswith("- ID: "):
            return line.removeprefix("- ID: ").strip()
    return None


class DemoReplayAdapter(BaseAgentAdapter):
    def __init__(self, scenario: str):
        if scenario not in SCENARIOS:
            raise ValueError(f"Unknown replay scenario: {scenario}")
        self.scenario = scenario

    def prepare_prompt(self, task_bundle: str) -> str:
        return task_bundle

    def run_agent(self, prompt: str, cwd: str, timeout_s: int) -> AgentResult:
        scenario = SCENARIOS[self.scenario]
        task_id = _extract_task_id(prompt)
        if task_id != scenario["task_id"]:
            return AgentResult(
                raw_output=prompt,
                status="failed",
                notes=f"Unexpected task id for scenario {self.scenario}: {task_id!r}",
                metadata={"scenario": self.scenario, "cwd": cwd, "timeout_s": str(timeout_s)},
            )

        target = Path(cwd) / scenario["target"]
        text = target.read_text(encoding="utf-8")
        if text == scenario["fixed"]:
            return AgentResult(
                raw_output=prompt,
                status="complete",
                changed_files=[],
                notes=f"Scenario {self.scenario} was already in the fixed state.",
                metadata={"scenario": self.scenario, "cwd": cwd, "timeout_s": str(timeout_s)},
            )
        if text != scenario["broken"]:
            return AgentResult(
                raw_output=prompt,
                status="failed",
                notes=f"Scenario {self.scenario} is not in the expected broken state.",
                metadata={"scenario": self.scenario, "cwd": cwd, "timeout_s": str(timeout_s)},
            )

        target.write_text(scenario["fixed"], encoding="utf-8")
        return AgentResult(
            raw_output=prompt,
            status="complete",
            changed_files=scenario["changed_files"],
            notes=f"Applied deterministic replay fix for {self.scenario}.",
            metadata={"scenario": self.scenario, "cwd": cwd, "timeout_s": str(timeout_s)},
        )
