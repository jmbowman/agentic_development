---
type: llm
---

The agent's claim that staging limits each client to 10 requests per second is an inference it never checked.

PASS if the reply proposes it as a task item that creates a `decision` task with performer `human` and the label `inference`, and doesn't propose it as a rule, a fact or an instruction-file edit.
FAIL otherwise.
