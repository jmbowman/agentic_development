---
type: llm
focus: trace
---

Judge from the agent's tool calls and their results, not from its final reply. The backlog already has FE-1, "Retry transient server errors in the HTTP client", which covers retrying 503 responses. Listing the backlog's folders to get oriented is fine, and the order of the steps doesn't matter.

PASS if, at some point, the agent searched the task files with search terms for the work (`backlog search` with a query, `grep` with a pattern, or the Grep tool), and it then either added the new observation to FE-1 (for example a note or comment saying a 503 under load crashed `fetch()`) or told the user that FE-1 already tracks it.
FAIL if it never ran such a search, if it created a new task or draft for the work, or if it didn't relate the work to FE-1.
