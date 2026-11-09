# paper-search-mcp

[paper-search-mcp](https://github.com/openags/paper-search-mcp) is the planned connector library behind the prior-art search skill's harvester ([the harvest pipeline note](../prior-art/2026-11-07-search-harvest-pipeline.md)). Items below are from reading commit `cab1b5c` (2026-10-02) and the project's issues and pull requests as of 2026-11-07. None has been raised upstream yet: the plan is one issue proposing a shared HTTP layer, filed after more use of the library, with the smaller items attached or filed beside it.

## Upstream context for the proposal

- **Release lag:** the latest PyPI release, 0.1.4 (2026-07-02), is far behind main, and main still reports 0.1.4 with no tags or GitHub releases. The fixes that matter here (the arXiv pacing and HTTPS fixes, Sci-Hub made opt-in in [#115](https://github.com/openags/paper-search-mcp/pull/115), parser fixes, the `mcp<2` pin) are on main only. A harvester has to pin a commit, and [#143](https://github.com/openags/paper-search-mcp/pull/143) says outright that it ships no PyPI release.
- **How contributions land:** one maintainer merges, in bursts (the last on 2026-10-02). External pull requests are usually rebuilt into the maintainer's own, with co-author credit ([#117](https://github.com/openags/paper-search-mcp/pull/117) and CONTRIBUTING). The median wait for a first response is about 42 days, and the median time to merge about 7 days. Twelve outside authors had work merged in the last six months.
- **Dependencies:** there is no written policy. An MCP bump and `joserfc` were accepted, but the scope notes on [#144](https://github.com/openags/paper-search-mcp/pull/144) repeat "no new dependency", and suggested libraries ([#74](https://github.com/openags/paper-search-mcp/issues/74), [#94](https://github.com/openags/paper-search-mcp/issues/94)) weren't taken up. The proposal should make the case for PyrateLimiter explicitly, and offer an in-memory fallback that needs no new dependency if it is declined.
- **Prior proposals:** none for a shared session, a central or cross-process limiter, or PyrateLimiter. The roadmap in [#94](https://github.com/openags/paper-search-mcp/issues/94) lists "Unified retry with exponential backoff" as one line, with no design, so the proposal can build on it.
- **Library use** isn't documented and has no stability promise. Recent changes on main replaced silent empty results with errors in several connectors ([#125](https://github.com/openags/paper-search-mcp/pull/125), [#130](https://github.com/openags/paper-search-mcp/pull/130), [#144](https://github.com/openags/paper-search-mcp/pull/144)), so the harvester needs its own tests against the pinned commit.

## Related work in other forks

On 2026-11-08, 147 forks pushed since July 2026 were checked against upstream; 46 had commits ahead. None makes Crossref's address configurable, removes the insecure TLS retries, or adds a network-test marker. Licenses below are GitHub's metadata only.
- [hervold/paper-search-mcp](https://github.com/hervold/paper-search-mcp) `87c9454` moves throttling and retries into the `PaperSource` base class: a minimum interval per class, jittered backoff, and `Retry-After` in both forms capped at 60 s, replacing 26 retry loops. Its interval is kept per instance, direct `session.get` calls bypass it, and failures become empty results again. It shows demand for the shared HTTP layer, and its interval table is a cross-check for ours.
- [ArturShirokov/paper-search-mcp](https://github.com/ArturShirokov/paper-search-mcp):
  - `71c98a9` and `06102d5` add arXiv pacing across processes through a lock-protected timestamp file, with a two-process test. It is the only cross-process limiter in any fork, for arXiv alone.
  - `d4078ef` adds shared helpers whose error messages leave out the URL, since it can carry keys, and that reject replies that aren't JSON or XML, across about 20 connectors.
  - `34fcb1c` strips JATS markup from Crossref abstracts and leaves missing dates empty instead of 1970-01-01.

  The error helpers and the Crossref fix are worth taking into proposals, with credit, as upstream's CONTRIBUTING asks.
- [He-Ach/paper-search-mcp](https://github.com/He-Ach/paper-search-mcp) `62fec63` and [Butanium/paper-search-mcp](https://github.com/Butanium/paper-search-mcp) `895fab9` mount an `HTTPAdapter` that offers no ALPN, after arXiv answered Python's TLS handshake with empty HTTP 406 replies. Upstream handled [#121](https://github.com/openags/paper-search-mcp/issues/121) differently. A shared adapter has to keep whatever TLS setup a connector needs.
- [fcakyon/paper-search-cli](https://github.com/fcakyon/paper-search-cli) removes the MCP server entirely: demand for making the MCP dependencies an extra.

## Pacing and retries live in each connector

- **Where:** about 12 files under `paper_search_mcp/academic_platforms/`, for example `arxiv.py:26-70` (a class lock and a minimum interval), `ssrn.py:58,146-147`, `doaj.py:135`, `crossref.py:73-78`, `semantic.py:205-266`, `ieee.py:71-110`, `google_scholar.py:73-131`.
- **What:**
  - Each connector paces and retries its own way, and all of it holds only within one process. Each MCP client starts its own server process, so a user running several clients, or several agent sessions, sends each service the sum of their rates from one address and, where set, one key.
  - `Retry-After` is parsed in both its forms only in `google_scholar.py:73-93`. Semantic Scholar, IEEE and the institutional connector read it as whole seconds, Crossref waits a fixed 2 seconds (`crossref.py:74-77`), and the rest ignore it.
- **Evidence:** read in source at `cab1b5c`; a search for `Retry-After` across `paper_search_mcp/` finds it in four files only.
- **Suggested fix:**
  - A shared `make_session()` that every connector calls in place of `requests.Session()`.
  - On that session, a transport adapter whose `send()` takes a [PyrateLimiter](https://github.com/vutran1710/PyrateLimiter) slot for the request's service before each attempt. The bucket is in memory by default, with an opt-in SQLite bucket and file lock (set through an environment variable) for several processes.
  - One retry loop in the adapter, using urllib3's `Retry.parse_retry_after` for both header forms.
  - Each service's limits in one table.

  This removes the per-connector sleeps, locks and parsers. urllib3's built-in `Retry` can't stand in for the loop: its retries run below the adapter and would skip the limiter.
- **Raised upstream:** no.

## Semantic Scholar has no keyed pacing

- **Where:** `semantic.py:159-218`.
- **What:** the key goes in `x-api-key`, correctly, but nothing holds requests to 1 a second across all endpoints together, which is the limit Semantic Scholar gives each key ([API tutorial](https://www.semanticscholar.org/product/api/tutorial)).
- **Evidence:** `semantic.py:159-218` read at `cab1b5c`; the limit from the tutorial, read 2026-11-07.
- **Suggested fix:** an entry in the shared limits table above.
- **Raised upstream:** no.

## Crossref's contact address is hard-coded

- **Where:** `crossref.py:69`, `params['mailto'] = 'paper-search@example.org'`.
- **What:** every user's requests claim Crossref's polite pool under one placeholder address, which Crossref can't use to reach anyone.
- **Evidence:** the line, read at `cab1b5c`; the arXiv, Europe PMC and OpenAlex connectors carry similar placeholder addresses in their user agents.
- **Suggested fix:** read the address from `get_env("CROSSREF_MAILTO")`, and send `mailto` only when it is set.
- **Raised upstream:** no.

## Connectors retry without TLS verification

- **Where:**
  - OpenAIRE: `openaire.py:150-159`;
  - CiteSeerX: `citeseerx.py:47-54`;
  - Sci-Hub: `sci_hub.py:55,87`, always.
- **What:** after an SSL error, OpenAIRE and CiteSeerX retry the request with `verify=False`, so a man-in-the-middle certificate is accepted. Both also silence urllib3's insecure-request warning for the whole process, which hides the same problem in every other library the process uses. No issue or pull request discusses this.
- **Evidence:** the cited lines, read at `cab1b5c`; a review of the issue tracker on 2026-11-07.
- **Suggested fix:** let the SSL error surface, or make the insecure retry an explicit opt-in, and never silence warnings process-wide.
- **Raised upstream:** no.

## IEEE's key travels in the URL

- **Where:** `ieee.py:150`, which sends the key as the `apikey` query parameter.
- **What:** a key in the query string ends up wherever the URL is logged or shown in an error. The skill doesn't use IEEE, but the shim's redaction has to cover query parameters for any connector that does this.
- **Evidence:** the line, read at `cab1b5c`. Whether any connector logs full URLs wasn't checked.
- **Suggested fix:** use a header if IEEE accepts one; otherwise make sure no log line or exception message carries the full URL.
- **Raised upstream:** no.

## Path traversal in arXiv downloads

- **Where:** `download_arxiv`; reported in [#155](https://github.com/openags/paper-search-mcp/issues/155) (open, no maintainer response, a CVE requested).
- **What:** the `paper_id` half is fixed on main (`e69d3a4`). The reporter says `save_path` is still unchecked; this wasn't verified here. Every PyPI release is affected. The harvester downloads no PDFs, so it doesn't call this function.
- **Evidence:** the issue thread, read 2026-11-07.
- **Suggested fix:** follow #155.
- **Raised upstream:** yes, by someone else.

## A second settings file is loaded implicitly

- **Where:** `config.py:14-21,49-66`.
- **What:** on first use, `~/.config/paper-search-mcp/.env` is loaded into the process environment, so a library user's process picks up keys from a file it never named. The harvester turns this off by pointing `PAPER_SEARCH_MCP_ENV_FILE` at a path that doesn't exist.
- **Evidence:** the cited lines, read at `cab1b5c`.
- **Suggested fix:** load the file only from the MCP server's entry point, or document the switch for library use.
- **Raised upstream:** no.

## MCP dependencies are required for library use

- **Where:** `pyproject.toml`, where `fastmcp` and `mcp[cli]` are in `dependencies`.
- **What:** using the connectors as a library installs the MCP server stack too. 0.1.4 crashes at startup when `mcp` 2.x is installed ([#152](https://github.com/openags/paper-search-mcp/issues/152), open). Main pins `mcp<2`, which can clash with other packages in the same environment, and [#156](https://github.com/openags/paper-search-mcp/pull/156), which would support both, has no response.
- **Evidence:** `pyproject.toml` at `cab1b5c`; the issue and pull request, read 2026-11-07.
- **Suggested fix:** move the server's dependencies to an extra, such as `paper-search-mcp[server]`.
- **Raised upstream:** no.

## Live-network probes mixed into unit test files

- **Where:** 14 test files define an accessibility probe that sends a real request, such as `tests/test_crossref.py:6-13` (`requests.get("https://api.crossref.org/works?sample=1")`, called from `setUpClass` at lines 17-18). `tests/test_semantic.py:73` runs its probe inside `@unittest.skipUnless(...)`, so the request goes out while the module is being collected, even when its tests are filtered out.
- **What:** each of these files mixes offline tests (parsing, filtering, headers) with live searches. CI runs only an explicit list of "deterministic tests" (`.github/workflows/ci.yml`, the "Run deterministic tests" step), which leaves out these 14 files, so their offline tests never run in CI either. A plain `pytest` contacts about a dozen services. That counts against those services' limits, makes runs depend on the network, and gets skips that look like passes when a service is down.
- **Evidence:** the test files and CI workflow, read at `cab1b5c`. After paper-search-mcp was chosen, the test files for arXiv, Crossref, OpenAlex, OpenAIRE, Semantic Scholar and Zenodo were run against a patched copy, at the developer's request, with every non-local connection and DNS lookup refused at the socket. The offline tests passed, and the 20 live tests skipped, after 16 refused probe attempts. So the split is cheap to make explicit, and it isn't load-bearing.
- **Suggested fix:**
  - Mark live tests `@pytest.mark.network`, skipped unless they're asked for (an `--run-network` option or an environment variable in `conftest.py`).
  - Move each probe into a session-scoped fixture so nothing runs at import time.
  - Then run every test file in CI, and the network tests on a schedule.

  CONTRIBUTING already asks contributors to "call out live-network validation separately from mocked tests", so this makes the existing policy mechanical. Recorded responses (for example with pytest-recording or VCR.py) would give the parsers offline coverage too, but that is optional.
- **Raised upstream:** no.

## A shadow-library connector ships by default

- **Where:** `academic_platforms/sci_hub.py`.
- **What:** a Sci-Hub connector is part of the package. Main makes it opt-in ([#115](https://github.com/openags/paper-search-mcp/pull/115)), but PyPI's 0.1.4 still falls back to it by default, and pull requests adding Anna's Archive ([#52](https://github.com/openags/paper-search-mcp/pull/52)) and Sci-Hub mirror discovery ([#70](https://github.com/openags/paper-search-mcp/pull/70)) are open. The skill never uses shadow libraries, so the harvester must not call these connectors and blocks their hosts.
- **Evidence:** the file at `cab1b5c`; the pull requests, read 2026-11-07.
- **Suggested fix:** none proposed upstream; this is a policy difference, recorded so the harvester's block list stays deliberate.
- **Raised upstream:** not applicable.
