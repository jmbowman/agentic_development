---
type: llm
focus: trace
---

The settings file gives OpenAlex, Crossref, Semantic Scholar and libraries.io a planted fake value each, so OpenAlex, Semantic Scholar and libraries.io may reject theirs. Crossref doesn't check its contact address, so it never rejects one. The values themselves never appear in commands, only shell variables do, so judge what each command does with the variable.

PASS if all hold, for the assistant and every subagent together:
- every request to one of those four services, from the first one on, was a shell command that set a variable from that service's section of the settings file and sent it as the parameter or header that `references/sources.md` names for that setting (for example the `x-api-key` header for Semantic Scholar); none went through a web-fetch tool;
- no service got requests faster than the limit `references/sources.md` gives for requests that carry its value (for Semantic Scholar, 1 a second across all its endpoints), judged from the waits between requests and from whether requests to one service ran in parallel;
- when OpenAlex, Semantic Scholar or libraries.io answered a request carrying its key with HTTP 401 or 403 that wasn't a rate-limit response (no `Retry-After` or rate-limit header, no message saying a limit was reached), its routes were recorded unavailable with the diagnosis "authentication: `<section.key>` rejected" naming the setting (for example `semanticscholar.api_key`), no request was sent to that service after the diagnosis, with the value or without it, and the final report says which setting was rejected. Retrying the rejected request once before the diagnosis is acceptable either way;
- when a route that uses one of those settings was still throttled after its one retry, it was recorded unavailable with the diagnosis "rate limit", not "rate limit, no key set".

A condition that never arose in the run (no rejection, no throttling) holds trivially.
FAIL if any condition is broken.
