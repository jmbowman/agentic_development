---
type: llm
focus: trace
---

Judge from the agent's tool calls and their results, not from its final reply.

PASS if the agent read `CLAUDE_CODE_SESSION_ID` and, when it held a session ID, added to the new task's frontmatter a `sessions` entry with that `id`, `role: created`, an `agent` and a `date`; or, when the variable was empty or unset, added no session record.
FAIL if the variable held an ID and no matching record was added, or if a record was added with an ID other than the one the variable held.
