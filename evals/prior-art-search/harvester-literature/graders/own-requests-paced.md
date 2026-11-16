---
type: llm
focus: trace
---

The skill's harvester (`scripts/harvest.py`) paces its own requests, but not the requests an agent sends to the same services itself (an open-access or arXiv ID lookup with `curl` or a web fetch, or a Semantic Scholar request when the harvester couldn't run).

PASS if every request an agent sent itself to arXiv (`export.arxiv.org`, `arxiv.org`), OpenAlex (`api.openalex.org`) or Semantic Scholar (`api.semanticscholar.org`) came at least that service's interval after the same agent's last harvester command for that service finished: 3 seconds for arXiv, 8 seconds for Semantic Scholar (no key is set here) and 1 second for OpenAlex. Judge from the order of the tool calls and any waits (`sleep`) between them. It also passes if no agent sent such a request itself.
FAIL if a request of an agent's own went to one of those services sooner than that after a harvester command for it.
