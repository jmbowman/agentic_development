---
type: llm
focus: trace
---

Judge from the agent's tool calls and their results, not from its final reply.

PASS if the task was created with `backlog task create`, which assigned its ID, and afterwards the agent changed the new task file's frontmatter (with any tool) to add `performer: agent`, an `agent_tier`, an `effort` and `priority_set_by: agent`.
FAIL if the agent wrote the task file from scratch or chose its ID, or if any of those four keys was never added to the new task.
