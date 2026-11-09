# Prior art: a harvest pipeline for agent-run prior-art searches (2026-11-07)

- **Effort:** full method, because the result becomes a long-lived part of the prior-art search skill that every host repo receives.
- **Already known:** the developer had no tools in mind and had dismissed none. No earlier note or decision in this repo covers the topic.

## Need and criteria

The prior-art search skill queries literature APIs (OpenAlex, arXiv, Crossref, OpenAIRE, Semantic Scholar, Zenodo, Europe PMC, Hugging Face papers), GitHub, GitLab and Codeberg, and package registries. Its route table has ten literature routes: arXiv, OpenAlex, OpenAIRE, Semantic Scholar, papers.cool, Hugging Face papers, Zenodo, Crossref, Europe PMC and venue program pages. Agents send these requests themselves today, which spends tokens on mechanical work and lost queries without any record ([#157](https://github.com/jmbowman/agentic_development/issues/157)). The skill is Apache-2.0, ships as plain files copied into each host repo, and its scripts must pass this repo's strict lint profile. Scripts may declare their dependencies in a PEP 723 header and run with `uv run`.

| Requirement as proposed | Underlying need |
|---|---|
| A harvester per service that paces and retries | N1: stay within each service's stated rate limit, counted across all its endpoints and across concurrent callers, including several agent processes on one machine |
| | N2: retry politely: honor `Retry-After` and rate-limit headers, with bounded retries |
| The harvester inserts keys and the user agent | N3: credentials and identity handled by the tool, and never printed in logs, errors or output |
| Raw results on disk, ledger records from what ran | N4: every query recorded, so none is lost silently |
| (ideal) one maintained library for many services | N5: knows each service's request shapes and limits, and is kept current as their terms change |
| A normalizer and merger keyed by owner/repo | N6: records merged across rounds, so the next round's seeds are a diff |
| A record validator and renderer | N7: schema checks, and rendering of the ledger, the matrix and the papers table, with link and commit checks |

Hard criteria:
- H1: keeps within per-service limits across endpoints and concurrent callers, natively or with a small addition (a pluggable backend, one method to override, or one point every request passes through);
- H2: honors `Retry-After`;
- H3: keeps credentials out of logs and output;
- H4: a license compatible with use in, and redistribution beside, an Apache-2.0 skill;
- H5: actively maintained, with a commit or release in the last 12 months.

Preferences: Python; dependencies declarable in a PEP 723 header; coverage of many of the services; maintained per-service knowledge; one point that every request passes through, so a wrapper is cheap; a project open to contributions; offline testability. The skill's draft rules for agents that pace themselves (a 15-second wait without `Retry-After`, one retry) were treated as candidate rules, not criteria.

## Verdict

**Blend:** [paper-search-mcp](https://github.com/openags/paper-search-mcp)'s connectors, used as a library and pinned in a PEP 723 header, behind a transport shim of our own, plus our own clients for GitHub and the package registries.

- **The shim** is a `requests` transport adapter installed on every session the connectors create. Before each attempt it takes a slot from a [PyrateLimiter](https://github.com/vutran1710/PyrateLimiter) SQLite bucket with its file lock, one bucket per service holding every rate the service states. It also:
  - handles 429 and 503 responses, waiting `Retry-After` in either form, and reuses urllib3's parser;
  - refuses `verify=False`;
  - blocks shadow-library hosts;
  - fills in the Crossref contact address;
  - redacts credentials;
  - writes the query log and the raw responses.

  Every connector request passes through `requests.Session.send` (verified below), so nothing bypasses it. The shim is an estimated 250-400 lines.
- **The same shim is a contribution upstream.** A shared session factory, the limiter adapter (in memory by default, the SQLite bucket opt-in), one `Retry-After` loop, and the per-service limits in one table would replace pacing and retry code that is now spread across about 12 connector files and inconsistent between them. Each MCP client starts its own server process, so the project's in-process limits already fail its own users who run several clients. An issue is to be drafted after more use; until then the shim installs the same adapter from outside. Notes for the issue are in [the tool-feedback page](../tool-feedback/paper-search-mcp.md).
- **Fallback:** [litsurvey](https://github.com/udaykdk/litsurvey), if paper-search-mcp's direction or upkeep changes. It has no dependencies and one request function, `http.get`, and its contributing guide ties new sources to its limit table, so an atomic file-lock limiter (about 100 lines) fits its scope. It covers 5 of our 10 literature routes against paper-search-mcp's 7.

No maintained library both knows several literature services' request shapes and shares one limit across processes. The closest designs for a shared limit are [PyrateLimiter](https://github.com/vutran1710/PyrateLimiter) (general purpose) and [Liyux3/scholar-mcp](https://github.com/Liyux3/scholar-mcp) (scholarly, but its license fails H4).

N6 and N7 were searched only lightly (see Could not verify). [CoLRev](https://github.com/CoLRev-Environment/colrev)'s search history and per-source result feeds are the design to borrow for N4 and N6.

## Candidates and matrix

A first pass ruled out the multi-service scholarly tools because each limits rate within one process. A second pass read 15 of them in source as bases to wrap, extend, contribute to or fork, judging how cheaply each could meet the need with a shared limiter added.

Ranked shortlist:
1. [paper-search-mcp](https://github.com/openags/paper-search-mcp): the widest coverage of our routes (7 of 10: arXiv, OpenAlex with citations, Crossref, OpenAIRE, Semantic Scholar, Zenodo, Europe PMC), usable as a library without its MCP server, every request through `requests.Session.send`, and an active project with many contributors. Its connector-level problems (below) are all fixable in the shim. Two costs come with it:
   - **No usable release:** PyPI's 0.1.4 (2026-07-02) lacks most of the fixes on main, and main has no tags, so the harvester pins a commit.
   - **Slow, bursty upkeep:** one maintainer merges in bursts, with a median of about 42 days before an outside pull request gets a response.

   It would drop if the project stopped merging outside contributions or moved its connectors off `requests`.
2. [litsurvey](https://github.com/udaykdk/litsurvey): standard library only, one request function, and the best record merging (DOI, arXiv and Semantic Scholar IDs), but 5 of 10 routes, one author, `Retry-After` in seconds only, and no OpenAlex key. It would move up if paper-search-mcp's upkeep faltered.
3. [academic-tools-mcp](https://github.com/hunter-heidenreich/academic-tools-mcp): the best HTTP layer read, with one throttle per provider, `Retry-After` in both forms with caps, and current per-service notes, but only 3 of our routes, async only, and installable from git only. Its `net/` layer is the model for the shim.
4. [scholar-flux](https://github.com/SammieH21/scholar-flux): the cleanest injection point (a limiter passed to its constructor) and a scope that invites new providers, but no Semantic Scholar and only 3 of our routes.

| Candidate | Class | License (file:line at commit) | Reason |
|---|---|---|---|
| [paper-search-mcp](https://github.com/openags/paper-search-mcp) | build on | MIT, LICENSE:1-3 at cab1b5c | Widest coverage; one interception point; active |
| [PyrateLimiter](https://github.com/vutran1710/PyrateLimiter) | build on | MIT, LICENSE:1,3 at 4.5.1 | Atomic cross-process limiter with several rates per bucket |
| [litsurvey](https://github.com/udaykdk/litsurvey) | build on (fallback) | MIT, LICENSE:1-3 at 9c22eec | Standard library only; one request function; non-atomic cross-process spacing to replace |
| [academic-tools-mcp](https://github.com/hunter-heidenreich/academic-tools-mcp) | borrow ideas | MIT, LICENSE:1-3 at a246ecd | Throttle and retry layer to model the shim on |
| [scholar-flux](https://github.com/SammieH21/scholar-flux) | borrow ideas | Apache-2.0, LICENSE:1-2 at bd05215 | Providers as data; injectable limiter; key masking |
| [findpapers](https://github.com/jonatasgrosman/findpapers) | borrow ideas | MIT, LICENSE:1,3 at 3b42b66 | One retry method for most requests, but main is an unreleased rewrite with compiled dependencies |
| [CoLRev](https://github.com/CoLRev-Environment/colrev) | borrow ideas | MIT, LICENSE:1 at ba45b19 | Search history and per-source feeds (N4, N6); 58 HTTP call sites, no `Retry-After` |
| [scholar](https://github.com/dbosk/scholar) (scholarcli) | borrow ideas | MIT, LICENSE:1 at 5fa4bc2 | Quota groups persisted per service; no single request point |
| [scitech-librarian](https://github.com/fabiocampolim-design/scitech-librarian) | borrow ideas | Apache-2.0, LICENSE:1-3 at cd01f59 | Backends as data (N5); ignores `Retry-After` |
| [tenacity](https://github.com/jd/tenacity) | borrow ideas | Apache-2.0, LICENSE:2 at 9.2.1 | A retry loop with a computed wait; the shim's loop is small enough not to need it |
| [nature-academic-search](https://github.com/wp-a/nature-academic-search) | borrow ideas | MIT, LICENSE:1 at 725c2ec | Strips query strings from errors; three separate HTTP paths |
| [librarian-scholarly](https://github.com/kevin-j-smith/librarian-scholarly) | borrow ideas | Apache-2.0, LICENSE:2-3 at 70a323c | Cache keys kept free of credentials; needs a host package |
| [paper-search-pro](https://github.com/O0000-code/paper-search-pro) | borrow ideas | Apache-2.0, LICENSE.txt:2 at 2b55e08 | OpenAlex budget-header parsing; four SDKs, no single request point |
| [oalex](https://github.com/Burton-David/oalex), [citefinder](https://github.com/gitronald/citefinder) | borrow ideas | MIT (pointer only) | oalex sends the key as a header and fails fast on a spent budget; citefinder doesn't cache errors |
| [requests-cache](https://github.com/requests-cache/requests-cache), [hishel](https://github.com/karpetrosyan/hishel) | borrow ideas | BSD-2-Clause, BSD-3-Clause (read by a subagent; lines not recorded) | On-disk HTTP caches, for offline tests |
| [polymath-mcp](https://github.com/Moreti2002/polymath-mcp) | reject | MIT, LICENSE:1 at 1800f16 | No API key support; one commit; an HTTP-date `Retry-After` raises |
| [pvliesdonk/scholar-mcp](https://github.com/pvliesdonk/scholar-mcp) | reject | MIT, LICENSE:1 at 33bc510 | Ignores `Retry-After`; OpenAlex and Crossref only by DOI |
| [papers-mcp](https://github.com/LAHutchins91/papers-mcp) | reject | MIT, LICENSE:1 at 42d6135 | TypeScript and hosted; its keyed Semantic Scholar pace breaks the 1-a-second limit |
| [local-deep-research](https://github.com/LearningCircuit/local-deep-research) | reject | MIT, LICENSE:1 at c11365d | Its adaptive limiter probes below learned waits and ignores stated limits; its `Retry-After` parser is worth borrowing |
| [pubmed-search-mcp](https://pypi.org/project/pubmed-search-mcp/) | borrow ideas | Apache-2.0 (pointer only) | Its docs describe concurrency shared at the most conservative source's limit and per-source cooldowns after a 429, within one process; PubMed isn't one of our routes |
| [rate-limit-lite](https://github.com/aiplusplus360/rate-limit-lite) | borrow ideas | MIT (read by a subagent) | Shares a limit across processes through SQLite `BEGIN IMMEDIATE`; created the day it was found, so too new to depend on |
| [literature-evidence-mcp](https://github.com/Furox-Art/literature-evidence-mcp) | borrow ideas | pointer only | A file-locked, hash-chained evidence ledger: an idea for the query log (N4) |
| [cloak](https://github.com/hoophq/cloak), [ghx](https://github.com/brunoborges/ghx) | borrow ideas | ghx: MIT (read by a subagent); cloak: not read | cloak swaps placeholder credentials for real ones on the way out (N3); ghx is a working machine-wide broker in front of `gh`, for GitHub only |
| [PaperSearch](https://github.com/dr-dumpling/PaperSearch), Lixplore_cli and litmesh (no links found) | reject | MIT (read by a subagent) | Smaller multi-source tools with in-process limits only; PaperSearch and litmesh are TypeScript |
| [safethrottle](https://github.com/mikenrafter/safethrottle) | reject | no license found | Fails H4 |
| [requests-ratelimiter](https://github.com/JWCook/requests-ratelimiter) | reject | MIT, LICENSE:1,3 at 0.10.0 | Fails H3: logs the full request URL |
| [stamina](https://github.com/hynek/stamina) | reject | MIT, LICENSE:1,3 at 26.1.0 | Its default logging hook logs call arguments, which risks H3 |
| [Liyux3/scholar-mcp](https://github.com/Liyux3/scholar-mcp) | reject | PolyForm Noncommercial with extra terms, LICENSE:1 at 93a1867 | Fails H4 |
| [limits](https://github.com/alisaifee/limits) | reject | MIT (pointer only) | No file backend, so sharing across processes needs a server |
| [throttled-py](https://github.com/ZhuoZhuoCrayon/throttled-py) | reject | MIT (read by a subagent) | No file backend, so sharing across processes needs a server |
| [wenxian](https://github.com/njzjz/wenxian) | reject | LGPL-3.0, LICENSE:1 at 82f7e82 | Weak copyleft; identifier lookup only |
| Local forward proxies: [ZT-Agent-Proxy](https://github.com/Tamerktb/ZT-Agent-Proxy), [distributed-proxy-rate-limiter](https://github.com/kotylevskiy/distributed-proxy-rate-limiter), [proxylens-mitmproxy](https://pypi.org/project/proxylens-mitmproxy/), [trollbridge](https://github.com/dandriscoll/trollbridge) | reject | MIT where read | None limits request rate over HTTPS without terminating TLS, which needs a local certificate authority every client trusts |
| [backoff](https://github.com/litl/backoff), [bottleneck](https://www.npmjs.com/package/bottleneck), ratelimit, ratelimiter, scholarly, Sickle (no links recorded for the last four) | reject | not read | Fail H5 |
| papersgpt-for-zotero, paper-distill-mcp, scitex-scholar, z-search, fastpaper-cli, papis, crossref-local, openalex-local, SouWen (no links recorded) | reject | AGPL or GPL (pointer only) | Fail H4 |

Single-service clients ([pyalex](https://github.com/J535D165/pyalex), [arxiv.py](https://github.com/lukasschwab/arxiv.py), [habanero](https://github.com/sckott/habanero), [semanticscholar](https://github.com/danielnsilva/semanticscholar)) all pace within one process, and are references for request shapes only.

Matrix (bases verified in source; "shim" means the gap is closed by the transport shim, not by the candidate):

| Criterion | paper-search-mcp | litsurvey | academic-tools-mcp | scholar-flux | PyrateLimiter |
|---|---|---|---|---|---|
| H1 limits across processes | extensible: every request through `requests.Session.send` | extensible: one `http.get` (http.py:119-160); its file-based spacing isn't atomic (http.py:92-104) | extensible: override `Throttle.slot` (throttle.py:49-223) | extensible: limiter passed in (search_api.py:165,187) | native, with `use_file_lock=True` (sqlite_bucket.py:91-96,122-154) |
| H2 `Retry-After` | partial: both forms in Google Scholar only (google_scholar.py:73-93); seconds only in Semantic Scholar, IEEE and the institutional connector; a fixed 2-second wait in Crossref (crossref.py:74-77); ignored elsewhere | partial: seconds only (http.py:109-116) | native, both forms, capped (http.py:144-178) | native, both forms (retry_handler.py:389-503) | unsupported (listing) |
| H3 credentials kept out | partial: keys in headers; cache off when a key is set (search_cache.py:46-71) | partial: `--debug` prints full URLs (http.py:134-135) | native: logs carry URLs without query strings | partial: masks its own handlers only | native: logs carry no URLs |
| H4 license | MIT | MIT | MIT | Apache-2.0 | MIT |
| H5 maintained | native (last commit 2026-10-02) | native (v1.2.1, 2026-10-17) | native (11 releases in 2026) | native (2026-08-11) | native (4.5.1, 2026-10-20) |
| Our literature routes covered | 7 of 10 | 5 of 10 | 3 of 10 | 3 of 10 | n/a |
| N4 query log | unsupported (listing) | partial: per-run history JSON | unsupported | partial: opt-in cache | n/a |
| Interface | library and JSON CLI; MCP optional | library, JSON CLI | async library behind an MCP server | library | library |
| Dependencies | 10, including `fastmcp` and `mcp` even for library use | none | 4 | 6 | none; `filelock` for the file lock |

**Blends considered.**
- paper-search-mcp plus the shim plus our own GitHub and registry clients: chosen.
- litsurvey extended with a file-lock limiter and three new sources (OpenAIRE, Zenodo, Hugging Face papers), plus the same GitHub and registry clients: the fallback. It costs more of our own connector code, and with one author it leans more on our upkeep.
- A local rate-limiting forward proxy in front of any client: rejected. Over HTTPS it limits only connections unless it terminates TLS.
- scholar-flux with an injected limiter: it lacks Semantic Scholar, the service with the tightest keyed limit.

**Scenario walk.**
1. *Three subagents query Semantic Scholar with a key at once.* Each attempt takes a slot from the service's SQLite bucket at 1 a second, so their requests are spaced across processes. paper-search-mcp's own Semantic Scholar pacing doesn't matter, since the shim sees each attempt. This passes.
2. *A service changes its terms.* The limit changes in the shim's per-service table. If upstream accepts the contribution, the change goes there. The harvester pins a commit, so a custom Renovate regex manager with the `git-refs` datasource proposes the new commit. The `pep723` manager doesn't refresh a script lock file, so a lock-refresh step runs `uv lock --script`, as the lock-refresh workflow does for `mise.lock`.
3. *Crossref returns 429 with an HTTP-date `Retry-After`.* The shim parses it, holds the service's bucket for the wait so other processes wait too, and retries, whatever the connector's own retry does.
4. *A connector falls back to `verify=False` or calls a shadow-library host.* The shim refuses the request and logs it, and the route records the failure.

## Limitations checked in source

Verified:
- [paper-search-mcp](https://github.com/openags/paper-search-mcp)'s connectors all fetch through `requests`: `feedparser` only parses content `requests` fetched (arxiv.py:93,202 at cab1b5c); `httpx` appears only in `server.py` and `http_auth.py`; `urllib3` is used only to silence warnings (listing over `paper_search_mcp/`).
- paper-search-mcp reads keys and contact addresses from environment variables, with an optional `PAPER_SEARCH_MCP_` prefix (config.py:73-82 at cab1b5c), and on first use loads `~/.config/paper-search-mcp/.env` into the environment unless `PAPER_SEARCH_MCP_ENV_FILE` points elsewhere (config.py:14-21,49-66).
- paper-search-mcp hard-codes Crossref's contact address as `paper-search@example.org` (crossref.py:69 at cab1b5c).
- paper-search-mcp's OpenAIRE and CiteSeerX connectors retry without TLS verification after an SSL error, and silence urllib3's warning for the whole process (openaire.py:150-159, citeseerx.py:47-54 at cab1b5c). Its IEEE connector sends the key as a URL query parameter (ieee.py:150).
- paper-search-mcp ships a Sci-Hub connector (`academic_platforms/sci_hub.py` at cab1b5c), a shadow library the skill must never use.
- paper-search-mcp sends the Semantic Scholar key as `x-api-key` with no 1-a-second pacing (semantic.py:159-218 at cab1b5c).
- [PyrateLimiter](https://github.com/vutran1710/PyrateLimiter) reserves atomically across processes only with `use_file_lock=True` (sqlite_bucket.py:91-96,122-154,249-256 at 4.5.1), accepts several rates per bucket (utils.py:10-43), treats one table as one limit (sqlite_bucket.py:30-36), and leaves mixing threads and processes in file-lock mode undecided (sqlite_bucket.py:242-245).
- [litsurvey](https://github.com/udaykdk/litsurvey)'s cross-process spacing reads a file's modification time, sleeps and touches the file with no lock in between, so two processes can both proceed (http.py:72-104 at 9c22eec).
- [requests-ratelimiter](https://github.com/JWCook/requests-ratelimiter) logs the full URL (requests_ratelimiter.py:135 at 0.10.0).
- Renovate 44.212.0's `pep723` manager bumps versions in inline headers but has no `updateArtifacts`, so it leaves a uv script lock file stale (`dist/modules/manager/pep723/index.js:6-19`). It sends every dependency to the PyPI datasource (`pep621/utils.js:33-47`), so a git-pinned dependency such as a paper-search-mcp commit isn't bumped. That is inferred from reading the code, not from running it. A custom regex manager with the `git-refs` datasource can bump the commit. Details are in [the Renovate tool-feedback page](../tool-feedback/renovate.md).

Docs only:
- OpenAlex needs no key for basic queries; it allows 10 requests a second without a key and 30 with a free one, sent as `api_key` or an `Authorization: Bearer` header, and meters use by a daily budget ([authentication](https://help.openalex.org/api/authentication/), read 2026-11-07); the page doesn't mention a mailto "polite pool". This contradicts pyalex's documentation, which says a key has been required since 2026-02-13; the service's own page is taken as authoritative. academic-tools-mcp's description of credit-based metering matches the daily budget.
- paper-search-mcp's issue tracker (read 2026-11-07) holds no earlier proposal for a shared session or a central limiter; its roadmap ([#94](https://github.com/openags/paper-search-mcp/issues/94)) lists "Unified retry with exponential backoff" without a design. The maintainer's notes on [#144](https://github.com/openags/paper-search-mcp/pull/144) lean against new dependencies. An open report of path traversal in arXiv downloads ([#155](https://github.com/openags/paper-search-mcp/issues/155)) concerns a function the harvester doesn't call. The details are in [the tool-feedback page](../tool-feedback/paper-search-mcp.md).

Could not verify:
- The second-pass readers worked from shallow clones, so commit cadence comes from head dates, changelogs and READMEs.
- [scholar-flux](https://github.com/SammieH21/scholar-flux): whether exception messages and URLs stored in its cache are masked.
- PulseMCP was unavailable: its v0beta API returns 410 (shut down in September 2026), and v0.1 requires an API key.
- The awesome-mcp-servers README itself was never opened, and the GitHub topics for agent skills were checked only through web search.
- N6 and N7 were searched lightly. The R packages (litsearchr, openalexR, citationchaser) were excluded for time.

**Leads for the route list.** paper-search-mcp has connectors for sources that `references/sources.md` doesn't list and that [the catalogs note](2026-11-04-agent-readable-catalogs-and-paper-sources.md) didn't judge: OpenReview (machine-learning venues), HAL, bioRxiv, medRxiv, chemRxiv, CiteSeerX, IACR, PubMed and PMC, and generic OAI-PMH. Each needs the catalogs note's probe before it joins the route list. CORE, DOAJ, dblp, SSRN, ACM, IEEE, Scopus, Web of Science and Google Scholar were judged there, and their reasons stand.

## Coverage ledger

| Route | State | Queries or reason |
|---|---|---|
| The stack itself | searched | Python 3.12, `uv`, `curl`; the standard library's `sqlite3` and `fcntl` could build a cross-process limiter; nothing knows any service's shapes or limits |
| Earlier notes and decisions | searched | `docs/prior-art/` grep for client and limiter names; none |
| GitHub repository search | searched | "openalex arxiv crossref"; "scholarly api client pushed:>2025-11-01"; "rate limiter sqlite"; second pass: "federated academic search"; "scholarly metasearch"; "systematic review search"; "OAI-PMH harvester"; "rate limit forward proxy" |
| GitHub topics | searched | `topic:openalex topic:crossref`; `topic:literature-search`; `topic:rate-limiter language:python` |
| GitHub code search | searched | "Retry-After api.openalex.org language:python"; "SQLiteBucket crossref OR arxiv OR openalex"; second pass: "api.openalex.org export.arxiv.org api.crossref.org api.openaire.eu"; "pyrate_limiter arxiv"; "filelock api.openalex.org" |
| GitLab and Codeberg search | searched | "openalex"; "scholarly api"; "crossref client"; "rate limiter" |
| npm | searched | "keywords:openalex"; "scholarly api client rate limit"; "rate limiter redis shared" |
| PyPI | searched | JSON for 41 known names; `site:pypi.org` "python client OpenAlex Crossref arXiv Semantic Scholar unified rate limit retry"; "rate limiter shared across processes sqlite file lock requests"; "academic search openalex arxiv crossref semantic scholar multi-source rate limit" |
| crates.io | searched | "openalex"; "scholarly literature search"; "distributed rate limiter sqlite" |
| ecosyste.ms | searched | keywords openalex, crossref, arxiv, semantic-scholar, rate-limiter, literature-review |
| Homebrew formulae | searched | local regexes over `formula.json` for scholarly, citation and rate-limit terms |
| LibHunt | searched | `/r/PyrateLimiter`; `/r/requests-cache`; `/r/arxiv.py` (its `/alternatives` pages return 404) |
| Cross-language equivalents | searched | "rust OR go OR typescript library unified client OpenAlex Crossref arXiv Semantic Scholar rate limiting per source"; the R scholidonline docs |
| Awesome lists | searched | "awesome openalex crossref arxiv" (code search); "awesome scholarly APIs list"; "awesome rate limiting list"; the lists found catalog APIs, not harvest libraries |
| General web search | searched | "unified scholarly API client python shared rate limiter across processes"; "multi-source academic paper search library python"; "rate limiting forward proxy per-host requests per second mitmproxy addon" |
| Hosted services | searched | Lens.org, Dimensions, Scopus and the Semantic Scholar datasets (docs only); none covers arXiv, Zenodo, OpenAIRE, GitHub and registries, and all need accounts |
| MCP Registry | searched | "openalex"; "arxiv"; "scholar"; "papers"; "literature" |
| PulseMCP | unavailable | network: v0beta API shut down (410); v0.1 needs an API key |
| Skill directories | searched | skills.sh: "paper search"; "openalex"; "rate limit" |
| Claude Code plugin marketplaces | searched | local regex over 317 plugins for scholarly and rate-limit terms; no match |
| Awesome lists for agent skills | searched | "awesome-mcp-servers Research section academic papers"; returned directory sites, not the README |
| GitHub topics for agent skills | searched | through web search only ("topic:mcp-server openalex semantic-scholar"), because another subagent held GitHub |
| Anthropic's skills repo | excluded | its reference skills don't cover literature APIs or rate limiting, and the need is a library or script |
| Language registries | excluded | the need names no language beyond Python, with npm and crates.io searched as prior art |
| libraries.io | excluded | the need doesn't name several package ecosystems |
| nixpkgs | excluded | condition unmet: no brotli decompressor installed |
| AUR, alternativeto.net | excluded | their triggers are end-user and desktop tools; this need is a library or script |
| aitoolnet.com | excluded | the need isn't an AI product |
| Literature routes | excluded | no approach question, and the software routes found implementations of every requirement |

## Snowball rounds

Subagents searched in parallel, each holding its own services, so rounds are counted per group.

- **First pass:**
  - **GitHub group:**
    - Round 1 found [findpapers](https://github.com/jonatasgrosman/findpapers), [paper-search-mcp](https://github.com/openags/paper-search-mcp), [scitech-librarian](https://github.com/fabiocampolim-design/scitech-librarian), [litsurvey](https://github.com/udaykdk/litsurvey), [PyrateLimiter](https://github.com/vutran1710/PyrateLimiter), [requests-ratelimiter](https://github.com/JWCook/requests-ratelimiter), [requests-cache](https://github.com/requests-cache/requests-cache), [hishel](https://github.com/karpetrosyan/hishel), [limits](https://github.com/alisaifee/limits), [throttled-py](https://github.com/ZhuoZhuoCrayon/throttled-py), [tenacity](https://github.com/jd/tenacity), [stamina](https://github.com/hynek/stamina), [rate-limit-lite](https://github.com/aiplusplus360/rate-limit-lite), [paper-search-pro](https://github.com/O0000-code/paper-search-pro) and [local-deep-research](https://github.com/LearningCircuit/local-deep-research).
    - Round 2 found none new.
  - **Registries group:**
    - Round 1 found [scholar](https://github.com/dbosk/scholar) (scholarcli), along with paper-search-mcp, PyrateLimiter, requests-ratelimiter, limits, tenacity, stamina, hishel and requests-cache.
    - Round 2 found [pubmed-search-mcp](https://pypi.org/project/pubmed-search-mcp/) and [nature-academic-search](https://github.com/wp-a/nature-academic-search), plus four leads judged weak fits (scholar-corpus, wesearch, agent-papers-cli, doiget).
    - Round 3 found [citefinder](https://github.com/gitronald/citefinder) and [oalex](https://github.com/Burton-David/oalex).
    - Round 4 found search-hub (no link found) and [CoLRev](https://github.com/CoLRev-Environment/colrev). Round 5 wasn't run, because its seeds were MCP servers of the shape already found; the second pass's reads of CoLRev and those shapes stand in for it.
  - **Web group:**
    - Round 1 found [scholar-flux](https://github.com/SammieH21/scholar-flux), [librarian-scholarly](https://github.com/kevin-j-smith/librarian-scholarly), paper-search-mcp, PyrateLimiter and requests-ratelimiter.
    - Round 2 found [polymath-mcp](https://github.com/Moreti2002/polymath-mcp), [papers-mcp](https://github.com/LAHutchins91/papers-mcp), fastpaper-cli (no link recorded) and limits.
    - Round 3 found none new.
  - **MCP Registry follow-up:** [Liyux3/scholar-mcp](https://github.com/Liyux3/scholar-mcp), which fails H4, and [pvliesdonk/scholar-mcp](https://github.com/pvliesdonk/scholar-mcp).
- **Second pass:** new vocabulary (federated search, metasearch, systematic-review search sources, OAI-PMH harvesters), scholarly code that already uses a shared limiter, and local proxies.
  - Round 1, repository search, found [academic-tools-mcp](https://github.com/hunter-heidenreich/academic-tools-mcp), [PaperSearch](https://github.com/dr-dumpling/PaperSearch), Lixplore_cli and litmesh (no links found).
  - Round 2, code and proxy search, found [wenxian](https://github.com/njzjz/wenxian), [literature-evidence-mcp](https://github.com/Furox-Art/literature-evidence-mcp), [trollbridge](https://github.com/dandriscoll/trollbridge), [cloak](https://github.com/hoophq/cloak), [ZT-Agent-Proxy](https://github.com/Tamerktb/ZT-Agent-Proxy), [distributed-proxy-rate-limiter](https://github.com/kotylevskiy/distributed-proxy-rate-limiter), [safethrottle](https://github.com/mikenrafter/safethrottle) and [ghx](https://github.com/brunoborges/ghx).
  - Round 3, web and PyPI search, found [proxylens-mitmproxy](https://pypi.org/project/proxylens-mitmproxy/), plus two leads not taken further (one on Docker Hub only, one a WAF-evasion tool).
  - Round 4 found none new.

Apart from the registries group's fifth round, every group stopped when a round added no new serious candidate. The round cap wasn't reached.

## Refresh trigger

Search again if [paper-search-mcp](https://github.com/openags/paper-search-mcp) stops merging outside contributions, moves its connectors off `requests`, or declines the shared-limiter change in a way that blocks the shim. Also search again if six months pass before the harvest design is built.
