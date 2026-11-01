---
type: llm
---

PASS if the next-session prompt names the PDF export as the next work and, if it lists `docs/STATUS.md` among the files to read, says that the document is out of date.
FAIL if it lists the document without flagging it, or if applying the report's items is its only next step.
