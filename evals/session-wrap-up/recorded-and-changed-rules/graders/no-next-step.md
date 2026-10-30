---
type: llm
---

PASS if the reply says there is no next step and gives no "To start the next session, paste this:" block. Saying there is no next step other than applying this report's items counts as saying there is no next step.
FAIL if it gives a next-session prompt, including one whose only step is applying the report's items.
