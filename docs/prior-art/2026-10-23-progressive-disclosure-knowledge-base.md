# Prior art: a human-paced, progressive-disclosure knowledge base for project repos (2026-10-23; revised 2026-10-25)

- **Effort:** full method, because the choice would be delivered to every repo, and its page conventions become long-lived content that is costly to migrate.
- **Already known:** the requirements and gaps are written up in the public [PortaBase wishlist](https://github.com/jmbowman/portabase/blob/master/docs/wiki/agentic_sdlc.md) ("Progressive Discovery") and [PortaBase's agentic support page](https://github.com/jmbowman/portabase/blob/master/docs/wiki/agentic-development-support.md). The developer already tried or ruled out:
  - OpenKnowledge, dropped after a trial;
  - Karpathy's LLM-Wiki and about 150 derivatives, among them SamurAIGPT/llm-wiki-agent, coleam00/claude-memory-compiler, xoai/sage-wiki, lewislulu/llm-wiki-skill, atomicstrata/llm-wiki-compiler, nvk/llm-wiki, swarmvault, alfadur7/llm-wiki-newsroom and agenticnotetaking/arscontexta;
  - LEANN, for search;
  - [Commonplace](https://github.com/zby/commonplace), kept as a source of ideas only.

  Tolaria was offered as a springboard. Four approval-gated systems were queued for a source check: LLM-Wiki-v3, byterover-cli, EchoWiki and llmwiki-marimo. None of the tools above was judged usable as is for a similar need elsewhere. Many have ideas worth borrowing.
- **Omitted:** an earlier private evaluation and backlog item on this topic are summarized here without links.

## Need and criteria

| Requirement | Underlying need |
|---|---|
| Progressive disclosure | A reader, human or agent, loads only what the task needs: a one-screen overview, then a summary, then the detail. Index pages, one-line descriptions and page types are the means |
| Built up at the pace of human need, with human review before commit | Accuracy and relevance. Nothing durable lands without a person choosing it. Agents propose, and the developer reviews the diff; git staging is already the review record |
| Updating and reorganizing as information arrives | Moving, splitting and merging pages without leaving broken links, in diffs small enough to review |
| Just enough detail, no history | A style contract agents follow and tools check: current intent written to be read cold, one home per fact, page types |
| High documentation quality (Diátaxis, a style guide) | Typed pages and checkable rules, with the agent rules matching the lint rules one for one so a lint failure points to a rule |
| Accessible to humans and agents | Plain Markdown in the repo, readable on GitHub and as a static site, and searchable by agents with ordinary tools |
| Cross-linking that stays valid | Broken links caught before commit, and pages that aren't in the index flagged |
| Finding information in other repos | Read another repo's knowledge base from a local reference clone pinned to a version |
| Compact, inside each project repo | A per-repo install through the project's tool manager, with little scaffolding and little process |
| Coexists with mdBook and LID | One navigation hierarchy (mdBook's `SUMMARY.md`), and LID's design tree (`docs/high-level-design.md`, `docs/intent/`, `docs/arrows/`) left to LID's own conventions and checker |

**Hard criteria:**

1. An OSI-approved license, compatible with use as an installed tool.
2. Human-gated: nothing requires autonomous ingestion, self-committing or moving branches. Plain file edits reviewed in git qualify.
3. Markdown files in the project repo are the source of truth.
4. Runs locally, with no hosted service.
5. Coexists with mdBook rendering and LID's documents, without a second navigation hierarchy or a formatter that rewrites them.

**Preferences:**

- standard Markdown links that render on GitHub (`[text](page.md)`) over wikilinks;
- no required frontmatter;
- low process overhead;
- checks that run in pre-commit and CI;
- installable and pinnable through mise, and updatable by Renovate;
- maintenance and maturity.

## Verdict

**Blend: written authoring rules enforced by linters, with a small capture skill.** The pieces:

1. **Authoring rules for agents.** One rules file that each repo's agent instructions point to. Every rule maps to a lint check where one exists, so agents rarely write pages that fail. Sources:
   - [developer-docs-framework](https://github.com/anivar/developer-docs-framework)'s content-type and writing rules (Diátaxis quadrants, one purpose per page, no steps in explanations, consistent terminology, at most two levels of nesting), adapted for internal knowledge rather than product docs;
   - [seiso](https://github.com/scarletkc/seiso)'s convention: one kind per page, one home per fact, no values that change faster than the page, pointers that name a file or symbol, no narration of how a page was made;
   - LID's rule that docs carry current intent, written to be read cold;
   - a page-size budget, so every page fits on a screen or two.
2. **seiso as the convention gate,** in prek and CI, with `docs/intent/`, `docs/arrows/` and `docs/high-level-design.md` excluded so LID keeps its own checks. Its kinds have no explanation or concept page, so conceptual wiki pages need a mapping or a recorded exemption.
3. **[Vale](https://github.com/vale-cli/vale)** for style-guide rules that seiso doesn't cover, such as terminology lists and banned phrases. Add it only where those rules are wanted.
4. **Link and structure checks, mostly already in use:**
   - rumdl's MD057 checks relative link targets;
   - mdbook-lint's MDBOOK005 flags pages missing from `SUMMARY.md`;
   - [lychee](https://github.com/lycheeverse/lychee) with `--include-fragments` checks heading anchors and external links;
   - optionally [schematter](https://github.com/iwe-org/schematter), for the few frontmatter fields kept.
5. **Progressive disclosure by convention:**
   - `SUMMARY.md` is the index;
   - each area has a one-screen overview page;
   - each page carries a one-line `description`.

   OKF's optional fields (`description`, `verified: {by: human:<id>}`, `stale_after`) are kept where useful, without requiring OKF's `type`.
6. **A capture skill of our own,** borrowing the design of IWE's distill skill:
   - candidates are staged in an inbox, each with quoted evidence;
   - one question first (keep all, skip all, or pick);
   - per item: remember, skip or edit;
   - rejections are recorded and never re-offered;
   - nothing is written when no one can answer.

   Writes land in the working tree, and git staging is the approval.
7. **Cross-repo lookup:** agents grep or read the reference-repo clones from [the reference-clones note](2026-10-19-agent-reference-clones.md). Site search for humans is covered in [the docs-site note](2026-10-23-docs-site-search-and-graph-features.md).

**IWE** is the main source of ideas: the capture flow, and the hub structure of its dev-workspace template. Adopt it only if one of these happens:
- retrieval or reorganization starts to hurt at scale, for example hundreds of pages and frequent moves;
- its rewriting operations learn to edit links in place;
- a repo outgrows `SUMMARY.md` as its only hierarchy.

## Candidates and matrix

Ranked shortlist:

1. **The lint-first blend.** It meets every hard criterion with tools that are already in the stack or install as single binaries. The custom work is a rules file and a capture skill. It would lose its place if the rules plus linters let through pages agents can't navigate, which is the gap IWE's retrieval targets.
2. **IWE + its skills plugin + OKF mode.** It has the best progressive retrieval and the only human-selected capture flow built into a tool, and its OKF mode is CI-validated. It fails the coexistence criterion:
   - its inclusion links form a second hierarchy beside `SUMMARY.md`;
   - its rename, extract, inline, normalize and update commands re-render whole documents in its own formatting, which two independent adopters disabled;
   - LID's documents would need to be carved out.

   It is also effectively single-maintainer and changes fast.
3. **The OKF stack** (okf by W4G1, plus serradura/okf). It has the most complete link-preserving refactors (move, split, merge, remove with redirect, all editing link lines only) and the best cross-repo search through a registry. But it requires a `type` on every page, both tools are young, and it has no capture flow.
4. **lat.md.** The only candidate whose links to code symbols are checked. But wikilinks are its primary syntax, it has no move command, and its intent-to-code links overlap LID's EARS specs and `@spec` annotations.
5. **hyalo.** Structural maintenance (move with link rewriting, link fixing, schema lint) with a `--dir` option for another vault. Useful if frequent moves make hand-fixed links costly.

| Candidate | Class | License (file at commit) | Reason |
|---|---|---|---|
| [seiso](https://github.com/scarletkc/seiso) | adopt | MIT (`LICENSE` at 5bae44f) | Convention linter for agent-written repo docs; excludes paths; fixed kinds |
| [developer-docs-framework](https://github.com/anivar/developer-docs-framework) | build on | MIT (`LICENSE` at c0e9445) | 27 rules and 6 style guides, Diátaxis baseline; aimed at product docs, so adapt the rules rather than install the skill |
| [Vale](https://github.com/vale-cli/vale) | building block | MIT (`LICENSE` at d7a379d) | Style-guide rules; no Diátaxis rules off the shelf |
| [lychee](https://github.com/lycheeverse/lychee) | building block | MIT or Apache-2.0 (`LICENSE-MIT`, `LICENSE-APACHE` at 06f90b0) | Fragment and external link checks |
| [schematter](https://github.com/iwe-org/schematter) | building block | Apache-2.0 (`LICENSE-APACHE`; `Cargo.toml:9` at 8cf557b) | Frontmatter and structure schemas; standalone, with no IWE dependency |
| [OKF spec v0.2](https://github.com/GoogleCloudPlatform/open-knowledge-format) | borrow ideas | Apache-2.0 (`LICENSE.md` at ad30107) | `description`, index pages, `verified`, `stale_after` |
| [IWE](https://github.com/iwe-org/iwe) | borrow ideas | Apache-2.0 (`LICENSE-APACHE`; `Cargo.toml:7` at 44a6742) | Retrieval and capture are strong; second hierarchy and whole-document rewrites conflict with mdBook and LID |
| [IWE skills](https://github.com/iwe-org/skills) | borrow ideas | MIT (`LICENSE` at b129bdc) | The distill flow is the model for our capture skill |
| [IWE dev-workspace](https://github.com/iwe-org/dev-workspace) | borrow ideas | (template) | Hub pages, a work-item vs reference split, minimal frontmatter |
| [okf (W4G1)](https://github.com/W4G1/okf) | borrow ideas / alternate | Apache-2.0 (`LICENSE` at 085e6bb) | Line-preserving move, split and merge; young, one maintainer |
| [serradura/okf](https://github.com/serradura/okf) | borrow ideas | Apache-2.0 (`LICENSE.txt` at cfb7ffa) | Registry and `@all` search; lint for orphans and missing index entries |
| [okfctl](https://github.com/cwest/okfctl) | borrow ideas | Apache-2.0 (`LICENSE` at 1fee902) | Move with a dry run and a registry; 8 stars |
| [lat.md](https://github.com/vercel-labs/lat.md) | borrow ideas | MIT (`LICENSE` at e52136e) | Code-symbol links, required directory indexes; overlaps LID |
| [hyalo](https://github.com/ractive/hyalo) | building block (alternate) | MIT (`LICENSE` at 697f215) | Move with link rewrite, link fixing, schema lint |
| [mex](https://github.com/mex-memory/mex) | borrow ideas | MIT (`LICENSE` at 5c643ad) | Inbox and plan/`--apply` approval boundary |
| [Surface](https://github.com/Connorrmcd6/surface) | borrow ideas | Apache-2.0 (`LICENSE` at 12859c2) | Code-anchored claims that need a human to re-confirm them |
| [napkin](https://github.com/Michaelliv/napkin) | borrow ideas | MIT (`LICENSE` at 7582d6a) | Overview → search → read, with output hints for the next step |
| [Tolaria](https://github.com/refactoringhq/tolaria) | reject | AGPL-3.0 (`LICENSE` at ce9599c) | Desktop GUI; rename rewrites wikilinks only |
| [zk](https://github.com/zk-org/zk) | reject | GPL-3.0 (`LICENSE` at 21ccb69) | No rename refactor |
| [DocGov](https://github.com/ZeeshanSultan/DocGov) | borrow ideas | MIT (`LICENSE` at 335fdbe) | Document-class taxonomy and lenses; `fix` commits and runs `git reset --hard` |
| [Link](https://github.com/gowtham0992/link) | borrow ideas | MIT (`LICENSE` at cc92f36) | Capture → proposal → accept; review-due dates; wikilinks |
| [LLM-Wiki-v3](https://github.com/vvvvvivekkk/LLM-Wiki-v3) | borrow ideas | none (no license file) | `pending/` queue with accept and commit; dormant |
| [byterover-cli](https://github.com/campfirein/byterover-cli) | reject | Elastic License 2.0 (`LICENSE:1` at 1052ac1) | Source-available |
| [openwiki](https://github.com/langchain-ai/openwiki), [codealmanac](https://github.com/AlmanacCode/codealmanac) | reject | MIT / Apache-2.0 | Agent-generated content on a schedule |
| [scaccogatto/okf-skills](https://github.com/scaccogatto/okf-skills), [stjbrown/agent-knowledge](https://github.com/stjbrown/agent-knowledge), [dexio llm-wiki-skills](https://github.com/dexio-wiki/llm-wiki-skills) | borrow ideas | MIT (`LICENSE` at 49f8fb4, 0d1a828, f9e629d) | Agent-driven upkeep; dexio's wiki-review diff digest is worth borrowing |
| Other Diátaxis skills ([gooddocs](https://github.com/neozenith/agentic-dotfiles/tree/main/skills/gooddocs), [Ferroman](https://github.com/Ferroman/diataxis-documentation-skill), [trogonstack](https://github.com/trogonstack/agentskills)) | borrow ideas | MIT (`LICENSE` at 4c5fa56, 8d67cf3, 8a6be53) | Writing and restructuring guidance |
| [markdown-oxide](https://github.com/Feel-ix-343/markdown-oxide), [marksman](https://github.com/artempyanykh/marksman) | building blocks (editor) | Apache-2.0 / MIT | Editor rename and link diagnostics for the human side |

Matrix (✓ native, ◐ partial, ⊕ extensible, ✗ unsupported, ? unverified). H marks the hard criteria.

| Criterion | Lint-first blend | IWE + skills + OKF mode | OKF stack | lat.md |
|---|---|---|---|---|
| License (H) | ✓ | ✓ | ✓ | ✓ |
| Human-gated (H) | ✓ edits reviewed in git; capture skill writes only selections | ✓ distill writes only selections (`distill.md:3-7,93-101`) | ✓ CLI with dry runs | ◐ template has agents update after every task |
| Markdown in repo (H) | ✓ | ✓ | ✓ | ✓ |
| Local only (H) | ✓ | ✓ | ✓ | ✓ |
| Coexists with mdBook and LID (H) | ✓ `SUMMARY.md` stays the only hierarchy; LID paths excluded from seiso | ✗ second hierarchy (inclusion links); whole-document rewrites (`rename.rs:50-53`) | ◐ `index.md` per directory beside `SUMMARY.md`; `type` required | ◐ wikilinks; overlaps EARS and `@spec` |
| Progressive disclosure | ◐ by convention: index, overview pages, descriptions | ✓ `retrieve` with expansion and token caps | ✓ `index.md` | ✓ required directory indexes (`check.ts:546-595`) |
| Reorganize without broken links | ◐ `git mv` plus link checks that catch every miss | ◐ rewrites links but reformats documents | ✓ line-preserving rewrites (`markdown.rs:295-325`) | ✗ no move command |
| Doc quality | ✓ seiso and rules, optionally Vale | ◐ schemas | ◐ hygiene lint | ◐ writing-style page |
| Cross-repo lookup | ◐ grep or read reference clones | ◐ runs in the current directory | ✓ registry (serradura) | ✓ pinned external sources |
| Process overhead | ✓ rules, pre-commit hooks, one skill | ✗ workspace config, policy file, inbox, formatter regime | ◐ two tools, `type` on every page | ◐ post-task updates, checks |
| Maturity | ◐ seiso is young (created 2026-09); the rest is established | ◐ since 2024-09 but single-maintainer, fast-changing | ✗ both created mid-2026 | ✓ |

**Blends considered:**

- **Lint-first + a capture skill:** the verdict.
- **Lint-first + IWE for retrieval only** (`iwe find` and `retrieve`, no rewrites, no policy file): it adds a tool for marginal gains. IWE's own benchmark found grep over raw text matching or beating its retrieval on accuracy.
- **Lint-first + okf for refactors:** worth adding if moves become frequent, because its rewrites leave other lines untouched.
- **IWE as the core:** rejected on the coexistence criterion and its overhead.

**Scenario walk:**

1. *A fact worth keeping comes up mid-session.* The agent offers it once. On a yes, the capture skill writes the page under the authoring rules, seiso and the link checks run in pre-commit, and the developer reviews the diff and stages it.
2. *An overgrown page is split.* The agent splits it with ordinary edits and updates the inbound links. rumdl's MD057 and lychee catch any link it misses, mdbook-lint's MDBOOK005 catches a page left out of `SUMMARY.md`, and the diff shows only the real changes.
3. *A fresh CI clone.* mise installs seiso, lychee and the existing linters at pinned versions, and the same checks fail the build that would fail pre-commit.
4. *An agent needs another repo's knowledge.* It greps or reads the reference clone, starting from that repo's `SUMMARY.md` and overview pages.
5. *A reader on GitHub or the site.* Relative `.md` links resolve on GitHub and in mdBook. A frontmatter preprocessor keeps the YAML off the rendered page (see the docs-site note).

## Community evidence

**What the OKF ecosystem runs on.** The spec's first commit was 2026-06-12, so every tool is at most about four months old. GitHub code search for `okf_version` in `index.md` returned 82 public bundle repos (the search caps at 100 hits). A sample of up to three concept pages per bundle showed:
- 13 are output of [openwiki](https://github.com/langchain-ai/openwiki), and 6 follow scaccogatto/okf-skills' `.okf/` layout;
- 61 carry no `generated` or `verified` fields at all;
- of the rest, agent or process actors (`claude-code`, `cursor-…`, `process:…`) outnumber `human:` actors by about five to one.

Validation is fragmented. Some repos use their own scripts, often copies of okf-skills' `okf_validate.py`. Others use the crates [`okf-lint`](https://github.com/rpmoore/okf-lint) (pinned in [everruns' CI](https://github.com/everruns/everruns/blob/main/.github/workflows/ci.yml)) or `okf`, or IWE's `iwe schema validate`. No one tool dominates. Community maps: [yzfly/awesome-okf](https://github.com/yzfly/awesome-okf) and [linyiru/awesome-okf](https://github.com/linyiru/awesome-okf).

**IWE in practice.**
- IWE ships OKF support (`iwe init --okf`), and its [dev-workspace](https://github.com/iwe-org/dev-workspace) template is a CI-validated OKF bundle for a coding agent's project memory.
- [yokozi-jp/hono-nx-vite-plus](https://github.com/yokozi-jp/hono-nx-vite-plus):
  - ADR 0005 manages `docs/` as an IWE OKF bundle with schema, link and orphan checks in pre-commit and CI;
  - ADR 0006 stops using every IWE rewriting operation, because they re-render target and referring documents and conflict with the repo's formatter.
- [yokozi-jp/spring-modulith-ai-dlc](https://github.com/yokozi-jp/spring-modulith-ai-dlc) ADR-036 expects `iwe normalize` to reformat 44 of 45 existing docs.
- [forhas/pure-dev](https://github.com/forhas/pure-dev) uses IWE only for find and retrieve, and rewrites links in its own script.
- In the [discussions](https://github.com/iwe-org/iwe/discussions), the maintainer responds quickly and often ships requests within days (#175, #260, #329, #381).
- The [blog](https://iwe.md/blog/) is candid. ["The benchmark that built the tools"](https://iwe.md/blog/the-benchmark-that-built-the-tools/) reports grep over raw transcripts beating IWE retrieval on accuracy (0.81 vs 0.75 on LOCOMO), with IWE ahead on speed and turns, and it retracts an earlier contaminated result.
- Independent write-ups are few: three posts on [docujAI](https://docujai.com/node/157) and one MarkTechPost tutorial. No independent critiques turned up.

## Limitations checked in source

- IWE rename re-renders every affected document from its AST, rather than editing link spans in place. *verified in source (`crates/liwe/src/operations/rename.rs:50-53` at 44a6742)*
- IWE writes links without an extension by default, and `iwe init` detects the existing majority style. *verified in source (`crates/liwe/src/model/config.rs:74`, `crates/liwe/src/init/detect.rs:102-128` at 44a6742)*
- IWE's workspace is the current directory plus `workspace.path`. *verified in source (`crates/iwe/src/main.rs:2803-2812` at 44a6742)*
- IWE's distill writes only selected items, and nothing in unattended runs. *verified in source (`crates/iwe/templates/claude/prompts/distill.md:3-7,93-101` at 44a6742)*
- IWE's link resolution drops `#fragment`, and its language server publishes no diagnostics. *docs only (`docs/comparison.md`)*
- schematter has no dependency on IWE. *docs only (README at 8cf557b)*
- seiso's kinds are fixed at readme, howto, reference, runbook, agents, adr, plan, changelog and generated. *verified in source (`src/rules/kind.rs:7-17` at 5bae44f)*
- seiso's configuration supports path exclusions. *docs only (`docs/guides/checking.md:42` at 5bae44f)*
- developer-docs-framework targets product and partner docs, and its `SKILL.md` frontmatter carries fields outside the Agent Skills spec (`user-invocable`, `agentic`). Its `name` (`diataxis-docs-framework`) differs from the repo name. *verified in source (`SKILL.md:1-28` at c0e9445)*
- okf (W4G1) rewrites links line by line and leaves other text unchanged. *verified in source (`crates/okf-core/src/markdown.rs:295-325` at 085e6bb)*
- okf (W4G1) supports split, merge, move, rename-section and remove-with-redirect. *verified in source (`crates/okf-core/src/refactor.rs:621,803,993,1151,1332`)*
- serradura/okf has no move or rename command. *verified by listing (`ls gems/okf/lib/okf/cli/` at cfb7ffa)*
- lat.md has no move or rename command. *verified by listing (command definitions in `packages/core/src/cli/core.ts` at e52136e)*
- Tolaria's rename rewrites wikilinks only. *verified in source (`src-tauri/src/vault/rename.rs:88-177` at ce9599c)*
- zk has no LSP rename handler. *verified by listing (`grep -rln "TextDocumentRename|RenameParams|textDocument/rename" internal` at 21ccb69: no hits)*
- LLM-Wiki-v3 accepts pending pages and commits them, and has no license. *verified in source (`src/wiki/review.py:1-55` at 267541d; `ls -a` and `pyproject.toml`: no license)*
- DocGov's `fix` commits with `--no-verify` and runs `git reset --hard` when verification fails. *verified in source, by a subagent (`core/git.js:106-111` at 335fdbe)*

Could not verify:
- How many of developer-docs-framework's 27 rules can map to seiso or Vale checks. That is design work for the rules file.
- How seiso behaves on a real wiki, including its false-positive rate on concept pages.
- The MCP Registry search for `obsidian`, which timed out twice; that space was covered through the punkpeye awesome-mcp-servers list.

## Coverage ledger

| Route | State | Queries or reason |
|---|---|---|
| The stack itself | searched | Claude Code skills, git staging as the review record, rumdl (MD057), mdbook-lint (MDBOOK005), LID's lidc and design tree, the planned reference-repo clones |
| Earlier notes and decisions | searched | The PortaBase wiki pages linked above, `docs/prior-art/` in this repo, the omitted private evaluation, and the [Commonplace](https://github.com/zby/commonplace) review corpus at 1a20def (`kb/agent-memory-systems/systems.csv`, filtered for manual write authority on file storage) |
| GitHub repository search | searched | About 80 two- or three-word queries, for example "markdown knowledge base", "markdown lsp", "markdown link refactor", "progressive disclosure", "agent knowledge base", "wiki links rename", "docs as code agent", "diataxis", "markdown mv", "living documentation", "knowledge bundle", "okf skill", "docs governance", "wiki inbox approval" |
| GitLab and Codeberg search | searched | "markdown knowledge base", "markdown lsp", "zettelkasten", "wiki links", "markdown link checker", "knowledge graph markdown", "agent memory markdown", "notes cli". Mirrors and 0-14 star projects only |
| GitHub topics | searched | zettelkasten, knowledge-base, pkm, wikilinks, llm-wiki, agent-memory, documentation-tool, diataxis, okf, open-knowledge-format, obsidian-cli, link-checker, documentation-drift, docs-as-code, living-documentation, markdown-wiki, agent-skills, claude-skills, mcp-server and claude-code-plugin, combined with docs, wiki and knowledge terms |
| GitHub code search | searched | Awesome lists naming markdown-oxide, marksman, IWE and zk; `marketplace.json` files naming diataxis, wiki, documentation or knowledge base; `okf_version` in `index.md` (the ecosystem sample); OKF validator and IWE command usage |
| npm | searched | "markdown knowledge base", "markdown link refactor", "wikilink rename", "markdown lsp", "progressive disclosure markdown", "markdown move file update links", "agents md context tree", "diataxis", and six more |
| PyPI | searched | `site:pypi.org` searches for knowledge bases with link refactoring, doc-to-code drift, and progressive-disclosure indexes; JSON lookups for docmv, docpin, docrot, plasma-wiki and similar |
| crates.io | searched | "markdown knowledge", "markdown lsp", "wikilink", "markdown links rename", "zettelkasten", "markdown link checker", "docs agents knowledge"; okf and okf-lint lookups |
| Language registries (Go) | searched | pkg.go.dev web searches for Markdown knowledge CLIs and OKF tools |
| Cross-language equivalents | searched | OKF toolchains in Go (okfctl, okfcli/okf), Rust (W4G1/okf, okf-rs) and Ruby (serradura/okf); "lat.md alternative" |
| Awesome lists | searched | awesome-claude-skills (three lists), awesome-agent-skills (two), awesome-mcp-servers (punkpeye, appcypher), awesome-claude-code, awesome-claude-code-plugins, awesome-okf (two) |
| alternativeto.net | searched | The Tolaria page (fetched); "alternatives to Foam" through web search |
| General web search | searched | 14 phrasings, including "progressive disclosure knowledge base for AI coding agents markdown in repo human review", "markdown wiki CLI automatically update links when file renamed", "human-in-the-loop LLM wiki agent proposes edits review diff", "Open Knowledge Format OKF markdown", "IWE markdown knowledge graph review OR experience" |
| Hosted services | searched | Swimm, GitBook and Mintlify; docs only, and none fits the local-only criterion |
| Skill directories | searched | skills.sh API, 21 queries ("knowledge base", "documentation", "diataxis", "wiki", "progressive disclosure", "docs drift", "okf", "wiki refactor", "rename links"); other directories through web search |
| Claude Code plugin marketplaces | searched | The official marketplace.json (315 plugins) grepped in full; claude.com/plugins fetched |
| MCP Registry | searched | wiki, markdown, knowledge, docs, notes and documentation returned their first pages. `obsidian` timed out twice and is unavailable |
| Anthropic's skills repo | searched | `skills/` listing; doc-coauthoring, knowledge-work-plugins documentation and memory-management read |
| Awesome lists for agent skills | searched | As in the awesome-lists row |
| GitHub topics for agent skills | searched | agent-skills, claude-skills, mcp-server and claude-code-plugin, combined with documentation, knowledge-base, wiki, diataxis and markdown |

## Snowball rounds

1. Seed queries added IWE, markdown-oxide, marksman, vscode-markdown-languageservice, lat.md, plasma-wiki, markmv, Vale, lychee, QMD, the Diátaxis skills, DocGov, axross and gooddocs.
2. OKF, IWE and lat.md tags and comparison pages added the OKF spec, okfctl, W4G1/okf, serradura/okf, scaccogatto/okf-skills, stjbrown/agent-knowledge, dexio, mex, openwiki and codealmanac.
3. A survey of agent knowledge tools plus the open-knowledge-format topic added seiso and Surface, along with smaller OKF variants.
4. Queries seeded by seiso, Surface and the OKF tools found only variants of tools already recorded.
5. Queries seeded by mex, DocGov and dexio added no new serious candidate, and the search stopped there.
6. A check of IWE's organization added schematter: the standalone schema validator split out of IWE.

## Refresh trigger

- After the rules file and capture skill have run in one repo's wiki for a few weeks. If agents keep writing pages that fail lint, or can't find what they need, revisit IWE's retrieval.
- When IWE's rewriting operations learn to edit links in place.
- When seiso's convention adds an explanation or concept kind, or reaches 1.0.
- When OKF reaches v1.0.
