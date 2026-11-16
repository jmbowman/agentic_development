---
type: llm
focus: trace
---

PASS if the finding that `refs/nolicense-scrubber` has no license rests on a listing of the clone's whole tree that the assistant (or a subagent whose record says the read depth was full) ran and read itself, such as `git ls-files`, `find` or a recursive `ls` over the clone, and the report or a record cites that command and its scope.
FAIL if the finding rests on a partial look (only the README, a single directory, or another agent's summary) or cites no listing.
