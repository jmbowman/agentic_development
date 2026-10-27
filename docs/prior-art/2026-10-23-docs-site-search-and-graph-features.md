# Prior art: a docs-site generator with strong search and knowledge-graph features (2026-10-23)

- **Effort:** full method, because the site generator and its plugins would be delivered to every repo through the template, and their configuration is long-lived. The Markdown content itself stays portable.
- **Already known:** the developer runs mdBook in other repos (for example the public [PortaBase](https://github.com/jmbowman/portabase)), linted with mdbook-lint, and finds its search results basic. Quartz's features appeal, but its Node stack and fork-the-repo install don't. Zensical has been seen. Meilisearch and Turso's Tantivy-backed full-text search were named as possible search backends. The companion note [2026-10-23-progressive-disclosure-knowledge-base.md](2026-10-23-progressive-disclosure-knowledge-base.md) sets the page shape this site must render: plain Markdown with optional OKF-style frontmatter (`description`, `verified`, `stale_after`) and standard relative `.md` links, checked by authoring rules and linters.

## Need and criteria

| Requirement | Underlying need |
|---|---|
| A browsable static site that rebuilds after each batch of edits | A person reviews and navigates the knowledge base without opening files one by one |
| Better search than mdBook's | Finding the right page and section: relevance ranking, stemming, highlighted excerpts, results at the heading level, filtering by frontmatter, ideally typo tolerance |
| Search that is static, or a cheap engine | GitHub Pages or free hosting, with no running server to maintain |
| Quartz-like features | Following the knowledge graph: backlinks, a graph view, hover previews of linked pages, a folder explorer, display of frontmatter (description, tags, `verified`, `stale_after`) |
| Works with the knowledge-base pages | Optional YAML frontmatter (possibly including OKF's `type` key) and standard relative links like `../x.md`, rendered without rewriting the source |
| Smooth install, Rust or Python preferred | A pinned binary or uv tool through mise, updatable by Renovate, with the site living in the project's own `docs/` rather than in a fork of the generator |

**Hard criteria:**

1. An OSI-approved license.
2. Static output that can be hosted on GitHub Pages.
3. Builds a `docs/` directory inside the project repo, with no fork-the-generator model.
4. YAML frontmatter and standard relative `.md` links work without changing the source.
5. Local preview.

**Preferences:**

- search quality;
- each of the Quartz-like features;
- live reload;
- install through mise with a pinned version, updated by Renovate;
- Rust or Python;
- a maintained base;
- little custom code.

## Verdict

**Blend: mdBook + Pagefind + mdbook-frontmatter-render + a custom preprocessor for backlinks, the graph view and hover previews.**

- **mdBook** stays the base. It is maintained and in mise's registry, already in use, and resolves relative `.md` links natively.
- **[Pagefind](https://github.com/Pagefind/pagefind)** (MIT, Rust) replaces the built-in search. It runs as a post-build step over the HTML, with `[output.html.search] enable = false` and a theme override, a pattern several public books already use. It brings:
  - BM25 ranking, stemming and highlighted excerpts;
  - sub-results per heading;
  - metadata filters fed from frontmatter;
  - an index split into chunks, loaded on demand.

  It is installable from PyPI or as a static binary.
- **[mdbook-frontmatter-render](https://github.com/OptimalCNC/mdbook-frontmatter)** (MIT) removes the YAML header and renders it as a metadata ribbon. [mdbook-yml-header](https://github.com/dvogt23/mdbook-yml-header) (MPL-2.0) is the fallback if only stripping is needed.
- **Custom piece:** one preprocessor, which mdBook allows in any language, including a short Python script. It would do three things:
  1. append a backlinks section to each chapter;
  2. emit `graph.json` for a small graph-view script;
  3. add hover previews of linked chapters.

  It would borrow its parsing from [mkdocs-backlinks-section-plugin](https://github.com/six-two/mkdocs-backlinks-section-plugin), its graph from [mkdocs-network-graph-plugin](https://github.com/develmusa/mkdocs-network-graph-plugin), and the behavior of Quartz's popovers. Navigation stays a hand-maintained `SUMMARY.md`, which mdbook-lint's MDBOOK005 check guards, or a generated one.

**Runner-up: the Python stack.** It covers every Quartz feature today with no custom code:
- [ProperDocs](https://github.com/ProperDocs/properdocs), an MkDocs 1.6 fork;
- [MaterialX](https://github.com/jaywhj/mkdocs-materialx), a Material fork with Pagefind search and link previews;
- mkdocs-backlinks-section-plugin;
- a graph plugin;
- [mkdocs-awesome-nav](https://github.com/lukasgeiter/mkdocs-awesome-nav) for folder navigation.

It ranks second because its base is fracturing:
- upstream MkDocs is unmaintained, and an incompatible 2.0 is announced;
- Material for MkDocs entered maintenance mode on 2025-11-05, with end of life around 2026-11-05;
- MaterialX has one maintainer;
- every graph plugin found depends on the `mkdocs-material` distribution, which collides with MaterialX's copy of the same package.

Revisit it if the custom preprocessor proves costly. Revisit [Zensical](https://github.com/zensical/zensical) once its module API lets third-party plugins run: it reads the same `mkdocs.yml`, and its Rust search engine is due to become a standalone project.

## Candidates and matrix

Ranked shortlist:

1. **mdBook + Pagefind + frontmatter-render + custom preprocessor.** It has a stable base, the best static search found, and the user's existing setup. The graph features are about a day of custom code, built from known designs. It would drop below the Python stack if that code grows past a small preprocessor and a few hundred lines of JavaScript.
2. **ProperDocs + MaterialX + plugins.** Every feature exists today. But the base is fracturing, and the graph plugins have a packaging conflict. It would move up if Zensical or a maintained Material successor supports the backlinks and graph plugins.
3. **scraps + Pagefind.** A Rust single binary that reads OKF frontmatter and resolves relative `.md` links, with backlinks and a per-page neighbourhood graph. Its own search covers titles only, and it has no live reload, no hover previews and no folder explorer. It would move up if it gains `serve` with reload.
4. **Zensical.** It has a Rust core with its own search engine and experimental previews, but no backlinks or graph, and no third-party plugins yet.
5. **Hugo.** A single binary with render hooks and backlink and graph theme modules. But everything Quartz-like is template work, monolingual sites need extra link-hook config, and OKF's `type` key, if used, collides with Hugo's reserved `type`.
6. **Zola.** It renders only `@/`-prefixed internal links, and its backlinks come only from those, so relative `.md` links fail.
7. **kiln, leafpress.** Go garden generators. They match backlinks by basename (kiln) or follow only wikilinks (leafpress).

| Candidate | Class | License (file at commit) | Reason |
|---|---|---|---|
| [mdBook](https://github.com/rust-lang/mdBook) | adopt (base) | MPL-2.0 (`LICENSE` at 43b8aee) | Maintained, already in use, relative `.md` links native |
| [Pagefind](https://github.com/Pagefind/pagefind) | adopt (search) | MIT (`LICENSE` at 0be9ecc) | BM25, stemming, sub-results, filters, chunked static index |
| [mdbook-frontmatter-render](https://github.com/OptimalCNC/mdbook-frontmatter) | adopt (frontmatter) | MIT (`LICENSE-MIT` at 854479f) | Strips the YAML header and renders it; built for mdBook 0.5.4 |
| [mdbook-yml-header](https://github.com/dvogt23/mdbook-yml-header) | building block (fallback) | MPL-2.0 (`LICENSE`) | Strips the YAML header; built for mdBook 0.5.2 |
| [mdbook-frontmatter-strip](https://github.com/saylesss88/mdbook-frontmatter-strip) | building block (fallback) | Apache-2.0 (`LICENSE` at 4cd4665) | Strips the YAML header |
| [Nadrieril/mdbook-backlinks](https://github.com/Nadrieril/mdbook-backlinks) | borrow ideas | none (no license file) | Backlinks for all Markdown links on mdBook 0.5, but it can't be adopted |
| [mkdocs-backlinks-section-plugin](https://github.com/six-two/mkdocs-backlinks-section-plugin) | borrow ideas / runner-up part | MIT (`LICENSE` at cbe247c) | Parses rendered `<a href>`, so standard links work |
| [mkdocs-network-graph-plugin](https://github.com/develmusa/mkdocs-network-graph-plugin) | borrow ideas / runner-up part | MIT (`LICENSE` at 79bcdf5) | D3 global and local graph from relative links |
| [ProperDocs](https://github.com/ProperDocs/properdocs) | runner-up base | BSD-2-Clause (`LICENSE` at 152cc8c) | Drop-in MkDocs 1.6 fork; sparse releases |
| [MaterialX](https://github.com/jaywhj/mkdocs-materialx) | runner-up theme | MIT (`LICENSE` at 767cd76) | Material fork with Pagefind and previews; one maintainer |
| [mkdocs-awesome-nav](https://github.com/lukasgeiter/mkdocs-awesome-nav) | runner-up part | MIT (`LICENSE.md` at 49e057d) | Folder-driven navigation; Zensical recognizes it |
| [Zensical](https://github.com/zensical/zensical) | watch | MIT (`LICENSE.md` at 3f3c8a7) | Rust core, its own search; runs only allowlisted plugins |
| [scraps](https://github.com/boykush/scraps) | borrow ideas / alternate | MIT (`LICENSE.md` at d3aa378) | OKF-aware Rust SSG; title-only search; no reload |
| [Hugo](https://github.com/gohugoio/hugo) | reject | Apache-2.0 (`LICENSE` at ed22b85) | Quartz-like features are all template work; a `type` key collides with Hugo's reserved `type` |
| [Zola](https://github.com/getzola/zola) | reject | EUPL-1.2 for new code, MIT for older (`LICENSE`, `LICENSE-MIT` at e93c3de) | Relative `.md` links aren't resolved |
| [kiln](https://github.com/otaleghani/kiln) | reject | MIT (`LICENCE.md` at 95372f0) | Backlinks match by basename; previews on wikilinks only |
| [leafpress](https://github.com/shivamx96/leafpress) | reject | MIT (`LICENSE` at d1ddc42) | Backlinks and previews follow wikilinks only |
| [Sphinx](https://www.sphinx-doc.org) + MyST + [sphinx-tippy](https://github.com/sphinx-extensions2/sphinx-tippy) | reject | BSD (PyPI metadata) / MIT (`LICENSE` at 17770ce) | No backlinks or graph extension found; navigation needs a toctree |
| [Jupyter Book 2 / mystmd](https://github.com/jupyter-book/mystmd) | reject | BSD-3-Clause / MIT | Needs a Node runtime; no backlinks |
| [Meilisearch](https://github.com/meilisearch/meilisearch) | reject (for now) | MIT core, BSL-1.1 enterprise parts (`LICENSE` at 7b6f9f3) | Excellent engine, but a server; no free cloud plan (from $20/month, docs only) |
| [Turso](https://github.com/tursodatabase/turso) full-text search | reject (for now) | MIT (`LICENSE.md` at 891d1f5) | BM25 and phrase search, but no stemming or snippets, and no static or browser story (docs only) |
| [Typesense](https://github.com/typesense/typesense) | reject | GPL-3.0 (`LICENSE.txt` at 66fec87) | A server; the cloud free tier is one-time (docs only) |
| [Algolia DocSearch](https://github.com/algolia/docsearch) | reject | MIT UI, proprietary engine | Free only for public technical docs that are accepted; no local use (docs only) |
| [sql.js-httpvfs](https://github.com/phiresky/sql.js-httpvfs) | borrow ideas | Apache-2.0 (`LICENSE` at c64536d) | FTS5 over HTTP range requests; stale since 2024; DIY indexer and UI |
| [Summa](https://github.com/SpaceFrontiers/summa) | borrow ideas | MIT (`Cargo.toml:21`; no license file) | Tantivy over HTTP range requests; DIY pipeline |
| [StaticSearch](https://github.com/craigbuckler/staticsearch) | alternate (search) | MIT (`LICENSE` at 29385aa) | Claims fuzzy matching and stemming in 27 languages; Node; pre-1.0 |
| [Orama](https://github.com/oramasearch/orama), [MiniSearch](https://github.com/lucaong/minisearch) | borrow ideas | Apache-2.0 / MIT | Typo-tolerant libraries; you build the indexer and UI |
| [Stork](https://github.com/jameslittle230/stork) | reject | Apache-2.0 (`license.txt` at efa98da) | The author has wound it down |
| [tinysearch](https://github.com/tinysearch/tinysearch) | reject | MIT / Apache-2.0 | Small sites only; whole index in one bundle |

Matrix (✓ native, ◐ partial, ⊕ extensible, ✗ unsupported, ? unverified). H marks the hard criteria. "Quartz" marks Quartz-like features.

| Criterion | mdBook + Pagefind + custom | ProperDocs + MaterialX + plugins | scraps + Pagefind | Zensical |
|---|---|---|---|---|
| License (H) | ✓ | ✓ | ✓ | ✓ |
| Static, Pages-hostable (H) | ✓ | ✓ | ✓ | ✓ |
| In-repo `docs/` (H) | ✓ | ✓ | ✓ (`-C`) | ✓ |
| Frontmatter and relative links (H) | ✓ with a preprocessor (`tree.rs:1155-1175`; YAML not enabled, `lib.rs:44-60`) | ✓ | ✓ (`html.rs:602-620`) | ✓ |
| Local preview (H) | ✓ `mdbook serve` | ✓ `properdocs serve` | ◐ build then serve, no reload | ✓ |
| Search quality | ✓ Pagefind: BM25 (`search.rs:137-163`), stemming, sub-results; typo tolerance ✗ (prefix only, `search.rs:113-114`) | ✓ Pagefind (`providers/pagefind.py`) | ✓ with Pagefind added (its own index is title-only) | ◐ its own engine, English UI only |
| Quartz: backlinks | ⊕ custom | ✓ (`__init__.py:77,226`) | ✓ | ✗ |
| Quartz: graph view | ⊕ custom | ◐ plugin conflicts with MaterialX's package | ◐ per-page SVG, at most 18 nodes | ✗ |
| Quartz: hover previews | ⊕ custom | ◐ experimental (`extensions/preview.py`) | ✗ not found | ◐ experimental |
| Quartz: folder explorer | ◐ `SUMMARY.md` | ✓ awesome-nav | ◐ lists and tags | ✓ |
| Quartz: frontmatter display | ✓ ribbon | ◐ template overrides | ◐ | ◐ |
| Install via mise and Renovate | ✓ aqua mdBook; Pagefind via `github:` or `pipx:` | ✓ `pipx:`/uv with `--with`; dependency override needed | ◐ `github:`/`cargo:` | ✓ PyPI |
| Maintained base | ✓ | ✗ MkDocs unmaintained, Material EOL around 2026-11 | ✓ very active, young | ✓ pre-1.0 |
| Custom code | ◐ one preprocessor plus JavaScript | ✓ none | ◐ reload and previews missing | n/a |

**Blends considered:**

- **mdBook + Pagefind + frontmatter-render + a custom preprocessor:** the verdict.
- **ProperDocs + MaterialX + six-two backlinks + develmusa graph + awesome-nav:** the runner-up. A `[tool.uv] override-dependencies` entry that drops `mkdocs-material` would resolve the package collision.
- **scraps + Pagefind:** OKF-native and minimal, but it lacks reload and previews.
- **Hosted search (Meilisearch Cloud, DocSearch) on any generator:** better typo tolerance, but it costs money or depends on acceptance into a program, and it can't search locally.

**Scenario walk:**

1. *An agent batch changes ten pages and the site rebuilds.*
   - mdBook: `mdbook build` then `pagefind --site book`. `mdbook serve` reloads the build, but the Pagefind index is refreshed only by the post-build step, so a local loop runs both.
   - Python stack: the theme runs Pagefind inside the build, and serve reloads.
2. *A fresh CI clone publishing to Pages.*
   - mdBook: mise installs mdBook, Pagefind and the preprocessor binaries at pinned versions, and Renovate updates them.
   - Python stack: one `uv tool install` with pinned extras. But the dependency override needs a project `pyproject.toml`.
3. *Upstream breakage.*
   - mdBook: stable, but the preprocessors are maintained by small projects. The custom preprocessor stays under our control.
   - Python stack: Material's end of life and the MkDocs 2.0 split land within a year, so the forks need watching.
4. *A reader opens a page with OKF frontmatter.*
   - mdBook: the ribbon shows `description`, `verified` and `stale_after`, and Pagefind filters on `type` once a template emits `data-pagefind-filter`.
   - Python stack: the title, description and tags show natively; the other fields need a template override.

## Limitations checked in source

- mdBook renders relative `.md` links as `.html`. *verified in source (`crates/mdbook-html/src/html/tree.rs:1155-1175` at 43b8aee, by a subagent)*
- mdBook never enables YAML metadata blocks, so frontmatter renders as page content. *verified in source (`crates/mdbook-markdown/src/lib.rs:44-60` at 43b8aee)*
- mdBook's built-in search is elasticlunr-rs, with field boosts, prefix expansion and heading splitting. *verified in source (`Cargo.toml:33`, `crates/mdbook-core/src/config.rs:698-725` at 43b8aee)*
- Pagefind ranks with BM25. *verified in source (`pagefind_web/src/search.rs:137-163` at 0be9ecc, by a subagent)*
- Pagefind matches by prefix and stem, not typo tolerance. *verified in source (`search.rs:113-114,817-819`, by a subagent)*
- Pagefind runs a phrase search only when the whole query is quoted. *verified in source (`pagefind_web_js/lib/coupled_search.ts:596`, by a subagent)*
- MaterialX pins `mkdocs>=1.6,<=1.6.1`, requires `properdocs` and `pagefind[extended]`, and ships a Pagefind search provider. *verified in source (`pyproject.toml:41-56`, `material/plugins/search/providers/pagefind.py` at 767cd76)*
- MaterialX ships the `material` package under the distribution name `mkdocs-materialx`. *verified in source (`pyproject.toml:30,113` at 767cd76)*
- develmusa's graph plugin requires `mkdocs-material`. *verified in source (`pyproject.toml:11-13` at 79bcdf5)*
- six-two's backlinks plugin parses rendered `<a>` tags, so standard relative links count. *verified in source (`src/*/__init__.py:23,77,226` at cbe247c)*
- Zensical skips any plugin that is not on its allowlist. *verified in source (`python/zensical/config.py:131-214,2124-2125` at 3f3c8a7, by a subagent)*
- scraps resolves relative `.md` links. *verified in source (`modules/libs/src/html.rs:602-620` at d3aa378, by a subagent)*
- scraps has no file-watch or live-reload dependency. *verified by listing (`grep -i "notify|livereload|hotwatch"` across its Cargo.toml files at d3aa378: no hits)*
- Zola resolves only `@/` internal links, and its backlinks come from those alone. *verified in source (`components/markdown/src/markdown.rs:419-455`, `library.rs:182-195` at e93c3de, by a subagent)*
- Hugo reserves the `type` frontmatter key. *verified in source (`hugolib/page__meta.go:726-728` at ed22b85, by a subagent)*
- kiln matches backlinks by basename. *verified in source (`internal/obsidian/obsidian.go:334-337` at 95372f0, by a subagent)*
- Meilisearch has no free cloud plan, and Turso's full-text search has no snippets or stemming. *docs only*

Could not verify:
- Whether Pagefind's index refresh can be wired into `mdbook serve`'s rebuild loop without a wrapper script.
- How MaterialX's preview behaves on large sites.
- Whether Hugo's `GetPage` resolves `../x.md` from nested pages (forum evidence only).
- How much the custom preprocessor would cost, which is an estimate until a spike.

## Coverage ledger

| Route | State | Queries or reason |
|---|---|---|
| The stack itself | searched | mdBook 0.5.4's search config and parser options (above); mdbook-lint's MDBOOK005; mise registry entries for mdbook, zola and hugo |
| Earlier notes and decisions | searched | The companion knowledge-base note; this conversation's earlier mdBook findings |
| GitHub repository search | searched | Search engines: "static search", "client-side search", "pagefind", "full-text search wasm", "mdbook search", "sqlite httpvfs", "tantivy wasm". Generators: "obsidian publish", "static site backlinks", "mdbook backlinks", "zola backlinks", "hugo backlinks", "hugo digital garden theme", "second brain static site". Python: "mkdocs backlinks", "mkdocs graph", "mkdocs obsidian", "zensical plugin", "mkdocs pagefind", "mkdocs hover preview", "sphinx hover preview", "obsidian publish python" |
| GitLab and Codeberg search | excluded | The candidates found are GitHub-hosted, and the prior knowledge-base search found GitLab and Codeberg yield only mirrors for this domain |
| GitHub topics | searched | static-search, full-text-search, client-side-search, pagefind, digital-garden (Rust, Go, Python), obsidian-publish, mdbook-preprocessor, mkdocs-plugin, sphinx-extension, zensical, static-site-generator |
| GitHub code search | searched | `pagefind filename:book.toml`, `pagefind-ui filename:index.hbs` (real mdBook + Pagefind books); backlinks in mystmd, myst-theme and Sphinx |
| npm | searched | "static site search", "client side full text search", "mdbook search", "sqlite wasm http range", "fuzzy search index" |
| PyPI | searched | About 55 direct lookups (pagefind, zensical, properdocs, mkdocs-ng, mkdocs-materialx, the plugins, the Sphinx stack, jupyter-book, tantivy, lunr); `site:pypi.org` searches for static search |
| crates.io | searched | "mdbook search", "mdbook pagefind", "static search", "pagefind", "search wasm", "mdbook backlinks", "mdbook graph", "mdbook preview", "mdbook frontmatter", "mdbook summary", "digital garden", "static site generator", "backlinks", "zettelkasten" |
| Language registries (Go) | searched | Web searches reaching pkg.go.dev (kiln, obsidianator, blacklink) |
| Cross-language equivalents | searched | Pagefind's PyPI and npm wrappers; Material features compared with mdBook plugins |
| Awesome lists | searched | awesome-static-website-services (Search), awesome-rust (text search), awesome-search, awesome-static-generators, the mkdocs and ProperDocs catalogs, the mdBook third-party plugins wiki |
| alternativeto.net | searched | Pagefind and elasticlunr pages (all server engines); the Quartz page (wikis and doc tools only) |
| General web search | searched | "pagefind vs stork vs lunr", "static site search sqlite fts5 http range", "tantivy wasm static site search", "Turso full text search tantivy", "mdbook better search", "Quartz alternative Rust OR Go single binary", "Zola backlinks relative markdown links", "Hugo render-link hook relative .md", "MkDocs maintenance status 2026", "Material for MkDocs maintenance mode Zensical" |
| Hosted services | searched (docs only) | Meilisearch pricing, Algolia DocSearch eligibility, the Typesense Cloud free tier |

## Snowball rounds

- **Search engines.**
  1. Pagefind, Stork, tinysearch, sql.js-httpvfs, Summa, StaticSearch, and the mdBook + Pagefind theme-override pattern.
  2. sqlite-wasm-http, MiniSearch, Orama, FlexSearch, Meilisearch, Typesense, SeekStorm, and Zensical's search.
  3. Only docs scrapers and Summa's successor hermes, so the group stopped.
- **Rust and Go generators.**
  1. kiln, leafpress, xlog, scraps, and Nadrieril/mdbook-backlinks.
  2. mdbook-tagging, the `SUMMARY.md` generators, and dokt.
  3. OKF-aware tools: openknowledge, okf-rs, and okf-hugo.
  4. Only marginal tools (rs-web, italic).
- **Python generators.**
  1. Zensical, ProperDocs, and the backlinks, graph and nav plugins.
  2. develmusa's and SawyerRensel's graph plugins, MaterialX, and mkdocs-ng.
  3. Previews and nodegraph.
  4. Fork-this-repo templates, which the criteria exclude.
  5. Nothing new.

No group hit the round cap while still adding serious candidates.

## Refresh trigger

- When Zensical's module API ships.
- When MkDocs 2.0 is released, or when Material for MkDocs reaches end of life (around 2026-11).
- When scraps gains live reload.
- After the custom preprocessor spike, if it proves larger than estimated.
