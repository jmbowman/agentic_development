---
type: llm
focus: trace
---

Judge from the tool calls you can see and, for searches a subagent ran, from the queries the coverage ledger records.

PASS if all hold:
- in round 1, the assistant looked up topic names with GitHub's topic search (`search/topics`) for each of the need's key terms, searched each topic found that fits the need with a `topic:` search, and in later rounds looked up each new serious candidate's name there too (when a later round found no new serious candidate, no lookup is needed);
- the coverage ledger counts each topic lookup and each `topic:` search as a query.
FAIL if topic names were only guessed or taken from candidates' own tags, or either item is missing.
