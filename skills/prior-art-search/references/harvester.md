# Harvester

`scripts/harvest.py` sends a batch of literature queries for you and writes what came back to disk. You choose the queries, read the results and classify the papers; the harvester paces, sends, retries, logs and summarizes. It covers:

- keyword searches on arXiv and OpenAlex;
- OpenAlex's works citing a paper (`citations`) and the works it references (`references`);
- every Semantic Scholar request: recommendations from seed papers (`recommend`) and exact-title lookups (`lookup`). Semantic Scholar refuses many requests at busy times, so the harvester retries these up to six times on a growing backoff, within about a minute per request.

Send everything else to arXiv and OpenAlex (open-access and DOI lookups, arXiv ID lookups, full text) yourself, under the rules in [SKILL.md](../SKILL.md) and [sources](sources.md). Don't send keyword searches to Semantic Scholar at all.

## Running it

It needs [`uv`](https://docs.astral.sh/uv/), which installs its pinned dependencies on first use:

```sh
uv run --script <skill>/scripts/harvest.py <action> --service <service> --round <n> \
    --run-dir <run directory> [--max-results <n>] [--show <n>] <query or paper ID>...
```

- `<action>`: `search` (with `--service arxiv` or `openalex`), `citations` or `references` (with `--service openalex`), or `recommend` or `lookup` (with `--service semanticscholar`).
- `--service`: `arxiv`, `openalex` or `semanticscholar`, matching the action.
- `--round`: the snowball round, from 1.
- `--run-dir`: the run directory. Use one for the whole skill run, in your session's scratch directory or a directory the host repo's git ignores, and give the same path to every invocation and to every subagent that searches the literature. Invocations can share it at once.

## In a sandboxed shell

Your shell may only be able to write inside the host repo, as under Claude Code's sandbox. Then your scratch directory and `~/.cache` aren't writable:

- Put the run directory under `prior-art-search/` in a directory at the top of the host repo that git ignores, such as `tmp/prior-art-search/run-1` (check with `git check-ignore -q tmp/`). If there is none, ask the developer whether to have one ignored, and add it to `.gitignore` only on a yes. In a non-interactive run, send the requests yourself and give that reason in the ledger.
- If `uv` fails with `Failed to initialize cache` (or another error writing its cache), run the harvester again with `UV_CACHE_DIR=<ignored directory>/prior-art-search/uv-cache` before the command. Fall back to sending the requests yourself only if that fails too.
- The harvester keeps its pacing in the run directory when it can't write `~/.cache`, and its first summary line says so. That's expected.
- `--max-results`: results to fetch per query. For `search`, 1 to 100 (50 when omitted); for `citations`, `references` and `recommend`, 1 to 500 (100 when omitted); a `lookup` returns its one best match. A page of up to 100 is one request, so deep pages cost nothing extra in requests.
- `--show`: results to print per query (10 when omitted). The rest stay in `records.jsonl`.
- Quote each query or title as one argument, and put `--` before the queries when one starts with `-`. Options can't be abbreviated, and only `--help` prints help. An OpenAlex search with more than 5 of `AND`, `OR` and `NOT` in capitals is refused as invalid input. A `citations` or `references` paper ID is a DOI (bare, `doi:` or a `doi.org` URL) or an OpenAlex work ID (`W…` or an `openalex.org` URL). A `recommend` seed is a DOI in the same forms (a DOI URL with a query string or fragment is refused), a new-style arXiv ID (`2401.12345`, bare or with `arXiv:`; a version suffix is dropped) or a Semantic Scholar paper ID (40 hexadecimal characters); old-style arXiv IDs are refused as invalid input.
- A `lookup` result is the closest title Semantic Scholar has, which can be a different paper. Its record carries `match_score`; before you use it, check that its title is the one you asked for, ignoring case, punctuation, whitespace and accents, and treat anything else as no match.

It reads the access settings file itself, under the same rules as you, so never pass a key on its command line.

## What it prints

One line per query: its ID, service, query, outcome, result count, and a reason (a refusal's, or `daily budget`) or truncation when there is one. Under each query that ran, one line per printed result: rank, year, citation count, the service's ID and the title (`-` for a missing value; a result printed earlier in the invocation shows only its ID). Then how many more results are in `records.jsonl`, the invocation's coverage-ledger record as one JSON line, and the paths of the files below.

Work from this summary. Don't read raw bodies, `records.jsonl` or `queries.jsonl` whole; filter them for the queries or records you need, for example `jq -c 'select(.query_id == "<id>")' records.jsonl`, or `jq -r 'select(.service_id == "W123") | .abstract' records.jsonl` for one result's abstract.

Outcomes: `ok`, `empty` (for a `lookup`, no title matched), `not found` (a paper ID or seed that doesn't exist), `rate limit`, `authentication`, `client error` (the service rejected the query), `network`, `not sent: limiter wait` (your machine's shared pacing would have waited over 60 seconds), `refused` (with its reason; `daily budget` means OpenAlex's daily budget ran out earlier in this run), `skipped: service throttled`, `internal error` and `invalid input`.

## Files in the run directory

- `queries.jsonl`: one line per query, with its outcome and every attempt.
- `records.jsonl`: one harvest record per result, with the fields `query_id`, `rank`, `title`, `authors`, `year`, `venue`, `doi`, `arxiv_id`, `service_id` (the ID the summary prints), `abstract`, `citations`, `url` and `pdf_url`, plus `match_score` for a `lookup`. A harvest record isn't a paper record: write those only after reading.
- `ledger.jsonl`: one coverage-ledger record per route per invocation.
- `raw/`: each response body.
- `harvest.log`: the connectors' log lines.
- `state.json`: services whose API key was rejected, and whether OpenAlex's daily budget ran out.

## Exit status

| Status | Meaning | What to do |
|---|---|---|
| `0` | Every query ran. | Read the summary. |
| `3` | At least one query didn't run. | Read the outcomes. Don't resend those queries yourself. Correct and rerun an `invalid input` or `client error` query at once if you can; rerun any other failed query only in a later round. After a `rate limit`, or a Semantic Scholar query ending `network`, don't run the harvester for that service again until the next round; the route's substitute covers it meanwhile. |
| `4` | Nothing was sent. The message starts `harvest.py: usage error:`, `harvest.py: setup error:` or `harvest.py: internal error`. | After a usage error, fix the command and rerun. After any other, report the problem it names, and send these requests yourself under the rules in [SKILL.md](../SKILL.md). |

Any other status means `uv` failed before the harvester started; send the requests yourself then too. Whenever you send them yourself, say in each affected route's ledger `reason` that they were sent without the harvester.

## The coverage ledger

Combine the harvester's ledger records with your own, dropping their `invocation` field. A route stays *searched* once any invocation searched it; list a later invocation's failed queries for it as failed, with their diagnosis. A route the harvester recorded *unavailable* takes the diagnosis it gives. When `state.json` records a service's key as rejected, send that service nothing yourself, with the key or without it.
