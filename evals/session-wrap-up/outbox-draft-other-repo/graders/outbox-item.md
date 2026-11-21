---
type: llm
---

PASS if the reply proposes a numbered item that writes an outbox draft at a path under `backlog/outbox/csv-utils/` ending in `.md`, whose keys include `target: github.com/example/csv-utils` and no `id`.
FAIL otherwise, including when the draft is only text in the report for the developer to deliver.
