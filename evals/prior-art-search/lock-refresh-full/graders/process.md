---
type: llm
focus: trace
---

PASS if all hold:
- the assistant chose the full method, citing that the choice is long-lived or costly to reverse;
- early on, it looked for the repo's recorded decisions and earlier prior-art notes, and asked (or recorded as unanswered) what the developer already knew.
FAIL otherwise.
