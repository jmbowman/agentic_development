---
type: llm
focus: trace
---

Judge from the agent's tool calls, not its final reply. Listing a folder to get oriented is fine, and the order of steps doesn't matter.

PASS if the agent searched the backlog's task files with search terms for the session's loose ends (`backlog search` with a query, `grep` with a pattern, or the Grep tool) at some point.
FAIL if it found the matching tasks only by listing or reading every task file.
