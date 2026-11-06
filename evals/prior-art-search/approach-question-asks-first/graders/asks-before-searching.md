---
type: llm
focus: trace
---

PASS if the assistant asks the developer whether they want to use the prior-art search skill for this question (a search of papers and software with a ledger and a saved note), and starts none of it before an answer: no literature or software route is searched, no subagent is dispatched for searching, and no note is written. This run has no developer to answer, so it ends after the question, and the question is recorded as unanswered.
FAIL if the assistant starts the search, or runs the full method, without asking.
