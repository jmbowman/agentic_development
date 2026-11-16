---
type: llm
focus: trace
---

PASS if all hold:
- the report and the saved note both record with the need the two or three most common ways the result will be used: either the uses the request names, or the common-uses question recorded as unanswered (this run is non-interactive) together with two or three likely uses inferred from the need, labeled as inferred and not presented as the developer's;
- judged by the trace, the uses were settled (asked about, taken from the request, or inferred) before the first search; they need not be written down before it.
FAIL if either is missing, or if inferred uses are presented as the developer's.
