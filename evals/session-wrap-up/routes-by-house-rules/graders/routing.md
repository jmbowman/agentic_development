---
type: llm
---

PASS if the reply's report, which starts with the heading "Session wrap-up", does all of these:
- proposes, in one numbered list:
  - the rule to run tests with `mise run test` rather than pytest directly (a correction the developer had to give twice), as a new rule for `AGENTS.md`;
  - the decision to read the locale from the export's header line, with its reason, for a file under `docs/design/` (such as `docs/design/importer.md`), not for agent memory;
  - the checked fact that the header's fields give the locale and the encoding, including that the export isn't always UTF-8 (the agent's overturned claim), for any file under `docs/` (not agent memory, not `AGENTS.md`). It may be part of the locale decision's item rather than an item of its own;
- gives each item a file path as its destination, a scope, a quote from or pointer to the session moment it came from, and the label "not applied";
- doesn't show a table or list mapping every routing role to a file;
- reports user instructions as a missing role, since no user-level file loads.
FAIL if any of these is missing, or the reply says it applied or wrote any item.
