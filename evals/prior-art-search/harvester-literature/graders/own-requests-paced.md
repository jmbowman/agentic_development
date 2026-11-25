---
type: llm
focus: trace
---

The skill's harvester (`scripts/harvest.py`) paces its own requests, but not the requests an agent sends to the same services itself (an arXiv paper's full text fetched from `arxiv.org` with `curl` or a web fetch, or any request to these services when the harvester couldn't run).

PASS if every request an agent sent itself to arXiv (`export.arxiv.org`, `arxiv.org`), OpenAlex (`api.openalex.org`) or Semantic Scholar (`api.semanticscholar.org`) came at least that service's interval after the same agent's last harvester command for that service finished: 3 seconds for arXiv's API (`export.arxiv.org`) and 15 seconds for an `arxiv.org` page, 8 seconds for Semantic Scholar (no key is set here) and 1 second for OpenAlex. Judge from the order of the tool calls and any waits (`sleep`) between them. It also passes if no agent sent such a request itself.
FAIL if a request of an agent's own went to one of those services sooner than that after a harvester command for it.
