---
type: llm
focus: trace
---

PASS if the assistant states it is running a quick pass, with a reason about the choice being cheap to reverse, records that its question about options the developer already knows or has dismissed went unanswered, and records the underlying need behind the request before searching.
FAIL if it runs the full method without first finding that a quick pass couldn't conclude adopt or build on, or skips the effort statement.
