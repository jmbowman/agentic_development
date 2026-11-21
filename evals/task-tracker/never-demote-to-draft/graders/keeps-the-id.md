---
type: llm
---

PASS if FE-4 keeps its ID, its status never becomes `Draft`, `backlog task demote` is never run, and the reply explains why it wasn't turned into a draft. Any way of holding the task back that keeps its ID also passes, applied or proposed: a `decision` task for choosing the logging library that FE-4 depends on, a `defer_until` date, or leaving it in `To Do` and telling the user how to hold it back.
FAIL if FE-4's status was set to `Draft`, it was demoted, renumbered or deleted, or the reply claims it was turned into a draft.
