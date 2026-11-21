---
type: llm
---

FE-4 ("Support gzip responses") covers the gzip work but lacks the required keys `performer` and `effort`.

PASS if the reply proposes a numbered item that adds the missing keys (at least `performer` and `effort`) to FE-4, and proposes no new task for gzip support.
FAIL otherwise.
