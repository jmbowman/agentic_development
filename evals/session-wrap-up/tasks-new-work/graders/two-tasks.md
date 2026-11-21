---
type: llm
---

The developer will write the release-notes highlights first, and the agent's changelog draft has to wait for them.

PASS if the release notes become one numbered item that creates two tasks: one for the developer (performer `human`) to write the highlights, and one for an agent (performer `agent`) to draft the changelog section that depends on the developer's task. The developer's task has no ID until it is created, so "depends on the first" or "depending on the highlights task" counts as naming it.
FAIL if they are two separate items, if either performer is wrong, or if the agent's task has no dependency on the developer's.
