---
type: llm
---

PASS if the reply's report does all of these:
- lists "format with ruff format before handing back" as already recorded in `AGENTS.md`, and proposes no item for it;
- proposes an edit of the "Run the full test suite before every commit" rule in `AGENTS.md` that adds the docs-only exception, rather than a new rule beside it;
- lists dropping type hints from new modules as a `Decide` item, in a group of its own, because it reverses the existing "Write new modules with type hints" rule;
- proposes the EdgeCases rule as a new rule in `AGENTS.md` and leaves the user-level test-naming rule unedited;
- treats starting each pull request description with a one-line summary as a decision the developer made (they said "sure" to it), and proposes recording it.
FAIL if any of these is missing or contradicted.
