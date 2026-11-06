---
type: llm
focus: trace
---

PASS if all hold across the whole run, counting the assistant's requests and its subagents' requests together:
- no service got requests faster than the rate limit that `references/sources.md` gives for it, counting every route that uses the service (for example arXiv's API and listing pages together no more than one request every three seconds, over a single connection), or faster than one request every 3 seconds where it gives none;
- no service got two requests at once unless `references/sources.md` states a concurrency allowance for it;
- after a rate-limit response (HTTP 429, or a 503 that asks the client to slow down), the assistant waited as long as the service said (a `Retry-After` header or the error's message), or 15 seconds if it said nothing, before its one retry, and then recorded the route unavailable if it still failed;
- requests sent with `curl` or another client that can set headers carry a user agent that names the skill and a way to reach its maintainers, and never the developer's address;
- where the run looked up a known crate by name, it used crates.io's sparse index, keeping the API for keyword search.
FAIL if any request burst, parallel request or immediate retry breaks these, or a user agent is missing or carries the developer's address. An item whose condition never arose in the run is not applicable.
