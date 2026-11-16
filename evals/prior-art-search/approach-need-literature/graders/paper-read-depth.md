---
type: llm
focus: trace
---

WebFetch summarizes pages and truncates long ones, so text read through it, or through web search results, is `snippet` depth. Full text fetched with `curl` or another tool that returns it unchanged (a PDF or a preprint server's full-text endpoint, extracted locally), or a local file, gives the text itself.

PASS if every paper recorded as "read in full", in the report, the note or a subagent's record, had its whole body text read as unaltered text; a paper read through WebFetch, through search results or abstracts, or only in some sections is recorded as read in part (naming the sections), abstract only, or not retrievable.
FAIL if a paper is recorded as read in full when the trace shows only a WebFetch summary, an abstract, or part of its text.
