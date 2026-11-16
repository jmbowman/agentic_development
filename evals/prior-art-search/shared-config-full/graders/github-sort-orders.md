---
type: llm
focus: trace
---

Judge from the tool calls you can see and, for searches a subagent ran, from the queries the coverage ledger records.

PASS if all hold:
- each GitHub repository search of round 1, `topic:` searches included, ran twice: once sorted by stars, and once restricted with a `pushed:>` date about 12 months before the run and sorted by update time; so did each `topic:` search for a topic variant first found in a later round;
- the other GitHub repository searches of later rounds were sorted by stars.
FAIL if a round-1 search ran in only one order, the recent run lacks a `pushed:>` restriction, or a later search used another order.
