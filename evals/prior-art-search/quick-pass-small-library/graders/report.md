---
type: llm
---

PASS if the reply contains all of:
- exactly one verdict, adopt X or build on X;
- each candidate it presents classified, with a one-line reason and a license naming the license file or manifest field it was read from;
- a statement of what the developer already knew about or had dismissed, or that the question went unanswered;
- a coverage ledger listing each route with a state (searched with at least 2 differently worded queries, where a GitHub search run once sorted by stars and once restricted to recently pushed repos counts as one wording, except the two local routes, the stack itself and earlier notes and decisions, which are searched with what was checked; excluded with a concrete reason, "quick pass", or "blocks scripted clients"; or unavailable with a diagnosis), with at least two routes searched and at least one snowball round;
- if it found candidates it doesn't present, they are listed as seen, not classified.
FAIL if any of these is missing, if a license is attributed only to a badge or to forge API metadata, or if stars, downloads or popularity are given as evidence that a candidate meets a requirement.
