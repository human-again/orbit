from dataclasses import dataclass, field
from typing import Dict, List, Literal

AgentStatus = Literal["complete", "blocked", "needs_human", "failed"]

@dataclass
class AgentResult:
    raw_output: str
    status: AgentStatus
    changed_files: List[str] = field(default_factory=list)
    notes: str = ""
    metadata: Dict[str, str] = field(default_factory=dict)

class BaseAgentAdapter:
    def prepare_prompt(self, task_bundle: str) -> str:
        raise NotImplementedError

    def run_agent(self, prompt: str, cwd: str, timeout_s: int) -> AgentResult:
        raise NotImplementedError

    def extract_status(self, result: AgentResult) -> AgentStatus:
        return result.status

    def extract_artifacts(self, result: AgentResult) -> Dict:
        return {
            "changed_files": result.changed_files,
            "notes": result.notes,
            "metadata": result.metadata,
        }

    def supports_tools(self) -> bool:
        return False
