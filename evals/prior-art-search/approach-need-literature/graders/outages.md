---
type: llm
focus: trace
---

PASS if all hold; an item whose condition never arose in this run is not applicable (live services rarely throttle on demand, so these two specs have only nominal coverage in an online run):
- if a literature route was unavailable after its retries (one for a request the assistant sent itself; the harvester's own for its requests) and the route its substitute column names was searched, the verdict is not inconclusive or blocked from build for that reason alone, and the route is listed under "Could not verify";
- if a route was still throttled after its retries and no key was set, the ledger gives "rate limit, no key set" as its diagnosis;
- if OpenAlex answered a search with HTTP 503 whose message names the key, the assistant treated it as a rate limit (one retry, then "rate limit, no key set" with no key set), not as a rejected key, and didn't stop sending OpenAlex lookups because of it.
FAIL if an applicable item is missing.
