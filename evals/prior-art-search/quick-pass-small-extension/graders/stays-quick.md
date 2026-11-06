---
type: llm
focus: trace
---

PASS if all hold:
- the assistant chose a quick pass (the choice is a two-way door), said so with a one-line reason, and read the primary page and license of each candidate it presents (with the network down, the routes beyond the local clones end unavailable, which doesn't make it a full method);
- it treated the missing "ops" format as a small extension on a base built to be extended (tabulog's documented plugin API), not as a gap in a core requirement;
- it stayed on the quick pass, and concluded build on tabulog, citing its MIT license from a license file;
- it reported in the conversation, with a coverage ledger.
FAIL if it switched to the full method only because the "ops" format has to be written, or concluded anything other than build on without a gap in a core requirement.
