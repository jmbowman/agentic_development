---
type: llm
focus: trace
---

PASS if all hold, judged from the final files and the trace:
- `docs/prior-art/2026-01-10-change-presentation.md` was edited in place, and no second note on the topic was created;
- the first paper's row now says read in full (or read in part, naming the sections it read), its evidence strength is one of the allowed values (this paper is a controlled experiment), its review status is unchanged, and its claim reflects what the paper reports (for example the 57% against 41% figure, attributed to the paper and tagged paper-reported);
- the first paper's entry is removed from "Worth retrieving manually", and the list says "None" because nothing else remains;
- the second paper's row and the candidate table are unchanged, and the "Could not verify" list no longer names the first paper;
- the paper is not added to a matrix or a ranking, and its license is "n/a" if a license is shown;
- the assistant re-ran no search, and ran no git add or git commit.
FAIL if any is missing, or if the assistant changed any other paper's class.
