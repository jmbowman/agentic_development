# Harvester

`scripts/harvest.py` sends a batch of literature queries for you and writes what came back to disk. You choose the queries, read the results and classify the papers; the harvester paces, sends, retries, logs and summarizes. It sends every request to the APIs of arXiv, OpenAlex and Semantic Scholar:

- keyword searches on arXiv and OpenAlex (`search`), and on arXiv the newest preprints first (`--sort submitted`);
- a paper by its ID (`get`): an arXiv ID on arXiv, a DOI or work ID on OpenAlex, which also tells you whether the paper is open access and where;
- OpenAlex's works citing a paper (`citations`), the works it references (`references`) and its related works (`related`);
- every Semantic Scholar request: recommendations from seed papers (`recommend`) and exact-title lookups (`lookup`). Semantic Scholar refuses many requests at busy times, so the harvester retries these up to six times on a growing backoff, within about a minute per request.

Send these three APIs (`export.arxiv.org`, `api.openalex.org`, `api.semanticscholar.org`) nothing yourself, unless the harvester can't run (see Exit status). The one thing you still fetch yourself is an arXiv paper's full text, from its `arxiv.org/html/<id>` or `arxiv.org/pdf/<id>` page, under the rules in [sources](sources.md#rate-limits). Don't request arXiv's listing, search or abstract pages: a newest-first `search` and `get` return the same data. Don't send keyword searches to Semantic Scholar at all.

## Running it

It needs [`uv`](https://docs.astral.sh/uv/), which installs its pinned dependencies on first use:

```sh
uv run --script <skill>/scripts/harvest.py <action> --service <service> --round <n> \
    --run-dir <run directory> [--sort submitted] [--max-results <n>] [--show <n>] <query or paper ID>...
```

- `<action>`: `search` or `get` (with `--service arxiv` or `openalex`), `citations`, `references` or `related` (with `--service openalex`), or `recommend` or `lookup` (with `--service semanticscholar`).
- `--service`: `arxiv`, `openalex` or `semanticscholar`, matching the action.
- `--round`: the snowball round you are in, from 1, as [Rounds and reruns](#rounds-and-reruns) counts it.
- `--run-dir`: the run directory. Use one for the whole skill run, in your session's scratch directory or a directory the host repo's git ignores, and give the same path to every invocation and to every subagent that searches the literature. Invocations can share it at once.
- `--sort`: for an arXiv `search` only: `relevance` (the default) or `submitted`, which returns the newest preprints first. For a category's newest preprints, search for the category, such as `--sort submitted "cat:cs.SE"`, or add it to a query (`cat:cs.SE AND all:"test selection"`). It returns only the newest results up to `--max-results`, and a record carries the year, not the date: a new-style arXiv ID begins with the year and month of submission (`2611.…` is November 2026), which tells you whether a preprint is within the last 12 months.
- `--max-results`: results to fetch per query. For `search`, 1 to 100 (50 when omitted); for `citations`, `references` and `recommend`, 1 to 500 (100 when omitted); for `related`, 1 to 100 (20 when omitted); a `get` returns its one paper, and a `lookup` its one best match. A page of up to 100 is one request, so deep pages cost nothing extra in requests. A `get` is one request per ID (3 seconds apart on arXiv), and a `related` query is one request for the paper and one for each related work.
- `--show`: results to print per query (10 when omitted). The rest stay in `records.jsonl`.
- Quote each query or title as one argument, and put `--` before the queries when one starts with `-`. Options can't be abbreviated, and only `--help` prints help. An OpenAlex search with more than 5 of `AND`, `OR` and `NOT` in capitals is refused as invalid input.
- A `citations`, `references` or `related` paper ID, and a `get` ID on OpenAlex, is a DOI (bare, `doi:` or a `doi.org` URL) or an OpenAlex work ID (`W…` or an `openalex.org` URL). OpenAlex doesn't take an arXiv ID: give an arXiv preprint as its arXiv DOI, `10.48550/arXiv.<id>` without a version suffix (`10.48550/arXiv.1706.03762`).
- A `get` ID on arXiv is an arXiv ID, new-style (`2401.12345`) or old-style (`hep-th/9901001`), bare or with `arXiv:` directly before it; a version suffix (`v2`) fetches that version, and an `arxiv.org` URL is refused as invalid input.
- A `recommend` seed is a DOI in the same forms (a DOI URL with a query string or fragment is refused), a new-style arXiv ID (`2401.12345`, bare or with `arXiv:`; a version suffix is dropped) or a Semantic Scholar paper ID (40 hexadecimal characters); old-style arXiv IDs are refused as invalid input.
- A `lookup` result is the closest title Semantic Scholar has, which can be a different paper. Its record carries `match_score`; before you use it, check that its title is the one you asked for, ignoring case, punctuation, whitespace and accents, and treat anything else as no match.

It reads the access settings file itself, under the same rules as you, so never pass a key on its command line.

A harvest record stands in for the paper's abstract page: judge whether a paper is serious from the record's `abstract` (`jq` it out of `records.jsonl`), and take the link you cite from its `url`. Don't open the `arxiv.org/abs/` page for either.

## In a sandboxed shell

Your shell may only be able to write inside the host repo, as under Claude Code's sandbox. Then your scratch directory and `~/.cache` aren't writable:

- Put the run directory under `prior-art-search/` in a directory at the top of the host repo that git ignores, such as `tmp/prior-art-search/run-1` (check with `git check-ignore -q tmp/`). If there is none, ask the developer whether to have one ignored, and add it to `.gitignore` only on a yes. In a non-interactive run, send the requests yourself and give that reason in the ledger.
- If `uv` fails with `Failed to initialize cache` (or another error writing its cache), run the harvester again with `UV_CACHE_DIR=<ignored directory>/prior-art-search/uv-cache` before the command. Fall back to sending the requests yourself only if that fails too.
- The harvester keeps its pacing in the run directory when it can't write `~/.cache`, and its first summary line says so. That's expected.

## What it prints

One line per query: its ID, service, query, outcome, result count, and a reason (a refusal's, or `daily budget`) or truncation when there is one. A newest-first search's line also says `sort: submitted`, and a `related` query whose paper lists more related works than were fetched says `truncated: <n> listed`. Under each query that ran, one line per printed result: rank, year, citation count, the service's ID and the title (`-` for a missing value; a result printed earlier in the invocation shows only its ID). Under each OpenAlex `get` result, one more line gives `open access: <status>  <link>`, or `not open access`; the link is where to read a legal copy. A `related` result's rank is its place in OpenAlex's list, so ranks can skip. Then how many more results are in `records.jsonl`, the invocation's coverage-ledger record as one JSON line (none for a `get`), and the paths of the files below.

Work from this summary. Don't read raw bodies, `records.jsonl` or `queries.jsonl` whole; filter them for the queries or records you need, for example `jq -c 'select(.query_id == "<id>")' records.jsonl`, or `jq -r 'select(.service_id == "W123") | .abstract' records.jsonl` for one result's abstract.

Outcomes: `ok`, `empty` (for a `lookup`, no title matched; for `related`, the paper lists no related work, or none of those listed exists any more), `not found` (a paper ID or seed that doesn't exist), `rate limit`, `authentication`, `client error` (the service rejected the query), `network`, `not sent: limiter wait` (your machine's shared pacing would have waited over 60 seconds), `refused` (with its reason; `daily budget` means OpenAlex's daily budget ran out earlier in this run), `skipped: service throttled`, `internal error` and `invalid input`. A `related` query that fails part-way records none of its results.

OpenAlex charges its daily budget for searches, citations and references, not for the single-work requests of `get` and `related`. So after an OpenAlex `search`, `citations` or `references` query ends `rate limit` (a spent budget or a paused search), you may still run `get` and `related` on OpenAlex in the same round. If a `get` or `related` query itself ends `rate limit`, don't run either again until the next round.

## Rounds and reruns

A failed query, and a service stopped by `rate limit` (or Semantic Scholar by `network`), wait for your next round. Each agent that runs the harvester counts its own rounds, and a round is later only when both of these hold:

- you have finished your current round: every one of its queries, on all of your routes, has been sent or has an outcome from the harvester, a failure or a skip included;
- in the new round, before the harvester command for the stopped service or the failed query, or among that command's own queries, you run at least one seeded query, on any route, through the harvester or not. A seeded query is built from a new serious candidate in any way step 6 or the literature snowball uses one: its name, its ID, its references, citing or related works, its vocabulary, its topics, pages that list alternatives to it. You found that candidate in your previous round, on any route. A subagent may also use the seeds in its prompt, but only for its first round.

A failed query run again is never the seeded query, reworded or not. A higher `--round` number alone is not a later round: pass the number of the round you are in, and give a corrected query you rerun at once the same number as the command that failed it. The search has one numbering. The main agent counts from 1 and, when it dispatches a subagent for a later round, puts that round's number and its seeds in the prompt; a subagent starts from the number in its prompt (1 if there is none) and counts on from it for further rounds of its own.

The main agent's next round begins when every subagent of its current round has returned, its own queries of the round have run, and the round found a new serious candidate. Candidates its subagents returned count as its own. The seeded query may be one a subagent runs on being dispatched for the new round, so the main agent may then give that subagent a service that was stopped: it names the service as stopped in the prompt, and the subagent's first harvester command for it follows a seeded query or includes one. For a subagent dispatched with a round number after 1, that round is its first and is already later than the rounds before it. With no new serious candidate to seed from, there is no later round: leave the queries failed, and the route keeps the state the ledger gives it.

A stop outranks the immediate rerun of a corrected query: when one command ends with a `client error` query and a `rate limit` query for the same service, the corrected query waits for the next round too.

The services count requests by your machine's address, so a stop outlasts the subagent that met it. A subagent that returns with a service still stopped names it in what it returns, and the main agent doesn't run the harvester for that service, or give the service to another subagent, until its own next round (OpenAlex `get` and `related` excepted, as above).

## Files in the run directory

- `queries.jsonl`: one line per query, with its outcome and every attempt.
- `records.jsonl`: one harvest record per result, with the fields `query_id`, `rank`, `title`, `authors`, `year`, `venue`, `doi`, `arxiv_id`, `service_id` (the ID the summary prints), `abstract`, `citations`, `url` and `pdf_url`, plus `match_score` for a `lookup`, and `is_oa`, `oa_status`, `oa_url` and `oa_license` (each null when OpenAlex gives none) for an OpenAlex `get` or `related` result. A harvest record isn't a paper record: write those only after reading.
- `ledger.jsonl`: one coverage-ledger record per route per invocation. A `get` invocation adds none: fetching a paper you already know searches no route.
- `raw/`: each response body.
- `harvest.log`: the connectors' log lines.
- `state.json`: services whose API key was rejected, and whether OpenAlex's daily budget ran out, for searches or for every request.

## Exit status

| Status | Meaning | What to do |
|---|---|---|
| `0` | Every query ran. | Read the summary. |
| `3` | At least one query didn't run. | Read the outcomes. Don't resend those queries yourself. Correct and rerun an `invalid input` or `client error` query at once if you can, unless the service is stopped; rerun any other failed query only in a later round, as [Rounds and reruns](#rounds-and-reruns) counts it. After a `rate limit`, or a Semantic Scholar query ending `network`, don't run the harvester for that service again until the next round (but see OpenAlex's `get` and `related` above); the route's substitute covers it meanwhile. |
| `4` | Nothing was sent. The message starts `harvest.py: usage error:`, `harvest.py: setup error:` or `harvest.py: internal error`. | After a usage error, fix the command and rerun. After any other, report the problem it names, and send these requests yourself under the rules in [SKILL.md](../SKILL.md). |

Any other status means `uv` failed before the harvester started; send the requests yourself then too. Whenever you send them yourself, say in each affected route's ledger `reason` that they were sent without the harvester.

## Sending the requests yourself

Only when the harvester can't run, as above. Send only these requests, under the rules for your own requests in [SKILL.md](../SKILL.md) and [sources](sources.md#rate-limits) (one retry, the service's interval, the skill's user agent, a key sent as [sources](sources.md#access-settings) says):

| Action | Request |
|---|---|
| arXiv `search` | `https://export.arxiv.org/api/query?search_query=<query>&max_results=<n>`; add `&sortBy=submittedDate&sortOrder=descending` for the newest first |
| arXiv `get` | `https://export.arxiv.org/api/query?id_list=<id>&max_results=1` |
| OpenAlex `search` | `https://api.openalex.org/works?search=<query>&per_page=<n>` |
| OpenAlex `get` | `https://api.openalex.org/works/doi:<doi>?select=id,title,doi,publication_date,open_access,best_oa_location` (or `works/<W…>`) |
| OpenAlex `citations`, `references` | `https://api.openalex.org/works?filter=cites:<W…>&per_page=<n>` for citing works, and `filter=cited_by:<W…>` for referenced ones; take the work ID from a `get` |
| OpenAlex `related` | the `get` request with `select=id,related_works`, then a `get` for each work listed |
| Semantic Scholar `recommend` | `https://api.semanticscholar.org/recommendations/v1/papers/forpaper/<DOI:… or arXiv:…>?from=all-cs&limit=<n>&fields=title,abstract,externalIds,year,citationCount` |
| Semantic Scholar `lookup` | `https://api.semanticscholar.org/graph/v1/paper/search/match?query=<title>&fields=title,abstract,externalIds,year,citationCount` |

Still request nothing from `arxiv.org` but a paper's full text.

## The coverage ledger

Combine the harvester's ledger records with your own, dropping their `invocation` field. A route stays *searched* once any invocation searched it; list a later invocation's failed queries for it as failed, with their diagnosis. A route the harvester recorded *unavailable* takes the diagnosis it gives. When `state.json` records a service's key as rejected, send that service nothing yourself, with the key or without it.
