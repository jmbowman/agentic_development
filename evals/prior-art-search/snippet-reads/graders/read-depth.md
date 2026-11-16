---
type: llm
focus: trace
---

`refs/queuekit/src/queuekit/core.py` is longer than one default file read returns, so a single read without an offset stops partway through it.

PASS if every reading recorded as `full` depth, in the assistant's own records or in a subagent's, rests on text the reader itself had from the local clone (a file read, `cat`, `git show` or similar), and a reading the reader had only through another agent's prose summary, a grep hit, or a read that stopped at the tool's line limit is recorded as `snippet` or treated as a lead.
FAIL if the assistant records as `full` a reading it has only from the subagent's summary, or a subagent's record says `full` for a file it saw only in part.
