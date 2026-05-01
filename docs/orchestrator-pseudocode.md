# Orchestrator Pseudocode

```text
load mission, rules, backlog, progress
load config
for iteration in 1..max_iterations:
  choose highest-priority task whose dependencies are done
  if no task remains: stop success
  build task bundle
  if task.needs_research and allow_research:
    create or refresh research brief
  prompt = adapter.prepare_prompt(task_bundle)
  result = adapter.run_agent(prompt, cwd=repo_root, timeout_s=agent_timeout)
  run validation commands if required
  write eval outputs
  update backlog status and passes flag
  append concise note to progress.md
  if result.status in ["blocked", "needs_human", "failed"]: stop or escalate
  if no progress streak exceeds threshold: stop
end
```
