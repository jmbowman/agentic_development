# Prior art: generated views and queries over Markdown frontmatter (2026-11-19)

- **Effort:** full method, because the result backs the knowledge base's generated indexes and the docs site's backlog views, which every template's repos would inherit.
- **Already known:** [insitu](https://github.com/marcusinthesky/insitu) was the starting candidate. The developer knew of no other tool in this space and had dismissed none. The developer added the docs-site use: generated views of the backlog (the agents' and the developer's ready queues, and views Backlog.md's web view can't show), possibly through an mdBook preprocessor.

## Need and criteria

| Requirement | Underlying need |
|---|---|
| Views written into Markdown between comment markers | Index pages, tables and ranked lists that people and agents read without running a tool. Writing into the file is one means; rendering them when the docs site is built is another |
| SQL over frontmatter | Filter, sort, group and join across many files' frontmatter, nested lists included. SQL is one query language among several |
| A check that fails CI when a view is stale | No view is ever silently out of date: either a check gates a tracked view, or the view is computed whenever it is read |
| Writes only its own regions | The files a view reads are never rewritten. The task tracker computes its views on read and never writes task files (HLD tenet 10), so there a tool may only read |

Common uses, as the task and the developer gave them:

1. Generated indexes in the knowledge base, such as an index of decision documents (AD-264).
2. Views of the backlog in the docs site: the ready queues for agents and for the developer, and other views of task data (AD-326).
3. Ad-hoc queries over task and note frontmatter.

**Hard criteria:**

1. An OSI-approved license, compatible with use as an installed tool.
2. Runs locally, with no hosted service.
3. Markdown files stay the source of truth. The tool writes only its own output or marked regions of other files, and it never writes task files.
4. Coexists with mdBook and LID: no second navigation hierarchy, and no formatter that rewrites documents outside marked regions.

**Preferences:** pinnable through mise and updatable by Renovate; an mdBook integration, or output a preprocessor can insert; a CI staleness check; nested YAML; maintenance and maturity.

## Verdict

**Blend: insitu for tracked generated indexes and ad-hoc SQL, plus a small custom mdBook preprocessor that inserts the task tool's own views when the site is built.**

- **Knowledge-base indexes (use 1):** [insitu](https://github.com/marcusinthesky/insitu) writes SQL views over frontmatter between its markers, and `insitu check` fails CI when one is stale. [mdsmith](https://github.com/jeduden/mdsmith)'s `<?catalog?>` is the fallback if insitu stalls in alpha.
- **Ad-hoc queries (use 3):** `insitu sync` leaves its SQLite index, with a `documents` view, at a configured path, so `sqlite3` can query it with no second tool.
- **Backlog views in the docs site (use 2):** no tool found computes the tracker's readiness and ranking. Re-expressing them in SQL would make a second reader of the task format, which AD-326 rules out. The custom piece is the preprocessor AD-326 already plans: it runs the task tool and inserts its Markdown output at build time, and writes no tracked file. It borrows [mdbook-cmdrun](https://github.com/FauconFan/mdbook-cmdrun)'s marker (`<!-- cmdrun <command> -->`) and fixes its failure mode: a failing command must fail the build rather than put an error message into the page.

One choice is the developer's: whether a knowledge-base index is a **tracked file**, kept current by `insitu check` and readable on GitHub, or is **computed when read**, at site build or by a SessionStart hook as AD-264 plans. HLD tenet 10 favours computing on read, and the task-tracker design rejected a tracked board because every status change would modify a second file. A tracked index changes only when a decision doc is added or retitled, and the check stops it drifting. The recommendation is a tracked index for pages that agents and GitHub readers navigate by, and computing on read for everything else.

## Candidates and matrix

Ranked shortlist:

1. **[insitu](https://github.com/marcusinthesky/insitu)**: SQL over every file's frontmatter, marker regions, an in-memory `check`, and a persistent index for ad-hoc queries. It covers uses 1 and 3 by itself. It ranks first despite being alpha (0.2.0-rc.2). A stalled project, or breaking changes to its marker or model formats, would move mdsmith up.
2. **[mdsmith](https://github.com/jeduden/mdsmith)**: a mature, MIT-licensed Markdown linter whose `<?catalog?>` builds an index from frontmatter with CUE filters, and whose `check` gates CI. It ranks second because it brings about 70 lint rules that overlap the repo's other Markdown checks, all of which must be turned off one by one, and it has no joins. If the repo adopted it as its Markdown linter anyway, it would rank first.
3. **[mdbook-cmdrun](https://github.com/FauconFan/mdbook-cmdrun)**: inserts any command's output when the book is built, so the view can't go stale and no file is tracked. It ranks third because it is built against mdBook 0.4, which 0.5 says preprocessors must migrate from. A failing command also puts an error message into the page instead of failing the build. A 0.5 release that fails the build would make it the preprocessor to adopt instead of building one.
4. **[mq](https://github.com/harehare/mq)**: a jq-like Markdown query CLI that reads frontmatter across files and prints Markdown tables. It is a candidate for the query layer in front of a preprocessor, not verified in source.
5. **[DuckDB's yaml extension](https://github.com/teaguesterling/duckdb_yaml)**: `read_yaml_frontmatter` gives full SQL over a glob of files. It ranks below mq because the extension is installed from DuckDB's community repository when it runs, so it can't be pinned.
6. **Marker-region refreshers over any command:** [cmdsync](https://github.com/ndonfris/cmdsync) (`check` exits 1), [mdsh](https://github.com/zimbatm/mdsh) (`--frozen`) and [cog](https://github.com/nedbat/cog) (`--check`). Each could pair with a query CLI in place of insitu, at the cost of a second tool.

| Candidate | Class | License (file at commit) | Reason |
|---|---|---|---|
| [insitu](https://github.com/marcusinthesky/insitu) | build on | MIT (`LICENSE` at 9d53ca5, read whole) | SQL views written into marker regions, CI check, persistent SQLite index; alpha |
| [mdsmith](https://github.com/jeduden/mdsmith) | build on (fallback) | MIT (`LICENSE` at 28af6a9, read whole; appends the MIT notices of vendored `internal/punkt/` and goldmark code, with no added terms) | `<?catalog?>` with CUE filters and `check`; a whole linter to configure around |
| [mdbook-cmdrun](https://github.com/FauconFan/mdbook-cmdrun) | borrow ideas | MIT (`LICENSE` at 746f6f6, read whole) | Build-time command output; needs migrating to mdBook 0.5, and failures don't fail the build |
| [mq](https://github.com/harehare/mq) | build on (alternative query layer) | MIT (`LICENSE` at 96964f3, read whole by a subagent) | Frontmatter queries across files with Markdown table output; docs only |
| [DuckDB yaml extension](https://github.com/teaguesterling/duckdb_yaml) | borrow ideas | MIT (`LICENSE` at c619d85, read whole) | Full SQL over frontmatter globs; the extension can't be pinned |
| [cmdsync](https://github.com/ndonfris/cmdsync) | borrow ideas | MIT (`LICENSE.md` at 54f307d, subagent) | Command output in regions, with a `check`; v0.1.2, single maintainer |
| [mdsh](https://github.com/zimbatm/mdsh) | borrow ideas | MIT (`LICENSE` at eca79da, subagent) | `--frozen` CI check; last release 2022 |
| [cog](https://github.com/nedbat/cog) | borrow ideas | MIT (`LICENSE.txt` in cogapp 3.6.1, subagent) | Python generators between markers, with `--check` |
| [mdt](https://github.com/ifiokjr/mdt) | borrow ideas | Unlicense (subagent) | Provider/consumer blocks with `check`; data comes from `mdt.toml`, not frontmatter |
| [MarkdownDB](https://github.com/datopian/markdowndb) | reject | MIT (subagent) | Indexes into SQLite but writes no views; insitu covers the same ground |
| [rootline](https://github.com/pablontiv/rootline) | reject | Apache-2.0 (subagent) | Query-time aggregates only; `fix` and `migrate` rewrite source frontmatter |
| [mdbasequery](https://github.com/intellectronica/mdbasequery), [obaq](https://github.com/knu/obaq) | borrow ideas | MIT / BSD-2-Clause (subagent) | Obsidian Bases queries outside Obsidian; no markers or check |
| [embedoc](https://github.com/foo-ogawa/embedoc) | reject | MIT (subagent) | Regions over data sources, but nothing reads frontmatter across files, and no check mode |
| [sqlfence](https://github.com/ahojukka5/enkeksi) | borrow ideas | MIT (subagent) | SQL code blocks rendered as tables, with `--check`; no frontmatter source |
| [sensemaking](https://github.com/kmalakoff/sensemaking) | reject | MIT (subagent) | Ad-hoc SQL over frontmatter, links and tags; Node 22 and no views |
| [fmql](https://github.com/buyuk-dev/fmql) | reject | MIT (subagent) | Cypher-style queries; no views; adds a second query language |
| [mdbook-content-collections](https://github.com/saylesss88/mdbook-content-collections) | borrow ideas | Apache-2.0 (subagent) | Writes all chapters' frontmatter to JSON at build time; no rendering |
| [mdbook-tera](https://github.com/avitex/mdbook-tera) | reject | MIT (subagent) | Templates over a JSON or TOML file, built against mdBook 0.4 |
| [MDQL](https://github.com/mdql-db/mdql) | reject | AGPL-3.0 or commercial, plus a contributor CLA that assigns copyright and a trademark reservation (`LICENSE.md` at e1f1a94) | `INSERT`, `UPDATE` and `ALTER` rewrite files; schema files required |
| [GroundDB](https://github.com/JustMaier/groundDb) | reject | MIT (manifest only) | Path templates move source files when fields change |
| [krafna](https://github.com/7sedam7/krafna) | reject | unverified: MIT in `Cargo.toml` only | SQL-like but no joins, grouping or limits |
| [markdown-magic](https://github.com/DavidWells/markdown-magic) | reject | unverified: MIT in `package.json` only, no license file | No frontmatter source and no failing check |
| [Backlog.md](https://github.com/MrLesk/Backlog.md) `board export` | reject | MIT (subagent) | Fixed board format, written into the repo's README or `Backlog.md`, which the tracker's rules forbid |
| [querymatter](https://github.com/stevenwcarter/querymatter) | reject | none: no license file or field (listing by a subagent) | No license |

About 110 further tools were seen and judged not serious. Most are Obsidian-only plugins, frontmatter get/set or filter CLIs, agent-memory SQLite indexes, mdBook preprocessors with no data source, or marker tools that embed only whole files. The subagent records in the run's scratch directory list them.

Matrix (✓ native, ◐ partial, ⊕ extensible, ✗ unsupported, ? unverified):

| Criterion | insitu | mdsmith | mdbook-cmdrun | mq | DuckDB yaml |
|---|---|---|---|---|---|
| H1 OSI license | ✓ MIT | ✓ MIT | ✓ MIT | ✓ MIT | ✓ MIT |
| H2 local | ✓ | ✓ | ✓ | ✓ | ◐ extension fetched from DuckDB's repository on first use |
| H3 writes only its regions | ✓ regions, plus a `generated:` key only in files that opt in (`document.rs:72-93,295-323`) | ✓ when only `catalog` is enabled (`checker.go:52-70`) | ✓ in memory (`main.rs:32-48`) | ◐ `-i` rewrites its inputs; read-only without it (docs) | ✓ read-only |
| H4 coexists with mdBook and LID | ✓ HTML comment markers | ◐ `<?catalog?>` processing instructions render on GitHub, not checked in mdBook; the linter must be confined | ✓ is an mdBook preprocessor | ✓ | ✓ |
| Use 1: KB indexes | ✓ SQL models (`index.rs:216-234`) | ✓ glob, sort, CUE `where` (docs) | ⊕ with a query CLI | ⊕ with a preprocessor or region tool | ⊕ with a preprocessor or region tool |
| Use 2: backlog views at site build | ✗ no stdout output (`main.rs:43-79`) | ✗ | ⊕ runs the task tool | ⊕ | ⊕ |
| Use 3: ad-hoc queries | ◐ `sqlite3` on the state index (`index.rs:59-66`) | ◐ `list query` with CUE (docs) | ✗ | ✓ (docs) | ✓ (`yaml_frontmatter.cpp:184-311`) |
| CI staleness check | ✓ in memory, exit 1 (`main.rs:16-19,61-68`, `project.rs` `apply`) | ✓ `check` (docs) | ✓ computed at build | ◐ `--diff` exits 1 (docs) | n/a |
| Nested YAML | ✓ frontmatter stored as JSON (`index.rs:244`) | ◐ `row` uses scalars; `row-expr` needs CUE | n/a | ? | ✓ (docs) |
| Pinnable (mise, Renovate) | ✓ GitHub release binaries and crates.io, prereleases only | ✓ mise listed (docs) | ✓ cargo | ✓ cargo, brew (subagent) | ◐ DuckDB is; the extension isn't |
| Maturity | ◐ alpha; Rust engine since 2026-10 | ✓ v0.57, frequent releases | ◐ last push 2025-08 | ✓ active (subagent) | ✓ active |

**Blends considered.** insitu with mdbook-cmdrun reaches uses 1 to 3 with no custom code, but cmdrun is pinned to mdBook 0.4 and renders failures into the page. A query CLI (mq or DuckDB) with cmdsync covers use 1 like insitu, using two tools in place of one. insitu with the custom preprocessor (the verdict) adds only the piece AD-326 already plans.

**Scenario walk** (insitu and the preprocessor):

1. *The decision index (use 1).* A region in the decision index page runs a model over `docs/decisions/` and `docs/intent/*/decisions/`, selecting the path and `title` (or the H1 when `title` is missing). `insitu check` in prek and CI fails when a doc is added and the index isn't synced. If tracked indexes are declined, AD-264's hook computes the same list on read.
2. *The ready queues in the docs site (use 2).* A docs page holds `<!-- tasks: next --for agent -->`. At build, the preprocessor runs the task tool with links relative to the site, inserts the Markdown, and fails the build on a non-zero exit. No tracked file changes when a task's status does.
3. *An ad-hoc question (use 3).* "Open spikes by milestone": after `insitu sync`, run `sqlite3 .insitu/index.db "select milestone, count(*) from documents where type = 'spike' and status != 'Done' group by 1"`. `references` and other lists are JSON, readable with `json_each`.
4. *A fresh CI clone.* `insitu check` builds its index in memory (`index.rs:59-61`), so CI needs no state file, only the pinned binary.
5. *A malformed task file.* One file with invalid YAML frontmatter makes the whole insitu run fail (`index.rs:129-134`, `document.rs:111-113`), so CI fails loudly. The task tool's own lint reports the same file. mdsmith would treat the frontmatter as absent instead.
6. *An automated upgrade.* insitu publishes only prereleases so far. Renovate's handling of prerelease tags for a mise `github:` tool needs checking when insitu is pinned.

## Limitations checked in source

Verified:

- insitu indexes each selected Markdown file's frontmatter as JSON, and builds a `documents` view with one column per top-level key extracted by `json_extract`. *Verified in source (`crates/insitu-core/src/index.rs:19-28,216-234,244` at 9d53ca5)*
- insitu's models are read-only `SELECT` or `WITH` queries under an SQLite authorizer that denies writes and `load_extension`. *Verified in source (`index.rs:141-158,288-300` at 9d53ca5)*
- insitu writes only between its markers. It adds values to frontmatter only under `/generated/`, and only for files that declare `insitu.materializations`, through a lossless YAML editor. *Verified in source (`document.rs:72-93,264-282,295-372` at 9d53ca5)*
- `insitu check` builds its index in memory, writes nothing, and exits 1 when any view is stale. *Verified in source (`index.rs:59-66`, `crates/insitu/src/main.rs:16-19,61-68`, `crates/insitu-core/src/project.rs` `apply` at 9d53ca5)*
- insitu has no command that prints a view to standard output. Its commands are `init`, `sync`, `check`, `watch` and `extension`. *Verified in source (`main.rs:43-98` at 9d53ca5)*
- One file with invalid YAML frontmatter fails the whole insitu run. *Verified in source (`index.rs:129-134`, `document.rs:111-113` at 9d53ca5)*
- insitu's published versions are 0.2.0-rc.1 and rc.2 on crates.io, and v0.2.0-rc.2 on GitHub with Linux, macOS and Windows binaries. *Read from the crates.io sparse index and the GitHub release assets (2026-11-19)*
- mdsmith's `fix` applies only the rules enabled in the effective config. *Verified in source (`internal/fix/fix.go:164-174`, `internal/checker/checker.go:52-70` at 28af6a9)*
- mdsmith's `check` and `fix` have no flag that selects a single rule; their flag tables list none. *Listing (`docs/reference/cli/check.md:36-47`, `fix.md:30-39` at 28af6a9)*
- mdbook-cmdrun puts a failing command's error message into the page and returns success, even with `--strict`, so the build doesn't fail. *Verified in source (`src/cmdrun.rs:167-280` at 746f6f6)*
- mdbook-cmdrun depends on mdbook 0.4 and only warns when mdBook's version differs. *Verified in source (`Cargo.toml`, `src/main.rs:32-48` at 746f6f6)*
- DuckDB's `read_yaml_frontmatter` takes a glob and the options `as_yaml_objects`, `content` and `filename`. *Verified in source (`src/yaml_frontmatter.cpp:15-30,184-311` at c619d85)*

Docs only:

- mdBook 0.5 says preprocessors and renderers must be migrated from 0.4 to keep working. *Docs only (mdBook `CHANGELOG.md:122`, master, read 2026-11-19)*
- mdsmith's catalog takes a glob, a sort key, a CUE `where` filter and row templates, and treats invalid frontmatter as absent. *Docs only (`internal/rules/MDS019-catalog/README.md` at 28af6a9)*
- mq aggregates frontmatter across files with `-A` and exits 1 with `-U --diff` when anything would change. *Docs only (README at 96964f3)*

Could not verify:

- Whether mdbook-cmdrun 0.7.3 runs under mdBook 0.5 at all; nothing was installed or run.
- mq's frontmatter handling and its nested YAML, beyond its README.
- How Renovate treats insitu's prerelease tags.
- The licenses of readb and markbase: no repository was found.

## Coverage ledger

| Route | State | Queries or reason |
|---|---|---|
| The stack itself | searched | `mise.toml` (no Markdown query or region tool; Backlog.md 1.55.3 pinned); `scripts/tasks.py` (`board` writes Markdown, with no machine-readable output); the task-tracker design (the board is printed on demand, not tracked) |
| Earlier notes and decisions | searched | `docs/prior-art/` grepped for insitu, dataview, markdown-magic, cog, sqlite and frontmatter queries; no earlier note covers the topic. The knowledge-base note's blend and the task-tracker design were read |
| GitHub repository search | searched | 67 queries: round 1 had 16 wordings, each run twice (sorted by stars, and pushed after 2025-11-19 sorted by update time), such as "frontmatter sql", "markdown frontmatter query", "markdown generated section", "readme auto update", "mdbook preprocessor command", "dataview cli", "markdown sqlite"; rounds 2-4 had 21 star-sorted wordings. One secondary rate limit was waited out and the affected queries rerun |
| GitHub topics | searched | 16 topic-name lookups (frontmatter, markdown, mdbook, dataview, codegen and candidate names) and 22 `topic:` searches |
| GitHub code search | searched | 13 README searches naming krafna, mdsh, markdowndb, mdbook-cmdrun, embedme and cmdsync, and marker syntaxes |
| LibHunt | searched | `/r/markdown-magic` (unrelated alternatives); `/r/insitu` (404) |
| GitLab search | searched | "frontmatter query", "frontmatter sql", "markdown frontmatter index", "mdbook preprocessor", "dataview", `topic=frontmatter`, "markdown generated sections" |
| Codeberg search | excluded | Blocks scripted clients; searched through web search: `site:codeberg.org markdown frontmatter query`, `site:codeberg.org markdown generated index comment markers` (only Forgejo mirrors returned) |
| npm | searched | 20 wordings, such as "frontmatter sql", "markdown query frontmatter", "markdown comment blocks generate", "dataview cli", `keywords:frontmatter query`, "embedme" |
| PyPI | searched | Search page not requested; `site:pypi.org` web searches ("markdown frontmatter sqlite", "markdown generated sections between comment markers"); JSON lookups of fmql, frontmatter-mcp, markdown-to-sqlite, cogapp, mdsmith and sqldown |
| crates.io | searched | 23 API queries, such as "frontmatter", "mdbook preprocessor command", "markdown query", "markdown sqlite", `keyword=mdbook-preprocessor`, "readme sync check"; 31 crate archives read |
| libraries.io | searched | 20 queries (8 PyPI-only, 12 across platforms), such as "frontmatter sql", "markdown exec", "front matter query cli" |
| ecosyste.ms | searched | Keywords frontmatter, front-matter, mdbook-preprocessor, markdown-generator, dataview, markdown-database |
| Homebrew formulae | searched | Regex over names and descriptions for frontmatter, Markdown query, SQL, generation, TOC, index and database, mdbook, dataview and obsidian; only mq/mdq and TOC tools |
| AUR | searched | "frontmatter", "mdbook", "markdown query", "markdown sql" |
| Awesome lists | searched | "awesome markdown tools", "awesome obsidian dataview alternatives"; mdBook's third-party plugin wiki page and awesome-markdown read in full |
| alternativeto.net | searched (through web search) | "alternatives to markdown-magic", "alternatives to MarkdownDB", "krafna alternatives", "cog alternative rust"; no request to the site |
| General web search | searched | 30 queries, such as "query markdown frontmatter with SQL", "dataview outside obsidian cli", "mdbook preprocessor run command insert output", "auto-update section of README between comment markers check CI", "duckdb markdown extension frontmatter", "obsidian bases render outside obsidian" |
| Cross-language equivalents | searched | "markdown-magic python equivalent", "cog alternative rust", "go CLI query markdown frontmatter", "python query obsidian vault frontmatter dataframe", "dataview serializer write results markdown comment markers" |
| Language registries | excluded | The need names no other language; Go tools were found through GitHub and web search |
| nixpkgs | excluded | Condition unmet: no brotli decompressor installed |
| lib.rs | excluded | Blocks scripted clients; crates.io searched instead |
| Hosted services | excluded | Hard criterion 2 requires running locally |
| Skill directories, plugin marketplaces, MCP Registry, PulseMCP, Anthropic's skills repo, skill awesome lists and topics | excluded | The need is a command-line tool, not an agent skill, plugin or MCP server |
| aitoolnet.com | excluded | Not an AI product or agent tool |
| Literature routes | excluded | Not a question about approaches, and the software routes found implementations of every requirement |

## Snowball rounds

1. Seed queries across all routes added insitu's neighbours: cog, mdsh, markdown-magic, cmdsync, embedoc, mdbook-cmdrun, mdbook-tera, mdbook-content-collections, mdsmith, mdt, MarkdownDB, krafna, mq, rootline, mdbasequery, MDQL, GroundDB, fmql, sensemaking and the Dataview-style CLIs.
2. Candidate names, topics and READMEs added DuckDB's yaml and markdown extensions, sqlfence, readb, markbase, markdown-to-sqlite, markmac and Backlog.md's board export.
3. Index and ADR generators, Bases evaluators and alternatives pages added obaq, markasten and markdown-inject.
4. Queries seeded by mdsmith, mdbook-cmdrun, cog and the Bases tools added nothing new on GitHub or in the registries. The web route ran four further rounds that added only frontmatter-mcp, obsidiantools and mdbasequery variants, and stopped when round 8 added none.

The search stopped because a round added no new serious candidate.

## Refresh trigger

- When insitu releases 0.2.0 final or 1.0, or goes six months without a release.
- When mdbook-cmdrun releases a version built for mdBook 0.5, or one that fails the build on a failing command.
- When the knowledge base's first generated index is built, or the docs-site preprocessor (AD-326) is designed.
