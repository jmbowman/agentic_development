---
type: llm
---

FE-3 ("Log each request at debug level") is `Done` and archived (in `backlog/archive/tasks/`), so it doesn't cover the new work of scrubbing URLs in the debug log.

PASS if the reply proposes a numbered item that creates a new task for scrubbing the URLs (query strings) out of the debug log, and that task names FE-3 among its references.
FAIL if it proposes only a comment on FE-3, reopens or restores FE-3, or doesn't mention FE-3 in the new task.
