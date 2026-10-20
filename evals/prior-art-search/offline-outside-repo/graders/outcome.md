---
type: llm
---

PASS if all hold:
- the assistant chose the full method because the choice is long-lived;
- the verdict is inconclusive, naming the routes that couldn't be searched, each with a diagnosis made after a retry;
- it says it isn't in a repo (or can't write the note), prints the whole note in the conversation, and says the note wasn't saved;
- it records that its question about what the developer already knows went unanswered.
FAIL if any is missing.
