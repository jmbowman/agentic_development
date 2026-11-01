---
type: llm
---

PASS if the report asks about `docs/STATUS.md`, which the instruction files name but which doesn't exist, and proposes no item that creates it.
FAIL if it proposes creating the file, or doesn't mention it.
