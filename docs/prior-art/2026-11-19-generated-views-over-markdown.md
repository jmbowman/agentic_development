# Prior art: generated views and queries over Markdown frontmatter (2026-11-19)

- **Effort:** full method, because the result backs the knowledge base's generated indexes and the docs site's backlog views, and every repo made from the template would inherit both.
- **Already known:** [insitu](https://github.com/marcusinthesky/insitu) was the starting candidate. The developer knew of no other tool in this space and had dismissed none. The scope covers generated views of the backlog in the docs site as well as knowledge-base indexes: the ready queues for agents and for the developer, and views that Backlog.md's web view can't show, possibly through an mdBook preprocessor. The developer has security concerns about [mdbook-cmdrun](https://github.com/FauconFan/mdbook-cmdrun) and noted that its mdBook 0.5 migration ([pull request 23](https://github.com/FauconFan/mdbook-cmdrun/pull/23), open since 2025-12-22) hasn't moved.

## Need and criteria

| Requirement | Underlying need |
|---|---|
| Views written into Markdown between comment markers | Index pages, tables and ranked lists that people and agents read without running a tool. Writing into a file is one means; rendering the view when the docs site is built is another |
| SQL over frontmatter | Filter, sort, group and join across many files' frontmatter, nested lists included. SQL is one query language among several |
| A check that fails CI when a view is stale | No view is ever silently out of date: either a check gates a tracked view, or the view is computed whenever it is read |
| Writes only its own regions | The files a view reads are never rewritten. The task tracker computes its views on read and never writes task files (HLD tenet 10), so there a tool may only read |

Terms used below: a **region** is the text between a tool's begin and end comment markers, which the tool rewrites and nothing else does. A **tracked** view is a region or file committed to git; a view **computed on read** is produced when someone reads it (at docs-site build, by a command, or by a session hook) and is never committed.

Common uses, as the task and the developer gave them:

1. **Use 1:** generated indexes in the knowledge base, such as an index of decision documents listed by their H1 titles.
2. **Use 2:** views of the backlog in the docs site: the ready queues for agents and for the developer, and other views of task data (AD-326).
3. **Use 3:** ad-hoc queries over task and note frontmatter.

**Hard criteria:**

1. An OSI-approved license, compatible with use as an installed tool.
2. Runs locally, with no hosted service.
3. Markdown files stay the source of truth. The tool writes only its own output or marked regions of other files, and it never writes task files.
4. Coexists with mdBook and LID: no second navigation hierarchy, and no formatter that rewrites documents outside marked regions.

**Preferences:** pinnable through mise and updatable by Renovate; an mdBook integration, or output a preprocessor can insert; a CI staleness check; nested YAML; maintenance and maturity.

## Verdict

**Blend: [mq](https://github.com/harehare/mq) as the query layer for all three uses, plus a small custom view tool that runs only an allowlist of view commands: as an mdBook preprocessor when the docs site is built, and, if index pages are tracked, as a command that writes the same views into committed pages and fails CI when one is stale.**

- **mq** reads a directory of Markdown files into records with each file's path, first heading, parsed frontmatter and body, and prints Markdown. That gives use 1 its H1 titles with no extra parsing, gives use 3 a query language, and gives the view tool Markdown to insert. mq grants no file, command or network access unless a flag allows it, so each view runs as `mq --allow-read=<folder>` and never with `--allow-run`.
- **The view tool** is the custom piece AD-326 already plans. It replaces `<!-- view: <name> -->` markers with the output of commands named in an allowlist in its configuration (the task tool's views and a few mq queries), never runs a command written in a page, and fails when a command exits non-zero. As an mdBook preprocessor it uses mdBook 0.5's protocol. It takes the marker idea from [mdbook-cmdrun](https://github.com/FauconFan/mdbook-cmdrun), and differs where cmdrun falls short: cmdrun runs any shell command written in any page, never fails the build when a command fails, and is built for mdBook 0.4. The region tools found, such as [cmdsync](https://github.com/ndonfris/cmdsync) and [mdsh](https://github.com/zimbatm/mdsh), share cmdrun's first flaw: the command is written in the page's own marker, so a check in CI would run whatever a committed page names.
- **Backlog views (use 2)** come from the task tool itself, never from SQL or mq over task files. AD-326 asks the docs-site spike to take what it needs from the task tool rather than from a second reader of the format, and the task-tracker design lists the tool output it needs (links relative to the site, a machine-readable output) as its open item 13. The tool computes readiness and ranking and applies its rules for archived tasks and outbox drafts, so it stays the one place those rules live.
- **Tracked index pages** wait on AD-331. If it rules for them, the view tool gets two more modes: `sync` writes each view between the markers of a committed page, and `check` fails prek and CI when a page is stale. A tracked index is an exception to HLD tenet 10, which says derived values are computed when read, not written into files, so the ruling also rewords that tenet. If AD-331 rules against tracked indexes, the views appear only on the built site.
- **AD-264's SessionStart hook stays either way.** Its job is to put decision titles into the agent's context at session start, because agents tend to skip a page they're only pointed to; a page, tracked or built, doesn't do that. The hook can run the same allowlisted mq view.

[insitu](https://github.com/marcusinthesky/insitu) fits tracked SQL views best of everything found, and runs no command written in a page, but it is about ten weeks old, with one maintainer, five commits and one release candidate, so it is held as the replacement for mq and the view tool's `sync` and `check` modes if it matures.

## Candidates and matrix

The blend's member comes first; the rest are ranked by how well each covers the three uses on evidence verified in source, then by maturity, then by whether it runs commands written in a page:

1. **[mq](https://github.com/harehare/mq)**: verified in source; covers use 1 (H1 titles and frontmatter per file) and use 3, and prints Markdown the view tool can insert. Its sandbox flags let each view read one folder and run nothing. Mature: 21 months old, about 1,080 stars, frequent releases, one main maintainer. A release that changes `collection()`, or a need for SQL joins that its language can't express, would move insitu or DuckDB up.
2. **[insitu](https://github.com/marcusinthesky/insitu)**: verified in source; SQL views over every file's frontmatter, written into regions, with an in-memory `check`, so one tool covers tracked indexes and their CI gate without running commands from pages. Ranked below mq for maturity alone: first commit 2026-09-06, one contributor, five commits, one prerelease, one star. A 0.2.0 final release and a few months of activity would make it the tracked-index tool in place of mq and the view tool's `sync` and `check` modes.
3. **[mdsmith](https://github.com/jeduden/mdsmith)**: verified in source; its `<?catalog?>` builds an index from frontmatter fields with CUE filters, `check` gates CI, and `export --fix` prints a page with its catalogs regenerated, which the view tool could insert. Its lint rules can be switched off by category, so the catalog can run alone. It ranks below insitu because a catalog row reads only frontmatter fields, so a decision index of H1 titles would need a `title` key in every decision doc, and because it has had no release since its 0.58 release candidates of 2026-10-04. Decision docs gaining `title` frontmatter, and releases resuming, would make it a one-tool alternative for tracked indexes.
4. **[DuckDB's yaml extension](https://github.com/teaguesterling/duckdb_yaml)**: verified in source; `read_yaml_frontmatter` gives full SQL over a glob of files. It ranks below mdsmith because it reads no H1 and has no view or check of its own, and its extension is installed separately from DuckDB's community repository (`INSTALL yaml FROM community`), so the extension's version isn't pinned on its own. A use 3 that needs SQL joins across folders would make it the ad-hoc tool.
5. **[mdbook-cmdrun](https://github.com/FauconFan/mdbook-cmdrun)**: verified in source; inserts any command's output at build. It ranks last of the verified candidates: it runs arbitrary shell from any page, a failing command never fails the build, and it targets mdBook 0.4, with the 0.5 migration open in [pull request 23](https://github.com/FauconFan/mdbook-cmdrun/pull/23) since 2025-12-22. A release on mdBook 0.5 with a failing-build mode and a command allowlist would make it the preprocessor to adopt instead of building one.
6. **[cmdsync](https://github.com/ndonfris/cmdsync)**: refreshes regions from a command's output, and `check` exits 1 when one is stale; the idea behind the view tool's `sync` and `check` modes. Not verified in source. The command is written in each region's marker, so a CI check runs whatever a page names; a marker that named an allowlist entry instead would make it a candidate for those modes.
7. **[mdsh](https://github.com/zimbatm/mdsh)**: `--frozen` fails CI when a region would change. Not verified in source. Like cmdsync, it runs `$ command` lines written in the page, and its last release is from 2022, though the repository was active in 2026-10.
8. **[cog](https://github.com/nedbat/cog)**: `--check` fails when generated text is stale, but the generator is Python code written inside the marker comments, so every index carries a program. It would rank higher only for views that need logic mq can't express.

`(subagent)` in the license column means a search subagent read the license file in full; other licenses were read again for this note. Where a candidate has no license file, the license is read from its package manifest, as the skill's order allows, and the row says so.

| Candidate | Class | License (file at commit) | Reason |
|---|---|---|---|
| [mq](https://github.com/harehare/mq) | build on | MIT (`LICENSE:1-21` at 54c8c33) | Query layer for all three uses; Markdown output |
| [insitu](https://github.com/marcusinthesky/insitu) | build on (held until it matures) | MIT (`LICENSE:1-21` at 9d53ca5) | SQL views written into regions, CI check; too young to depend on |
| [mdsmith](https://github.com/jeduden/mdsmith) | borrow ideas | MIT (`LICENSE` at 28af6a9; appends the MIT notices of vendored `internal/punkt/` and goldmark code, with no added terms) | Catalog of frontmatter fields with CUE filters, `check` and `export --fix`; no H1 titles; inactive since 2026-10-04 |
| [cmdsync](https://github.com/ndonfris/cmdsync) | borrow ideas | MIT (`LICENSE.md` at 54f307d, subagent) | Regions refreshed from command output, with `check`; the command is written in the page |
| [mdsh](https://github.com/zimbatm/mdsh) | borrow ideas | MIT (`LICENSE` at eca79da, subagent) | `--frozen` CI check; runs commands written in the page; last release 2022 |
| [DuckDB yaml extension](https://github.com/teaguesterling/duckdb_yaml) | borrow ideas | MIT (`LICENSE:1-21` at c619d85) | Full SQL over frontmatter globs; extension version not pinned on its own |
| [mdbook-cmdrun](https://github.com/FauconFan/mdbook-cmdrun) | borrow ideas | MIT (`LICENSE` at 746f6f6) | Marker idea for the view tool; arbitrary shell, failures never fail the build, mdBook 0.4 |
| [cog](https://github.com/nedbat/cog) | borrow ideas | MIT (`LICENSE.txt` at c42137c) | `--check`; generators are Python in the markers |
| [mdt](https://github.com/ifiokjr/mdt) | borrow ideas | Unlicense (`license` on main, 2026-11-19, subagent) | Provider/consumer blocks with `check`; data from `mdt.toml`, not frontmatter |
| [sqlfence](https://github.com/ahojukka5/enkeksi) (repository still named `enkeksi`) | borrow ideas | MIT (`LICENSE` at 77c00f1, subagent) | SQL code blocks rendered as tables, with `--check`; no frontmatter source |
| [mdbasequery](https://github.com/intellectronica/mdbasequery) | borrow ideas | MIT (`LICENSE` at ea25303, subagent) | Obsidian Bases queries without Obsidian; output to a file, no regions or check |
| [obaq](https://github.com/knu/obaq) | borrow ideas | BSD-2-Clause (`LICENSE` at 3381472, subagent) | Evaluates Bases code blocks in a file and prints the file with tables in their place; no check |
| [mdbook-content-collections](https://github.com/saylesss88/mdbook-content-collections) | borrow ideas | Apache-2.0 (`LICENSE` at e80513c, subagent) | Writes every chapter's frontmatter to JSON at build; no rendering |
| [MarkdownDB](https://github.com/datopian/markdowndb) | reject | MIT (`LICENSE` at f53cfef, subagent) | Indexes into SQLite but writes no views. The same commit is also reachable as `flowershow/markdowndb` |
| [rootline](https://github.com/pablontiv/rootline) | reject | Apache-2.0 (`LICENSE` at 79c6149, subagent) | Query-time aggregates only; `fix` and `migrate` rewrite source frontmatter |
| [embedoc](https://github.com/foo-ogawa/embedoc) | reject | MIT (`LICENSE` at 79fe0c2, subagent) | Regions over data sources, but no source reads frontmatter across files, and no check mode |
| [sensemaking](https://github.com/kmalakoff/sensemaking) | reject | MIT (`package/LICENSE` in npm 0.28.2, subagent) | Ad-hoc SQL over frontmatter, links and tags; needs Node 22; no views |
| [fmql](https://github.com/buyuk-dev/fmql) | reject | MIT (`LICENSE` at 89ff1e0, subagent) | Cypher-style queries; no views; a second query language beside mq |
| [mdbook-tera](https://github.com/avitex/mdbook-tera) | reject | MIT (`LICENSE` at bcf31d7, subagent) | Templates over a JSON or TOML file; built against mdBook 0.4 |
| [md-frontmatter-index](https://github.com/ForkTheGhost/md-frontmatter-index) | reject | MIT (`LICENSE` at 39468ed, subagent) | A script that writes whole index files from frontmatter; not packaged, no check |
| [MDQL](https://github.com/mdql-db/mdql) | reject | AGPL-3.0 or commercial, plus a contributor CLA that assigns copyright and a trademark reservation (`LICENSE.md` at e1f1a94) | `INSERT`, `UPDATE` and `ALTER` rewrite files; schema files required |
| [GroundDB](https://github.com/JustMaier/groundDb) | reject | MIT (`LICENSE` at c36dd24, subagent) | Path templates move source files when fields change |
| [krafna](https://github.com/7sedam7/krafna) | reject | MIT (`Cargo.toml` license field at ab3823e; no license file) | SQL-like, but no joins, grouping or limits |
| [markdown-magic](https://github.com/DavidWells/markdown-magic) | reject | MIT (`packages/core/package.json` license field at f6cd8c0; no license file in the tree) | No frontmatter source and no failing check |
| [Backlog.md](https://github.com/MrLesk/Backlog.md) `board export` | reject | MIT (`LICENSE` at b461c98, subagent) | Fixed board format written to a file; the task-tracker design forbids agents running it |
| [querymatter](https://github.com/stevenwcarter/querymatter) | reject | none: no license file or license field (listing at 825557f, subagent) | No license |

The search records hold 55 distinct candidates. Those not in the table are frontmatter filter or get/set CLIs, Obsidian-only plugins, agent-memory indexes, mdBook preprocessors with no data source, and marker tools that embed only whole files; none addresses use 1 or use 2 better than a row above.

Matrix of the verified candidates (✓ native, ◐ partial, ⊕ extensible, ✗ unsupported, ? unverified). Each cell gives its source; "listing" means a search of the source whose scope is given.

| Criterion | [mq](https://github.com/harehare/mq) | [insitu](https://github.com/marcusinthesky/insitu) | [mdsmith](https://github.com/jeduden/mdsmith) | [mdbook-cmdrun](https://github.com/FauconFan/mdbook-cmdrun) | [DuckDB yaml](https://github.com/teaguesterling/duckdb_yaml) |
|---|---|---|---|---|---|
| H1 OSI license | ✓ MIT (`LICENSE`) | ✓ MIT (`LICENSE`) | ✓ MIT (`LICENSE`) | ✓ MIT (`LICENSE`) | ✓ MIT (`LICENSE`) |
| H2 local | ✓ a single binary (README install section) | ✓ native binary (README "What it does") | ✓ single binary (README install section) | ✓ preprocessor binary (`src/main.rs:11-20`) | ◐ DuckDB is local; the extension is installed from DuckDB's community repository (README:8-13) |
| H3 writes only its regions | ✓ writes files only with `-i`, `-o` or `--allow-write` (`crates/mq-run/src/cli.rs:582-609,776-796`) | ✓ regions, plus `/generated/` frontmatter only in files that opt in (`plan.rs:48-113`, `document.rs:295-372`) | ✓ with only the `directive` category on (`checker.go:52-70`, `config.go:77`) | ✓ the book is changed in memory (`src/main.rs:32-48`) | ✓ a read-only table function (`yaml_frontmatter.cpp:184-311`) |
| H4 coexists with mdBook and LID | ✓ a CLI, no navigation of its own (README) | ✓ HTML comment markers (`document.rs:9-15`) | ◐ `<?catalog?>` blocks: how GitHub and mdBook render them wasn't checked | ✓ an mdBook preprocessor | ✓ a CLI, no navigation of its own |
| Use 1: KB index by H1 | ✓ `collection()` gives path, first heading, frontmatter (`builtin.rs:5743-5782`) | ◐ `title` is frontmatter only; the H1 must be cut from `body` with SQL (`index.rs:257-261`) | ◐ frontmatter fields only (`MDS019-catalog/README.md` "Template fields") | ⊕ runs any query CLI (`src/cmdrun.rs:250-254`) | ◐ frontmatter and body, no heading (`yaml_frontmatter.cpp:15-20`) |
| Use 2: output a preprocessor can insert | ✓ prints Markdown (README output formats) | ✗ no command prints a view (listing: subcommands in `crates/insitu/src/main.rs:43-98`) | ✓ `export --fix` prints a page with its catalogs regenerated, leaving the source unchanged (`docs/reference/cli/export.md:1-30`, docs) | ✓ is the preprocessor | ◐ the DuckDB CLI's Markdown output mode (not checked) |
| Use 3: ad-hoc queries | ✓ (`builtin.rs:5942`, README) | ◐ `sqlite3` on the index `sync` leaves (`index.rs:59-66`) | ◐ `list query` with CUE (`docs/reference/cli/query.md`) | ✗ no query of its own (listing: `src/` at 746f6f6) | ✓ SQL (`yaml_frontmatter.cpp:408`) |
| CI staleness check | ◐ `-U --diff` previews a rewrite (`cli.rs:780-784`); in the blend, the view tool's `check` | ✓ in memory, exit 1 (`crates/insitu/src/main.rs:173-186`, `insitu-protocol/src/models.rs:319-323`) | ✓ `check` (`docs/reference/cli/check.md`) | ✓ computed at build | ✗ none (listing: README "Parameters"); computed when queried |
| Nested YAML | ✓ frontmatter parsed into a dict (`builtin.rs:5748-5756`) | ✓ stored as JSON (`index.rs:244`) | ◐ `row` takes scalars; `row-expr` needs CUE (`MDS019-catalog/README.md`) | ⊕ whatever the command reads | ✓ fields become columns merged across files, lists queryable with `list_contains` (README:211,233) |
| Malformed frontmatter | ◐ fails the whole `collection()` call (`builtin.rs:5750-5751,5922-5930`) | ◐ fails the whole run (`index.rs:129-134`, `document.rs:111-113`) | ✓ treated as absent (`MDS019-catalog/README.md` "Edge Cases") | ⊕ the command's behaviour | ? not found |
| Pinnable (mise, Renovate) | ✓ GitHub releases, cargo, brew (v0.10.2, 2026-11-20) | ◐ GitHub release binaries, crates.io and PyPI wheels, prereleases only | ✓ mise and GitHub releases (README:113) | ✓ cargo | ◐ DuckDB pinnable; the extension version is not |
| Maturity | ✓ first commit 2025-02, about 1,080 stars, one main maintainer | ✗ first commit 2026-09-06, one contributor, five commits | ◐ first commit 2026-02, pre-1.0, no release since 2026-10-04 | ◐ last push 2025-08-12; mdBook 0.5 migration open | ✓ active (commit 2026-11-12) |

Matrix of the other serious candidates, none verified in source. Sources are the candidates' own READMEs or docs as the search subagents read them, at full depth except where marked *snippet*; "? not found" means the README or docs read say nothing either way. Registry and forge figures are metadata read on 2026-11-19.

| Candidate | H1–H4 | Use 1 | Use 2 | Use 3 | CI check | Pinnable | Maturity |
|---|---|---|---|---|---|---|---|
| [cmdsync](https://github.com/ndonfris/cmdsync) | ◐ writes only regions, but runs the command its marker names (README "Features") | ⊕ runs any command, mq included (README) | ◐ regions in committed files, not at build (README) | ? not found: no query of its own in the README | ✓ `check` exits 1 (`src/cli.ts:52,84,140` at 54f307d, read by a subagent) | ✓ npm 0.1.2 (registry) | ◐ 0 stars, pushed 2026-11-03 (forge) |
| [mdsh](https://github.com/zimbatm/mdsh) | ◐ writes only its blocks, but runs `$ command` lines in the page (README:85-98 in crate 0.7.0) | ⊕ runs any command (README) | ◐ blocks in committed files (README) | ? not found in README | ✓ `--frozen` (README:37-41 in crate 0.7.0) | ✓ crates.io 0.7.0 (registry) | ◐ last release 2022-11-03; repository pushed 2026-10-13 (forge) |
| [cog](https://github.com/nedbat/cog) | ◐ writes only its regions, but runs the Python written in them (docs, *snippet*) | ⊕ Python generators in markers (docs, *snippet*) | ◐ regions in committed files (docs, *snippet*) | ? not found | ✓ `--check` (`cogapp/options.py:222` at c42137c) | ✓ PyPI 3.6.1 (registry) | ✓ release 2026-11-15 (registry) |
| [mdt](https://github.com/ifiokjr/mdt) | ✓ provider and consumer blocks only (docs) | ◐ data from `mdt.toml`, not frontmatter (docs) | ◐ blocks in committed files (docs) | ? not found in docs | ✓ `check` exits 1 (docs) | ✓ crates.io 0.9.8 (registry) | ✓ updated 2026-11-07 (registry) |
| [sqlfence](https://github.com/ahojukka5/enkeksi) | ✓ writes Markdown tables from SQL code blocks (README) | ◐ SQL over SQLite or DuckDB, not frontmatter (README) | ◐ tables in committed files, or a separate `--output` (README) | ◐ SQL, over a database rather than frontmatter (README) | ✓ `--check` (README) | ◐ 1.0.0 installs from git; 0.3.0 on PyPI under the old name (registry) | ? not found |
| [mdbasequery](https://github.com/intellectronica/mdbasequery) | ✓ writes only to `--out` (README) | ◐ Bases queries over frontmatter, no H1 (README) | ✓ `--format md` to stdout (README) | ✓ filter, sort, group (README) | ? not found in README | ✓ npm (registry) | ◐ 22 stars, pushed 2026-10-11 (forge) |
| [obaq](https://github.com/knu/obaq) | ✓ prints to stdout (README) | ◐ Bases code blocks evaluated over frontmatter, no H1 (README) | ✓ prints the page with tables in place of the blocks (README) | ✓ Bases queries (README) | ? not found in README | ? installed from a checkout (README) | ? not found |
| [mdbook-content-collections](https://github.com/saylesss88/mdbook-content-collections) | ✓ writes a JSON file into the built book (docs) | ◐ JSON of all chapters' frontmatter, no rendering (docs) | ◐ needs theme JavaScript to display (docs) | ? not found in docs | ✓ computed at build (docs) | ✓ crates.io 0.3.0 (registry) | ◐ release 2026-06-19 (registry) |

**Blends considered.** mq with the view tool as a preprocessor covers uses 1 to 3 with every view computed on read; the view tool's `sync` and `check` modes cover tracked index pages if AD-331 wants them. mq with cmdsync for tracked pages needs no `sync` or `check` code, but runs whatever command a committed page's marker names. insitu alone covers uses 1 and 3 and tracked indexes, and with the view tool covers use 2, but rests on a ten-week-old project. mdsmith with the view tool covers indexes only if decision docs gain `title` frontmatter. mdbook-cmdrun in place of the view tool needs no code, but brings arbitrary shell from any page and builds that pass when a command fails.

**Scenario walk.** The blend first, through the three uses:

1. *The decision index (use 1).* The decision folders are planned but don't exist yet: a project-level `docs/decisions/` and a `decisions/` folder in each segment under `docs/intent/`. The view runs `collection()` once per decision folder, never over all of `docs/intent/`, so malformed frontmatter in an LLD or spec file can't break it, and lists each doc's path and first heading. Computed on read, the view tool inserts it into the site's decision index page, and AD-264's hook prints the same list at session start. Tracked (if AD-331 says so), the view tool's `sync` writes it into the index page's region, and its `check` in prek and CI fails when a doc is added and the page isn't refreshed.
2. *The ready queues in the docs site (use 2).* A page holds `<!-- view: next-agent -->`. At build, the view tool looks up `next-agent` in its allowlist, runs the task tool, inserts the Markdown, and fails the build on a non-zero exit. No tracked file changes when a task's status does. Two prerequisites are open: the tool prints its views with links relative to the site (task-tracker open item 13), and `board` prints to standard output; today the pilot `scripts/tasks.py` writes a tracked `backlog/BOARD.md`, which the design replaces (TASK-REPO-008, still open).
3. *An ad-hoc question (use 3).* "Which open spikes cite a prior-art note": an mq query over `backlog/tasks/` filters on `type`, `status` and `references`, which arrive as a list. It reads raw frontmatter, so it doesn't apply the tracker's rules for archived tasks, outbox drafts or readiness; anything the task tool computes is asked of the tool.

Then the other verified finalists through the same uses:

- *insitu:* use 1 by an SQL model in a region, with the H1 cut from the `body` column; use 2 only through a tracked page, since nothing prints a view; use 3 by `sqlite3` on `.insitu/index.db` (gitignored). Its default `sources.include` is `**/*.md` (`config.rs:12`), so one malformed task file would fail the decision index's check too, unless `include` is narrowed to the index's inputs.
- *mdsmith:* use 1 only with `title` frontmatter in every decision doc; use 2 through `export --fix`, whose output the view tool could insert, for catalogs only, never the task tool's ranking; use 3 through `list query` with CUE.
- *DuckDB:* use 3 with full SQL, nested lists as typed columns; uses 1 and 2 only behind the view tool, without H1 titles.
- *mdbook-cmdrun:* use 2 by running the task tool from a page, but a failing tool leaves partial output in the page with the build green, any page can run any command, and it needs mdBook 0.4.

And through four change scenarios:

4. *A fresh CI clone.* mq is one pinned binary, and the view tool ships in this repo. Nothing needs state from an earlier run.
5. *A malformed task file.* An mq query over `backlog/tasks/` fails as a whole (`builtin.rs:5922-5930`), and the task tool's lint names the file. Views that don't read task files are unaffected, because each query reads only its own folders.
6. *A new view.* Adding "drafts waiting in the outbox" to the site is a new allowlist entry naming a task-tool command, plus a marker in a page; no new tool. A page that names a view missing from the allowlist fails the build.
7. *An automated upgrade.* Renovate updates mq's pinned version like any mise tool; a release that changes `collection()`'s record shape fails the site build or the view tool's `check`, which is where it should surface.

## Limitations checked in source

Verified:

- [mq](https://github.com/harehare/mq)'s `collection(dir, respect_gitignore)` walks a directory recursively, collects `.md` and `.markdown` files in sorted order, and returns one record per file with `path`, `title` (the first heading of any level), `frontmatter` (YAML or TOML parsed into a dictionary) and `content`. *Verified in source (`crates/mq-lang/src/runtime/builtin.rs:5743-5782,5814-5934,5942-5958` at 54c8c33)*
- mq fails the whole `collection()` call when any file's frontmatter is invalid YAML. *Verified in source (`builtin.rs:5750-5751,5922-5930` at 54c8c33)*
- mq's `collection()` is in the v0.10.2 release. *Verified in source (`builtin.rs:5942` at tag v0.10.2, read through the contents API)*
- mq's command line grants no file reads, file writes, network access or command execution unless a flag allows it: `collection()` needs `--allow-read` (which can name the folders allowed), and the `system` function needs `--allow-run`. *Verified in source (`crates/mq-run/src/cli.rs:582-609,716-735`, `builtin.rs:5714-5740` at 54c8c33)*
- [insitu](https://github.com/marcusinthesky/insitu) stores each selected file's frontmatter as JSON and builds a `documents` view with one column per top-level key, leaving out its own `insitu` and `generated` keys. *Verified in source (`crates/insitu-core/src/index.rs:19-28,91,216-234,244`, `document.rs:64-70` at 9d53ca5)*
- insitu's `title` column comes only from a frontmatter `title` key. *Verified in source (`index.rs:257-261` at 9d53ca5)*
- insitu's models are read-only `SELECT` or `WITH` queries under an SQLite authorizer that denies writes and `load_extension`. *Verified in source (`index.rs:141-163,288-300` at 9d53ca5)*
- insitu writes only between its markers, and into frontmatter only under `/generated/`, only in a file that opts in through `insitu.materializations` or a region whose `target` is a `/generated/` pointer, and only into that file. *Verified in source (`plan.rs:48-113,121-160`, `document.rs:72-93,264-282,295-372` at 9d53ca5)*
- `insitu check` builds its index in memory, writes nothing, and exits 1 when a view is stale (2 on an error). *Verified in source (`index.rs:59-66`, `crates/insitu/src/main.rs:173-186`, `crates/insitu-protocol/src/models.rs:319-323` at 9d53ca5)*
- insitu has no command that prints a view; its commands are `init`, `sync`, `check`, `watch` and `extension`. *Verified in source (`crates/insitu/src/main.rs:43-98` at 9d53ca5)*
- One file with invalid YAML frontmatter fails the whole insitu run, and the default `sources.include` is `**/*.md`. *Verified in source (`index.rs:129-134`, `document.rs:111-113`, `config.rs:12` at 9d53ca5)*
- [mdsmith](https://github.com/jeduden/mdsmith)'s `fix` applies only the rules enabled in the effective config, and rules can be switched off by category; the catalog rule is in the `directive` category. *Verified in source (`internal/fix/fix.go:383-450,648-680`, `internal/checker/checker.go:52-70`, `internal/config/config.go:11-12,77`, `internal/rules/MDS019-catalog/README.md:6` at 28af6a9)*
- mdsmith's `check` and `fix` have no flag that selects a single rule. *Verified in source (listing: the flag tables in `docs/reference/cli/check.md:36-47` and `fix.md:30-39` at 28af6a9)*
- [mdbook-cmdrun](https://github.com/FauconFan/mdbook-cmdrun) runs each marker's text as a shell command (`sh -c`). By default a non-zero exit inserts the command's standard output with no error; with `--strict` or an expected exit code, an error message is inserted instead. Either way the build succeeds; only a shell that can't start fails it. *Verified in source (`src/cmdrun.rs:24-40,100-129,167-280` at 746f6f6)*
- mdbook-cmdrun depends on mdbook 0.4 and only warns when mdBook's version differs. *Verified in source (`Cargo.toml:17`, `src/main.rs:32-48` at 746f6f6)*
- [DuckDB's yaml extension](https://github.com/teaguesterling/duckdb_yaml)'s `read_yaml_frontmatter` takes a glob and the options `as_yaml_objects`, `content` and `filename`. *Verified in source (`src/yaml_frontmatter.cpp:15-30,184-311,408` at c619d85)*

Docs only:

- mdBook 0.5 says preprocessors and renderers must be migrated from 0.4 to keep working. *Docs only (mdBook `CHANGELOG.md:122`, master, read 2026-11-19)*
- mdsmith's catalog takes a glob, a sort key, a CUE `where` filter and row templates, reads only frontmatter fields, and treats invalid frontmatter as absent. *Docs only (`internal/rules/MDS019-catalog/README.md` at 28af6a9)*
- mdsmith's `export --fix` regenerates stale directive bodies in memory and writes the page to standard output, never modifying the source. *Docs only (`docs/reference/cli/export.md:1-30` at 28af6a9)*
- mq prints Markdown, tables, JSON, CSV and YAML. *Docs only (README at 96964f3)*
- [cmdsync](https://github.com/ndonfris/cmdsync) takes the command from each region's opening marker (`<!-- CMDSYNC start: <command> -->`), and its `check` writes nothing and exits 1 when a region is stale. *Docs only for this note (the marker from its README; `check` read in source by a subagent: `src/cli.ts:52,84,140` at 54f307d)*

Release and activity data, read from the forges on 2026-11-20 (metadata, not source): insitu's only releases are 0.2.0-rc.1 and rc.2 (crates.io, GitHub, PyPI wheels), from a repository created 2026-09-06 with one contributor and five commits. mdsmith's last releases are its 0.58.0 release candidates of 2026-10-04. mq's latest release is v0.10.2 of 2026-11-20. mdbook-cmdrun's pull request 23 (the mdBook 0.5 migration) has been open since 2025-12-22.

Could not verify:

- How GitHub and mdBook render mdsmith's `<?catalog?>` blocks.
- Whether mdbook-cmdrun 0.7.3 runs under mdBook 0.5 at all; nothing was installed or run.
- cmdsync, mdsh and cog beyond their docs and the subagents' readings.
- The licenses of readb and markbase (no repository found), markdown-inject (only the forge's license field was seen), frontmatter-mcp's PyPI 0.5.3 listing and obsidiantools.

## Coverage ledger

| Route | State | Queries or reason |
|---|---|---|
| The stack itself | searched | `mise.toml` (no Markdown query or region tool; Backlog.md 1.55.3 pinned); the pilot `scripts/tasks.py` (`board` writes the tracked `backlog/BOARD.md`; no machine-readable output); the task-tracker design (the board printed on demand instead, TASK-REPO-008 still open) |
| Earlier notes and decisions | searched | `docs/prior-art/` grepped for insitu, dataview, markdown-magic, cog, sqlite and frontmatter queries; no earlier note covers the topic. The knowledge-base note's blend and the task-tracker design were read |
| GitHub repository search | searched | 55 distinct queries, counted from the run's per-query output files (its summary record says 16 round-1 wordings and 67 queries, the 67 including reruns): 17 round-1 wordings, each run twice (sorted by stars, and pushed after 2025-11-19 sorted by update time), among them "markdown codegen", "mdbook preprocessor", "mdbook sql", "markdown database", "markdown query language", "auto-generated markdown", "readme markers", "markdown tables frontmatter", "markdown index generator" and "markdown embed output"; then 21 star-sorted wordings in rounds 2-3 (round 4 used only code search and topics), such as "mdbook frontmatter", "frontmatter index", "markdown sql", "frontmatter duckdb", "headless dataview", "obsidian bases cli", "markdown regions" and "yaml frontmatter sqlite". A secondary rate limit after query 15 was waited out, and 12 queries rerun |
| GitHub topics | searched | 16 topic-name lookups (frontmatter, mdbook, dataview, markdown-codegen, markdown-database, docs-as-code, markdown-preprocessor and nine candidate names) and 23 `topic:` searches (frontmatter, frontmatter-cli, markdown-frontmatter, mdbook-preprocessor, mdbook-plugin, dataview, markdown-database, docs-as-code, markdown-preprocessor, obsidian-bases and mqlang, each sorted both ways; okf by stars) |
| GitHub code search | searched | 7 README searches naming krafna, mdsh, markdowndb (two owners), mdbook-cmdrun, embedme and cmdsync; 6 multi-term queries, all with no hits |
| LibHunt | searched | `/r/markdown-magic` (unrelated alternatives); `/r/insitu` (404) |
| GitLab search | searched | "frontmatter query", "frontmatter sql", "markdown frontmatter index", "mdbook preprocessor", "dataview", `topic=frontmatter`, "markdown generated sections" |
| Codeberg search | searched (through web search) | Blocks scripted clients, so no requests to it: `site:codeberg.org markdown frontmatter query`, `site:codeberg.org markdown generated index comment markers` (only Forgejo mirrors returned) |
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

Rounds ran per route group; each lists the serious candidates it added.

1. Seed queries on every route: [cog](https://github.com/nedbat/cog), [mdsh](https://github.com/zimbatm/mdsh), [cmdsync](https://github.com/ndonfris/cmdsync), [embedoc](https://github.com/foo-ogawa/embedoc), [mdbook-cmdrun](https://github.com/FauconFan/mdbook-cmdrun), [mdbook-tera](https://github.com/avitex/mdbook-tera), [mdbook-content-collections](https://github.com/saylesss88/mdbook-content-collections), [mdsmith](https://github.com/jeduden/mdsmith), [mdt](https://github.com/ifiokjr/mdt), [mq](https://github.com/harehare/mq), [rootline](https://github.com/pablontiv/rootline), [mdbasequery](https://github.com/intellectronica/mdbasequery), [MDQL](https://github.com/mdql-db/mdql), [GroundDB](https://github.com/JustMaier/groundDb), [fmql](https://github.com/buyuk-dev/fmql), [sensemaking](https://github.com/kmalakoff/sensemaking).
2. Candidate names, topics, READMEs and the mdBook plugin list: [krafna](https://github.com/7sedam7/krafna), [MarkdownDB](https://github.com/datopian/markdowndb), [DuckDB's yaml extension](https://github.com/teaguesterling/duckdb_yaml), [sqlfence](https://github.com/ahojukka5/enkeksi), [markdown-magic](https://github.com/DavidWells/markdown-magic), [md-frontmatter-index](https://github.com/ForkTheGhost/md-frontmatter-index).
3. Index and ADR generators, and alternatives pages (web): nothing serious; markasten and markdown-to-sqlite were seen and judged narrower than rows above.
4. MDQL, frontmatter-mcp and mdBook SQL queries (web), and code search for embedme, markdowndb and cmdsync (GitHub): nothing serious.
5. Python and Obsidian equivalents (web): nothing serious; obsidiantools was seen only.
6. Go and other cross-language frontmatter query tools (web): nothing new beyond mdbasequery.
7. Bases evaluators (web): [obaq](https://github.com/knu/obaq).
8. mdBook preprocessors that list pages by frontmatter (web): nothing.

The search stopped because a round added no new serious candidate: the registries and GitHub routes after their fourth round, and the web routes after their eighth.

## Refresh trigger

- When [insitu](https://github.com/marcusinthesky/insitu) releases 0.2.0 final and stays active for a few months: reconsider it for tracked indexes in place of mq with the view tool's `sync` and `check` modes.
- When [mdbook-cmdrun](https://github.com/FauconFan/mdbook-cmdrun) merges [pull request 23](https://github.com/FauconFan/mdbook-cmdrun/pull/23) and adds a failing-build mode and a command allowlist: reconsider it in place of the view tool's preprocessor mode.
- When [mq](https://github.com/harehare/mq) changes the record shape of `collection()`.
- When AD-331 is ruled, or the view tool (AD-326) is designed.
