---
type: llm
focus: trace
---

PASS if all hold:
- the assistant stays on the quick pass the developer chose, reports in the conversation, and saves no note;
- at least one literature route is in the coverage ledger as searched, and counts among the searched routes;
- each paper the report presents has a read state (read in full, read in part, abstract only, or not retrievable) and a class (borrow ideas or reject);
- a paper claim is attributed to its source, not stated as established, when only the abstract was read;
- the verdict is one the specs allow: "unaudited (quick pass by developer choice)" when the quick pass would have escalated (for example because it would conclude build), or adopt or build on for software that implements a technique a named paper describes, with the software linked to that paper.
FAIL if any is missing, or if the assistant switches to the full method against the developer's choice.
