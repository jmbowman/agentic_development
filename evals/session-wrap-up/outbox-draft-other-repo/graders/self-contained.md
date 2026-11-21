---
type: llm
---

Judge only the outbox draft's description (the text between its description markers, or its body). Headings and wording don't matter.

PASS if it has all four parts: a first line that names quote_field() and the newline problem; what to change and why; sources to read (at least one concrete thing, such as report-builder's report.py by URL or csv-utils' own quote_field()); and what to report back.
FAIL if any of the four is missing.
