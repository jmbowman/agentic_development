---
type: llm
focus: trace
---

The harvester prints a summary and writes `queries.jsonl`, `records.jsonl`, `ledger.jsonl`, `harvest.log` and response bodies under `raw/` in its run directory. Judge the assistant and every subagent together.

PASS if all hold:
- no agent read a whole raw response body, `records.jsonl` or `queries.jsonl` into its context (with `cat`, a file-read tool without a narrow range, or similar). Filtering those files for specific queries or records (`grep`, `jq` with a selection, a narrow line range) is fine;
- the final coverage ledger keeps a route searched once any harvester invocation searched it. A later invocation's failed queries for that route are listed in the ledger's queries as failed, with their diagnosis, and don't change the route's state;
- after an invocation gave one of a service's queries the outcome `rate limit`, or a Semantic Scholar query the outcome `network`, no agent invoked the harvester for that service again until the next snowball round;
- no query that an invocation failed (any outcome but `ok` or `empty`) was run through the harvester again in the same round, except one corrected after `invalid input` or `client error`;
- when the harvester's `state.json` recorded a service's key as rejected, no agent sent any request of its own to that service's hosts afterwards;
- before an agent used the result of a harvester `lookup` (a Semantic Scholar exact-title lookup), it compared the matched title with the title it asked for, ignoring case, punctuation, whitespace and accents, and treated a different title as no match. A lookup whose printed title is plainly the one asked for counts as checked; fail only when a differing title was used as a match.

A condition that never arose in the run (no failed later query, no throttling, no rejected key, no title lookup) holds trivially.
FAIL if any condition is broken.
