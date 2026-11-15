---
type: llm
focus: trace
---

The skill ships a harvester, `scripts/harvest.py`, run with `uv run --script`. Judge the assistant and every subagent together.

PASS if all hold:
- every keyword search sent to arXiv (`export.arxiv.org`), OpenAlex (`api.openalex.org`) or Semantic Scholar (`api.semanticscholar.org`), and every OpenAlex lookup of the works citing or referenced by a paper, went through a harvester invocation, unless the fallback below applied;
- the fallback applied only when `uv` was missing, `uv` failed before the harvester started (an exit status other than 0, 3 or 4), or the harvester exited with status 4 for anything but a usage error (`harvest.py: usage error:`), which the agent fixed and reran instead. Under the fallback the agent sent those requests itself, and the coverage ledger's reason for each route whose requests it sent itself says they were sent without the harvester;
- the agent didn't resend itself (with `curl`, a web-fetch tool or any other client) any query that a harvester invocation had given an outcome, whatever the outcome or exit status;
- every invocation in the run passed the same `--run-dir`, which is in the session's scratch directory or in a directory the host repo's git ignores (the workspace has an ignored `tmp/`), and the prompt of every subagent that searched the literature routes gives that path (subagents that searched only software routes needn't have it). This condition doesn't apply when the fallback above legitimately applied and the harvester never ran.

Other requests to these services, such as exact-title lookups or open-access lookups, may be sent outside the harvester.
FAIL if any condition is broken.
