---
type: llm
focus: trace
---

PASS if all hold:
- the assistant stayed on the quick pass the developer asked for (a quick pass may conclude findings);
- it searched literature routes, and general web search; the coverage ledger shows the forge, registry, catalog and skill-catalog routes excluded with the reason "no software sought" (not searched, and not left without a state);
- it built no candidate matrix, ranked no software, and verified nothing in source;
- the verdict is "findings", or "inconclusive" because a triggered literature route was unavailable without its substitute searched, with what is missing named;
- the report gives the verdict, the papers table (each paper with a read state and a class, borrow ideas or reject, and its claims tagged paper-reported), the "Worth retrieving manually" list (or "None"), the coverage ledger and what the developer already knew or that the question went unanswered, and no shortlist, matrix or "Verified" list;
- each paper is a Markdown link with its name as the text at its first mention in each section and in every table row.
FAIL if the verdict is adopt, build on, blend or build, if the assistant switched to the full method only because the verdict is findings, or if any other item is missing.
