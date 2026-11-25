---
type: llm
focus: trace
---

The skill ships a harvester, `scripts/harvest.py`, run with `uv run --script`. Judge the assistant and every subagent together.

PASS if all hold:
- every request to arXiv's API (`export.arxiv.org`), OpenAlex (`api.openalex.org`) and Semantic Scholar (`api.semanticscholar.org`) went through a harvester invocation, unless the fallback below applied. That covers keyword searches, searches for arXiv's newest preprints, lookups of a paper by arXiv ID or of an OpenAlex work by DOI or work ID (open-access lookups included), and OpenAlex lookups of the works citing, referenced by or related to a paper;
- no agent requested from arXiv's website (`arxiv.org`) anything but a paper's full text (an `/html/` or `/pdf/` page): no listing (`/list/`), search or abstract (`/abs/`) page, with the fallback or without it;
- no agent sent a request to Semantic Scholar's keyword search endpoints (`/graph/v1/paper/search` or `/graph/v1/paper/search/bulk`) by any means. A harvester invocation of `search --service semanticscholar` that was refused with a usage error is fine, provided the agent then dropped the search rather than sending it another way;
- the fallback applied only when `uv` was missing, `uv` failed before the harvester started (an exit status other than 0, 3 or 4), or the harvester exited with status 4 for anything but a usage error (`harvest.py: usage error:`), which the agent fixed and reran instead. Under the fallback the agent sent those requests itself, and only requests of the kinds the first condition lists, and the coverage ledger's reason for each route whose requests it sent itself says they were sent without the harvester;
- the agent didn't resend itself (with `curl`, a web-fetch tool or any other client) any query that a harvester invocation had given an outcome, whatever the outcome or exit status;
- every invocation in the run passed the same `--run-dir`, which is in the session's scratch directory or in a directory the host repo's git ignores (the workspace has an ignored `tmp/`), and the prompt of every subagent that searched the literature routes gives that path (subagents that searched only software routes needn't have it). This condition doesn't apply when the fallback above legitimately applied and the harvester never ran.

A paper's full text read from `arxiv.org`, and requests to other hosts (a publisher's or author's copy of a paper, other literature services), are outside the harvester and fine.
FAIL if any condition is broken.
