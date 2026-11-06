---
type: llm
focus: trace
---

PASS if all hold:
- beside the software routes, the assistant selected literature routes (searches of papers, for example arXiv, OpenAlex, OpenAIRE or Semantic Scholar), searched them in this full-method run, and each ended in a ledger state (a literature route may be unavailable after its one retry);
- when a query used an ambiguous word such as "diff", "agent" or "comprehension", the same query also carried a software-specific term, beside the ambiguous word;
- in each snowball round that followed papers, the assistant did all of these in this order: backward citations, forward citations, related works, the vocabulary the papers use, then arXiv preprints from the last 12 months.
FAIL if literature routes were not selected or not searched, if the order was not followed, or if an ambiguous term was searched alone.
