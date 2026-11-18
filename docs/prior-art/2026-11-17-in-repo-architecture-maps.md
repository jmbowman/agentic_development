# Prior art: in-repo architecture maps for agents and reviewers (2026-11-17)

- **Effort:** full method. The search ran for task [AD-7](../../backlog/tasks/ad-7%20-%20Run-prior-art-Search-B-in-repo-architecture-maps-Groma-md-and-alternatives.md), which asked for a quick pass that switched to the full method if the skill's conditions held. They did. [groma.md](https://github.com/MrLesk/groma.md), [LikeC4](https://github.com/likec4/likec4), [Yggdrasil](https://github.com/krzysztofdudek/Yggdrasil) and LID's own design tree all met every hard criterion on the evidence first read. The verdict also sets the default for the repos that use this repo's templates.
- **Already known:**
  - **The trigger:** [groma.md](https://github.com/MrLesk/groma.md), from the author of [Backlog.md](https://github.com/MrLesk/Backlog.md). Backlog.md is this repo's task store, per [the task-management note](2026-11-12-task-management-for-humans-and-agents.md).
  - **No other tools known:** the developer knew no other architecture-map or C4 tools.
  - **OpenKnowledge:** "OpenKnowledge, dropped after a trial" in [the 2026-10-23 progressive-disclosure note](2026-10-23-progressive-disclosure-knowledge-base.md) was [inkeep/open-knowledge](https://github.com/inkeep/open-knowledge). The developer said (2026-11-17) it was dropped as overkill and immature, and because it worked against some of what the knowledge base is meant to do.
  - **[The 2026-10-27 review-burden note](2026-10-27-review-and-comprehension-burden.md):**
    - It classed [LikeC4](https://github.com/likec4/likec4) as borrow ideas ("overkill for one app"), and verified that LikeC4's `validate` checks layout against the model, not the model against code.
    - It classed [CodeBoarding](https://github.com/CodeBoarding/CodeBoarding) as borrow ideas.
    - It recommended Mermaid diagrams in LLDs, rendered in mdBook by [mdbook-mermaid](https://github.com/badboy/mdbook-mermaid). Its evidence: experiments where diagrams added to text improved comprehension with no time cost (Scanniello et al. 2014; Abrahão et al. 2013, as cited there).
  - **[The decision-records note](2026-11-06-decision-records-and-lid.md):** it saw [Structurizr](https://github.com/structurizr/structurizr).
  - **The knowledge-base blend:** this result has to sit beside it, as set in [the federated knowledge note](2026-11-06-federated-knowledge-and-work-items.md): mdBook, `SUMMARY.md`, seiso and extant.
- **Related:** [the cross-repo task coordination note](2026-11-16-cross-repo-task-coordination.md), the companion search for the task-tracker design in [AD-5](../../backlog/tasks/ad-5%20-%20Walk-LID-s-arrow-for-the-task-tracker-starting-from-the-pilot.md).

## Need and criteria

The question: does a tool like groma.md help agents and people understand a repo's architecture, and decide better, by enough to justify setting it up and keeping it current?

| Requirement | Underlying need |
|---|---|
| N1. Agents read the architecture cheaply | An agent decides where a change belongs and what it affects, using little context |
| N2. A visualization for people | Comprehension of the system, and review of what a change did to its structure (for example, an architecture diff on a pull request) |
| N3. Stays current with the code | The map is derived from the code, or drift between the two fails a check, so it can't silently rot |
| N4. Plain files in the repo | Changes to the map are reviewed as git diffs, like any other change |
| N5. Tasks link to components | A Backlog.md task shows the components it touches, and a component shows its work |
| N6. Coexists with LID and mdBook | No second design hierarchy competing with `docs/high-level-design.md` and `docs/intent/`, and no clash with an mdBook site |

**Common uses (confirmed by the developer):**

1. An agent starting work looks up which component owns a file and what that component touches.
2. A person reviews architecture drift on a pull request, with a visual aid.
3. Tasks show the components they touch.

**Hard criteria:**

- H1. An OSI-approved license.
- H2. Repo text files are the source of truth, with no required hosted service besides GitHub.
- H3. Runs locally, with no required account or AI service.
- H4. No automatic merge to the default branch. This matches the cross-repo search's H5.

**Preferences:**

- The tool doesn't commit or push on its own.
- Language coverage for this stack: Python, TypeScript, Rust and shell.
- Low setup and upkeep: a single binary or package, pinned by mise and updated by Renovate, that installs nothing else globally.
- Maturity and maintenance.
- Doesn't edit `AGENTS.md` or `CLAUDE.md` without asking.

## Verdict

**Blend.** LID's design tree, its `@spec` annotations and its hand-written Mermaid diagrams stay the architecture map. One small custom piece goes with them: a written rule for finding a file's owner, tracked as [AD-318](../../backlog/tasks/ad-318%20-%20Write-an-agent-rule-for-finding-which-segment-owns-a-file.md). No architecture-map tool is adopted now, here or as the default for other repos. The reasoning is HLD tenet 2: assemble from existing pieces and build only small gaps.

**Why no tool now:**

- **LID already provides most of the map.**
  - The HLD's Components table says where each component lives (`docs/high-level-design.md:159`, at 72dfa75). Its System Design section has a Mermaid component diagram (`docs/high-level-design.md:120`). Leaf LLDs describe each segment, and some carry their own diagrams (`docs/intent/subagent-notes/subagent-notes-design.md:92`).
  - 697 `@spec` lines in 82 non-Markdown files tie code, tests and eval cases to spec IDs (`git grep -c "@spec" 72dfa75 -- ':!*.md'`).
  - `mise run lid` fails on an orphaned or uncovered spec (`mise.toml:73`).
  - So use 1 is met with a lookup rule, and uses 2 and 3 in part. The diagrams are hand-written, render on GitHub, and change in the same reviewed diffs as the design.
  - What's missing is a structural view derived from code, and a picture of what a pull request changed in that structure.
- **Evidence on agents is mixed** (all paper-reported, mostly preprints).
  - Structured maps helped agents *find* code:
    - [Formal Architecture Descriptors as Navigation Primitives for AI Coding Agents](https://arxiv.org/abs/2604.13108) reports 33-44% fewer navigation steps.
    - [How Should Agents See Code?](https://arxiv.org/abs/2611.07286) reports better fault localization with 25-39% fewer tokens.
  - They helped little or not at all with *fixing* or *building*:
    - in How Should Agents See Code?, SWE-bench Pro resolution was mixed;
    - in [The Code of Theseus](https://arxiv.org/abs/2610.20068), recovered design documents made no significant difference to the held-out pass rate;
    - in [Evaluating AGENTS.md](https://arxiv.org/abs/2602.11988), context files added about 20% cost, and the repository overviews in them were not helpful.
  - The descriptor paper's gain shrank with a stronger model. Its authors expect larger gains in bigger repos, but didn't test that.
  - [RepoAtlas](https://arxiv.org/abs/2609.16936) gained 2.4 points over another graph-based method, which compares two maps rather than a map with none.
- **groma.md is the closest fit, but not yet safe to depend on.**
  - It is the only candidate that links Backlog.md tasks to components natively. [Eidos](https://github.com/mchawa/eidos)'s change deltas name components, but only in its own format, inside a second intent system that competes with LID's tree.
  - It calls itself an "early experimental prototype" with no compatibility promises.
  - It says it is "moving toward a model that is detached from the filesystem", which would break H2.
  - When Backlog.md is selected and no Backlog.md CLI is on PATH, it installs one globally (npm or bun `backlog.md@latest`, or brew), outside mise's pin. `groma plugin update` upgrades it the same way.
  - Its scanners don't cover shell.
  - Its task links rely on agents recording every modified file in the task after each edit.
  - It adds a second C4 hierarchy under `groma/` beside LID's tree.
- **Derived beats hand-kept, once it's stable.** Values that follow from other data are better computed than stored, so nothing drifts. That favours a map derived from code over one kept by hand, which is the case for a tool like groma.md once one is stable. Until then, the hand-kept parts stay small: a diagram per design doc, and `@spec` lines that `lidc` already checks.

**The custom piece** (AD-318):

- **The lookup rule:** to find a file's owner, look in order:
  1. its `@spec` IDs (`git grep -n "@spec" <file>`, then grep the ID under `docs/intent/` to find its segment);
  2. for a file with no `@spec` line, the HLD Components table's "Lives in" column;
  3. failing that, a grep for the path in `docs/intent/*/*-design.md`.

  Some LLDs name related segments in their prose, but nothing records a segment's neighbours systematically yet. `@spec` sits only at entry points, so many files (skill text, workflows, helpers) need step 2 or 3.
- **Task references:** tasks already link to segments in two forms. Some cite spec IDs, and many cite LLD paths (86 of 322 task files reference `docs/intent/`). A reverse lookup has to accept both forms. Settling one form belongs to the task-tracker design in AD-5.
- **A lidc query** that does the lookup is proposed in [lid-tooling feedback item (d)](../tool-feedback/lid-tooling.md).

**What would change this verdict:**

- groma.md commits to a stable in-repo format and drops the plan to detach from the filesystem;
- a repo grows large enough that agents' localization misses show up in sessions;
- a repo needs pull-request architecture diffs derived from code.

Then run the trial in [AD-320](../../backlog/tasks/ad-320%20-%20Trial-an-in-repo-architecture-map-tool-when-code-derived-PR-diffs-are-wanted.md): groma.md with [its Action](https://github.com/MrLesk/groma.md-action), or [LikeC4](https://github.com/likec4/likec4) with [likec4-architecture-diff-action](https://github.com/novibe-org/likec4-architecture-diff-action) if a hand-written model is enough.

**The task's open questions:**

- **OKF vs. OpenKnowledge.** They are different things.
  - OKF is the [Open Knowledge Format spec](https://github.com/GoogleCloudPlatform/open-knowledge-format) (v0.2). The earlier notes evaluated it and kept only an optional `description`. `verified` and `stale_after` later gave way to extant and blockwatch ([the federated knowledge note](2026-11-06-federated-knowledge-and-work-items.md)).
  - [OpenKnowledge](https://github.com/inkeep/open-knowledge) is a GPL-3.0 desktop and web Markdown editor (`LICENSE`, `README.md:9` at d04de0e). It ships an OKF skill pack (`packages/server/assets/skills/packs/okf/SKILL.md`).
  - The reasons it was dropped concern the editor, not the format.
  - [groma.md](https://github.com/MrLesk/groma.md) stores its map as an OKF 0.2 bundle with its own profile. Each C4 concept document needs a `type` (`C4 Actor`, `C4 System`, `C4 Container`, `C4 Component`), and the project record has `type: Groma Project` (`docs/component-markdown.md:40-49,147-176` at 587a806). This applies only inside `groma/`; it doesn't impose OKF on the rest of `docs/`.
- **Setup writes into `AGENTS.md`/`CLAUDE.md`.** Confirmed in source:
  - `groma init` adds or updates a managed `<!-- groma:start -->…<!-- groma:end -->` block in every existing `AGENTS.md` and `CLAUDE.md`, writing once for a symlinked pair. If neither file exists, it creates `AGENTS.md` (`src/agent-instructions.ts:6-13,67-79` at 587a806).
  - When Backlog.md is selected, it runs `backlog init … --agent-instructions agents`, but only if Backlog.md isn't already initialized (`src/init-command.ts:142-154`, `src/work/backlog-cli.ts:119-127`).
  - Here `CLAUDE.md` is a symlink to `AGENTS.md`, so groma.md would write one block. Removing it means deleting `groma/` and that block (`README.md:161`).
- **How it would sit beside LID and the knowledge-base blend.**
  - It would be a second hierarchy, derived from code (systems, containers, components), beside LID's tree, which is derived from intent. Nothing maps one onto the other.
  - Its OKF index (`groma/index.md`) is separate from `SUMMARY.md`. Listing `groma/` in `SUMMARY.md` would make its pages readable in mdBook, but the map itself needs `groma web` or its static export.
  - The Action's bundled publisher deploys previews to GitHub Pages from a `groma-previews` branch, and refuses to replace another Pages site. A repo whose Pages site is its mdBook instead runs the build step and passes its output to its own publisher (`README.md:17-29` at 8529a2e in groma.md-action).

## Candidates and matrix

**Ranked shortlist.** The ranking orders candidates by how well each serves the three common uses in the scenario walk below, as a part of this repo. Hard-criterion risks (groma.md's plan for H2) and the preferences break ties. A count of native cells alone would rank differently, because the native candidate gains most from the lookup rule and from what LID already checks.

1. **LID's design tree, `@spec` and Mermaid (native).**
   - Meets every hard criterion, N4 and N6. Covers N1, N2, N3 and N5 in part.
   - It would lose its place if agents in a larger repo kept missing where a change belongs, in ways a map derived from code would have caught.
2. **[groma.md](https://github.com/MrLesk/groma.md).**
   - The broadest coverage. It has:
     - a curated C4 map in Markdown;
     - `groma view <file>` for owners;
     - a live map and history comparison;
     - pull-request previews through its Action;
     - native Backlog.md links.
   - Held back by its prototype status, the stated move away from files, a possible global Backlog.md install, no shell scanner, and a second hierarchy.
   - It moves to first if it commits to a stable in-repo format and a repo needs code-derived diffs.
3. **[Yggdrasil](https://github.com/krzysztofdudek/Yggdrasil).**
   - Native N1 (`yg owner`, `yg context`) and N3 (`yg check` refuses undeclared dependencies).
   - No task links and no pull-request diff.
   - `init` changes git config and hooks without a confirmation step, and the tool is large: 28 commands.
   - It would rise if a repo wanted enforced component boundaries more than a picture.
4. **[LikeC4](https://github.com/likec4/likec4) with [likec4-architecture-diff-action](https://github.com/novibe-org/likec4-architecture-diff-action).**
   - A mature, plain-text `.c4` model with offline `validate` and `export`. The action posts a Mermaid diff of changed views on each PR, with no hosted service.
   - The model is written by hand. Only [asbuilt](https://github.com/padamson/asbuilt) (Rust) and [Archtrace](https://github.com/AdityaNerpagar/Archtrace) (TS/JS imports) tie it to code.
   - It would rise if a hand-written model with PR diffs turned out to be enough for use 2. The 2026-10-27 note found it overkill for one app.
5. **[faultline](https://github.com/halleylabs/faultline).**
   - Systems in `faultline.yml` with deny rules, a structural diff, a sticky PR comment, and MCP answers sized for agents.
   - `fault init` sends a directory outline and a README excerpt to Anthropic whenever `ANTHROPIC_API_KEY` is in the environment, unless `--no-ai` is passed (`src/cli.ts:94`).
   - `fault setup` writes `AGENTS.md`, `CLAUDE.md`, `.claude/settings.json` hooks, `.mcp.json` and a pre-commit hook without asking.
   - Files outside every system pass its check.
   - It would rise if `init` asked before calling a model, and `setup` asked before writing.
6. **[asbuilt](https://github.com/padamson/asbuilt).**
   - Generates a LikeC4 model from Rust code, with a strict drift check. Rust only.
   - It would rise with a Python or TypeScript front-end.

The skill allows four classes. "(building block)" and "(existing dependency)" below are labels on those classes, and the matrices have no not-applicable value. [AD-321](../../backlog/tasks/ad-321%20-%20Let-prior-art-search-classify-native-features-and-building-blocks-and-mark-a-criterion-as-not-applicable.md) settles both in the skill.

| Candidate | Class | License (file at commit) | Reason |
|---|---|---|---|
| LID design tree + `@spec` + Mermaid (native) | adopt (existing dependency) | LID [jszmajda/lid](https://github.com/jszmajda/lid) v1.4.6 (`apm.yml:7`); lidc [lid-tooling](https://github.com/EtaCassiopeia/lid-tooling) 0.3.0 (`mise.toml:13`); licenses read in their own notes | Already in use; with the lookup rule covers use 1, and uses 2 and 3 in part |
| [groma.md](https://github.com/MrLesk/groma.md) | borrow ideas (trial candidate, AD-320) | MIT (`LICENSE` at 587a806) | Best fit for N2 and N5; prototype, moving away from files |
| [groma.md-action](https://github.com/MrLesk/groma.md-action) | borrow ideas | MIT (`LICENSE` at 8529a2e) | Pull-request architecture previews through GitHub Pages |
| [LikeC4](https://github.com/likec4/likec4) | build on (building block) | MIT (`LICENSE` at 9f6ff0cd) | Plain-text C4 model and offline validator; was borrow ideas in the 2026-10-27 note, raised because a diff action now covers use 2 |
| [likec4-architecture-diff-action](https://github.com/novibe-org/likec4-architecture-diff-action) | build on (building block) | Apache-2.0 (`LICENSE` at 7a92157d) | Mermaid view diff as a PR comment; needs only the GitHub token |
| [Yggdrasil](https://github.com/krzysztofdudek/Yggdrasil) | borrow ideas | MIT (`LICENSE` at 45d1a51c) | Declared relations checked against code; heavy, intrusive `init` |
| [faultline](https://github.com/halleylabs/faultline) | borrow ideas | MIT (`LICENSE` at c983fdcb) | Structural diff, deny rules, sticky PR comment; sends repo data to Anthropic unasked when a key is set |
| [asbuilt](https://github.com/padamson/asbuilt) | borrow ideas | MIT OR Apache-2.0 (`LICENSE-MIT`, `LICENSE-APACHE`, `Cargo.toml:23` at 2aefbeb2) | Code-derived LikeC4 model with a drift check; Rust only |
| [archik](https://github.com/bacharSalleh/archik) | borrow ideas | MIT (`LICENSE` at 108d033) | Hand-written YAML map, browser canvas, PR comment with a node and edge diff; its `drift` checks only that mapped paths exist and that first-level source folders are mapped, plus imports for TS/JS; `init` writes into `CLAUDE.md` |
| [yarramate](https://github.com/yarrasys/yarramate) | borrow ideas | MIT (`LICENSE` at e5173e1) | Hand-written ArchiMate-style YAML model; never reads code (drift is against evidence other tools write); `init` writes into `AGENTS.md` and `CLAUDE.md` |
| [stacklit](https://github.com/glincker/stacklit) | borrow ideas | MIT (`LICENSE` at f6b5c06) | Map derived from code (tree-sitter for TS, Python, Rust; regex for shell) in one committed JSON file; its Action pushes commits by default, and `setup` installs a hook that stages files after every commit |
| [graphruntime](https://github.com/tryboy869/graphruntime) | borrow ideas | MIT (`LICENSE` at b35eb1f) | File-level `graph.json` for 42 languages with `diff` and `validate`; README depth |
| [Corbell](https://github.com/Corbell-AI/Corbell) | borrow ideas | Apache-2.0 (`LICENSE` at 75c7b20) | Multi-repo call graph in SQLite (not reviewed files) with MCP and a local UI; its task export goes to Linear and Jira only; README depth |
| [c4-codebase-architecture](https://github.com/lmammino/c4-codebase-architecture-skill), [c4-architecture](https://github.com/softaworks/agent-toolkit/tree/main/skills/c4-architecture) | borrow ideas | MIT / MIT (read whole) | Agent skills that draft C4 views as Markdown and Mermaid from a repo, with no drift check; ideas for drafting the Mermaid diagrams the verdict keeps (softaworks's writes to its own `docs/architecture/`, not into LLDs) |
| [likec4-dsl skill](https://github.com/likec4/likec4/tree/main/skills/likec4-dsl) | build on (building block) | MIT (LikeC4's `LICENSE` at 9f6ff0c) | LikeC4's own agent skill for writing and validating the model; goes with LikeC4 if AD-320 trials it |
| [easement](https://github.com/mokevnin/easement) | borrow ideas | MIT (`LICENSE` at 8f1b4e9) | Declared components and allowed dependencies, checked on PRs |
| [archlens](https://github.com/tushar-mahalya/archlens) | borrow ideas | MIT (`LICENSE` at b733990) | Markdown architecture pages flagged stale by fingerprinting the code they cite |
| [inixiative/atlas](https://github.com/inixiative/atlas) | borrow ideas | MIT (`LICENSE` at 95f20b8) | In-code annotations checked against a registry, generating `MAP.md`; close to `@spec` |
| [treedocs](https://github.com/DandyLyons/treedocs) | borrow ideas | MIT (`LICENSE` at bc891f1) | YAML map with stale checks; macOS only |
| [arc42-language](https://github.com/docToolchain/arc42-language) | reject | Apache-2.0 title over a modified text (`LICENSE` at ca307e9; H1 unverified) | Checks document consistency, not drift against code |
| [Eidos](https://github.com/mchawa/eidos) | reject | MIT (`LICENSE` at c638ea7) | A second, competing intent system beside LID's: AsciiDoc C4 specs, invariants bound to tests, and change deltas that name components in Eidos's own format only; rejected for the duplication |
| [tiepoint](https://github.com/knoxgraeme/tiepoint) | borrow ideas | AGPL-3.0 (read whole) | Links stories and backlog items to code, not to components |
| [ontology-atlas](https://github.com/wlsdks/ontology-atlas), [projections](https://github.com/githubnext/projections) | borrow ideas | MIT / MIT (read whole) | One Markdown file per concept with MCP; deterministic projections of commits and PRs (a prototype) |
| [SextantDrift](https://github.com/blacktea1526/SextantDrift), [nolli](https://github.com/ioleit/nolli), [archify-pr-action](https://github.com/arvindand/archify-pr-action), [trestle](https://github.com/timimsms/trestle) | borrow ideas | MIT / Apache-2.0 / MIT / MIT (read whole) | PR architecture diffs or diagram-to-path checks; young; README depth |
| [uigraph](https://github.com/uigraph-oss/uigraph), [archilens (saurabh-oss)](https://github.com/saurabh-oss/archilens) | borrow ideas | Apache-2.0 (read whole) / Apache-2.0 notice stub, README says MIT | Repo-file models with PR views; whether archilens works without a model key is unverified |
| [codealmanac](https://github.com/AlmanacCode/codealmanac) | reject | Apache-2.0 (`LICENSE.md` at 0f15350) | Agent-maintained wiki that needs a Codex or Claude runner; its default prompts tell the agent to commit wiki changes (`DEFAULT_AUTO_COMMIT = True`, `src/codealmanac/services/config/models.py:23`) |
| [CodeBoarding](https://github.com/CodeBoarding/CodeBoarding) | borrow ideas | MIT (per the 2026-10-27 note) | Analysis needs an LLM provider (Ollama allowed); unchanged from the earlier note |
| [Structurizr](https://github.com/structurizr/structurizr), [C4-PlantUML](https://github.com/plantuml-stdlib/C4-PlantUML), [c4x](https://github.com/jpantsjoha/c4x-vscode-extension), [Bausteinsicht](https://github.com/docToolchain/Bausteinsicht), [radical.tools](https://github.com/radicaltools/radical.tools) | reject | Apache-2.0 / MIT / MIT (vendor icon packs excluded) / MIT / MIT | Diagram tools that don't derive from code, and state no derived link to it; LikeC4 covers that role with a PR diff action |
| [dependency-cruiser](https://github.com/sverweij/dependency-cruiser), [import-linter](https://github.com/seddonym/import-linter), [tach](https://github.com/gauge-sh/tach), [archy](https://github.com/hslee16/archy), [pacta](https://github.com/pacta-dev/pacta-cli), [archfit](https://github.com/alexei-led/archfit), [archlint](https://github.com/muhammetsafak/archlint) | borrow ideas | MIT / BSD-2-Clause / MIT / MIT / Apache-2.0 / Apache-2.0 / per records | Boundary rules, mostly for one language (archlint and archfit cover several); graphs at most, no reviewed map; `tach show --web` uploads `tach.toml` |
| [stainless-code/codemap](https://github.com/stainless-code/codemap), [JordanCoin/codemap](https://github.com/JordanCoin/codemap), [kogriv/codemap](https://github.com/kogriv/codemap), [codegraph](https://github.com/colbymchenry/codegraph), [code-review-graph](https://github.com/tirth8205/code-review-graph), [codebase-memory-mcp](https://github.com/DeusData/codebase-memory-mcp), [ctx-optimize](https://github.com/muthuishere/ctx-optimize), [graphify](https://github.com/Graphify-Labs/graphify), [RepoMapper](https://github.com/pdavis68/RepoMapper), [repo-map](https://github.com/p4inz-code/repo-map), [madge](https://github.com/pahen/madge), [Aider's repo map](https://github.com/Aider-AI/aider) | reject | MIT; graphify Apache-2.0 (with LICENSE-MIT kept for earlier code) | Derived indexes for agents (N1 only), mostly SQLite or memory, not reviewed files; Aider's map isn't standalone and aider auto-commits by default (`aider/args.py:439-444`) |
| [knossos](https://github.com/AraneaDev/knossos), [systemap](https://github.com/0xfauzi/systemap), [readfirst](https://github.com/jeonghun917/readfirst), [annotated-tree](https://github.com/fredrikolis/annotated-tree), [fondamenta-archcode](https://github.com/talionwar/fondamenta-archcode), [open-vibe-architecture](https://github.com/cybopal/open-vibe-architecture), [wikifier](https://github.com/IronAdamant/wikifier), [chorograph](https://github.com/flancast90/chorograph), [code-map](https://github.com/hungduong-projects/code-map), [vibex](https://github.com/Raja0sama/vibex), [overarch](https://github.com/soulspace-org/overarch), [Repo2C4](https://github.com/rodri-oliveira-dev/Repo2C4), [flowy-docs](https://github.com/feluminais/flowy-docs), [structurizr-site-generatr](https://github.com/avisi-cloud/structurizr-site-generatr), [living-architecture (NTCoding)](https://github.com/NTCoding/living-architecture), [living-architecture (MotleyAI)](https://github.com/MotleyAI/living-architecture), [dekko](https://github.com/aahlijia/dekko), [likec4-discover](https://github.com/LiberiFatali/likec4-discover), [fractal](https://github.com/marcus/fractal), [repolens](https://github.com/CHAPIBUNNY/repolens), [archsteer](https://github.com/einvoice-dev1/archsteer), [ArchMesh](https://github.com/Tranz007/ArchMesh), [floorplan](https://github.com/haydenschmitty/floorplan), [oh-my-mermaid](https://github.com/oh-my-mermaid/oh-my-mermaid), [archify](https://github.com/tt-a1i/archify) | borrow ideas | MIT, Apache-2.0, GPL-3.0 (flowy-docs) or EPL-1.0 (overarch), per records | Each covers part of N1-N4 at README depth, in a narrower or younger form than the candidates above |
| [aoci-code](https://github.com/aoci-spec/aoci-code), [scryer](https://github.com/aklos/scryer), [archboard](https://github.com/miklschmidt/archboard), [VisFlow](https://github.com/VisFlow/visflow-plugin), [GitNexus](https://github.com/abhigyanpatwari/GitNexus), [napi](https://github.com/nanoapi-io/napi) | reject | FSL-1.1-MIT / FSL-1.1-MIT / BUSL-1.1 / proprietary / PolyForm Noncommercial / Sustainable Use | Fail H1 |
| [reposwarm](https://github.com/reposwarm/reposwarm), [gitdiagram](https://github.com/ahmedkhaleel2004/gitdiagram), [lore-map](https://github.com/srihari7070/lore-map), [erode](https://github.com/erode-app/erode), [pr-lens](https://github.com/coldteadotai/pr-lens), [novgraph](https://github.com/Novaya-AI/novgraph), [architecture-intelligence-platform](https://github.com/michaelegner/architecture-intelligence-platform), architecture-dna (no link found) | reject | MIT, Apache-2.0 or none found | Need an AI service, a paid hosted endpoint, or a Neo4j service (fail H2 or H3) |
| [nextjs-mcp-architecture](https://www.npmjs.com/package/nextjs-mcp-architecture), [Graphified](https://github.com/pyshine-labs/graphified) | reject | Source-available commercial agreement / no license file (README says MIT) | Fail H1, or H1 unverified |
| [tetragram](https://www.npmjs.com/package/@uyuutosa/tetragram), [mapping-codebases](https://github.com/oaustegard/claude-skills/tree/main/mapping-codebases) | reject | MIT (package metadata) / MIT | A docs-tree scaffolder that would replace LID's tree (fails N6); a skill whose `_MAP.md` went stale, deprecated by its author in favour of tree-sitting, which keeps no artifact |

Swimm (no link found) and CodeSee (no link found) are hosted services and fail H2 and H3 (search snippets only).

Possible lookalike copy: [Baraa-Suliman/codebase-mapper](https://github.com/Baraa-Suliman/codebase-mapper) reuses [stacklit](https://github.com/glincker/stacklit)'s tagline. It has no code and no license, only download links, so it was rejected and none of its links were followed. The original was found.

License with added or changed terms: [arc42-language](https://github.com/docToolchain/arc42-language)'s `LICENSE` is titled Apache-2.0 but alters several parts of the standard text:

- the definitions of "Work", "Contribution" and "Contributor";
- the patent-termination wording in section 3;
- section 4(d) and the closing paragraph of section 4;
- sections 8 and 9.

No other license read had added terms.

**Matrix for the finalists.** H marks the hard criteria. Values are native, partial, extensible, unsupported or unverified. Clone paths are repo-relative at the commits in the table above.

| Criterion | LID native | [groma.md](https://github.com/MrLesk/groma.md) | [LikeC4](https://github.com/likec4/likec4) + [diff action](https://github.com/novibe-org/likec4-architecture-diff-action) | [Yggdrasil](https://github.com/krzysztofdudek/Yggdrasil) | [faultline](https://github.com/halleylabs/faultline) | [asbuilt](https://github.com/padamson/asbuilt) |
|---|---|---|---|---|---|---|
| H1 OSI license | native (see table) | native (`LICENSE`) | native (`LICENSE` in both) | native (`LICENSE`) | native (`LICENSE`) | native (`LICENSE-MIT`, `LICENSE-APACHE`) |
| H2 repo files are the truth | native (`docs/`, `@spec` lines in code) | partial: Markdown in `groma/` today; `AGENTS.md:264` plans to detach from the filesystem | native (`.c4` text; diff action reads it with `git archive`, `action.yml:1-73`) | native (`.yggdrasil/` YAML) | native (`faultline.yml`, `src/config.ts:93-113`) | native (`model.c4`) |
| H3 local, no account or AI | native (`lidc` binary, `mise.toml:13`) | native: no AI calls; network only to fetch scanners and, when none is on PATH, the Backlog.md CLI (`README.md:149` docs only; `src/work/backlog-cli.ts:13-17`, `src/plugins/management.ts:52-59,82`) | native: `validate` offline; `publish` and `sync` opt-in | native: `--only-deterministic`; reviewers optional (`source/cli/src/cli/check.ts:36-89`) | native: AI not required, but `init` calls Anthropic if a key is set (`src/cli.ts:93-104`, `src/propose.ts:472-509`) | native: no HTTP client in the shipped crates |
| H4 no automatic merge to the default branch | native | native (no git writes in `src`, `packages`; the Action pushes only `groma-previews`) | native | native (commits and checkouts only in a temp clone, `source/cli/src/cli/simulate.ts:684,733`; `init` writes git config and a hook, not commits) | native (read-only git, `src/source.ts`) | native (no git commands) |
| N1 agents read cheaply | partial: one or two greps and an LLD read (AD-318) | native: `groma view <file>` (`docs/agent-instructions/backlog.md:16`) | partial: read `.c4` text | native: `yg owner`, `yg context` | native: MCP answers with token counts (`src/mcp.ts:15-86`) | partial: read `model.c4` (639 lines for 14k lines of code) |
| N2 visualization | partial: hand-written Mermaid in the HLD and LLDs (`docs/high-level-design.md:120` at 72dfa75), diffed in review | native: live map, history comparison, PR previews | native: views plus a PR Mermaid diff (`action.yml:1-73`) | partial: local portal, no PR diff | native: live map, sticky PR comment (`action.yml:34-78`) | partial: renders via `npx likec4` |
| N3 current with the code | partial: `lidc` checks spec IDs, not structure (`mise.toml:73`) | partial: scans refresh code references and keep curation (`docs/component-markdown.md:226-238`); no fail-on-drift command (`src/lint-command.ts:1-34` reports duplicates only) | unsupported: no source parser in the repo (`grep -rl` for parser dependencies across `packages/*/package.json`, per the verification record; LikeC4's validate checks layout, per the 2026-10-27 note) | native: undeclared dependencies fail `yg check` (`source/cli/src/relations/verifier.ts:9-21`) | partial: fails on deny rules, loosened rules and, with `--strict`, new cycles; unmapped files pass (`src/cli.ts:137-162`, `src/maintain.ts:186-226`) | native: `check` diffs the model (`crates/asbuilt/src/commands.rs:261-342`) |
| N4 plain files, git review | native | native (OKF Markdown) | native | native | native | native |
| N5 tasks link to components | partial: tasks cite spec IDs or LLD paths in `references` | native: Backlog.md modified files and refs (`docs/agent-instructions/backlog.md:1-72`); Backlog.md 1.55.3 has `--modified-file` and `--add-ref` | unverified (no task concept found in the README or `action.yml`; no listing made) | unsupported (`docs/nodes.md:192-215` has no link field; listing in the verification record) | unsupported (no task concept in `src/`, per the verification record) | unsupported (no task concept in its crates, per the verification record) |
| N6 coexists with LID and mdBook | native | partial: second C4 hierarchy; its bundled Pages publisher needs its own site | partial: second, hand-kept hierarchy | partial: second hierarchy | partial: second hierarchy | partial: second hierarchy |
| Languages (Py, TS, Rust, sh) | native: `@spec` comments work in any language | partial: no shell scanner (`ls plugins/scanners`) | unsupported: scans no code (same listing as N3) | partial: no shell (docs only, `docs/reviewers.md:270`) | partial: no shell; regex extractors for Python and Rust (`src/lang/extract.ts:29-167`) | partial: Rust only (`crates/asbuilt/src/commands.rs:197-200`) |
| Setup and upkeep | native: pinned in `apm.yml` and `mise.toml` | partial: npm or binary, plus scanner plugins from npm and a global Backlog.md CLI | partial: `npx likec4` (pin it as an npm package) | partial: npm, Node 22 or later, git config and hooks | partial: npm; writes agent configs and hooks | partial: cargo binary; `npx --yes likec4@1.60.0` for render and validate |
| Doesn't commit or push itself | native | partial (the CLI doesn't; the Action pushes a `groma-previews` branch) | native | native | native | native |
| Leaves `AGENTS.md` alone | native | unsupported: writes a managed block (`src/agent-instructions.ts:67-79`) | native | unsupported: writes one by default, with opt-out flags (`source/cli/src/cli/init.ts:1000-1002`) | unsupported: writes it and more (`src/setup.ts:51-243`) | native (opt-in skill) |
| Maturity | native: in use here, with its own spec and checker | partial: 0.7.8 (`package.json`); created 2026-07-11, 4 contributors, one with 1135 commits (GitHub API, read 2026-11-17); self-described prototype (`AGENTS.md:82-89`) | native: LikeC4 is widely used; the diff action is small and young | partial: 6.1.0, 3 contributors, created 2026-02-18 | partial: 0.5.1, 1 contributor, created 2026-09-26 | partial: 0.4.0, 2 contributors |

**Matrix for four more candidates, verified in source.** Paths are repo-relative at archik 108d033, yarramate e5173e1, stacklit f6b5c06 and Eidos c638ea7.

| Criterion | [archik](https://github.com/bacharSalleh/archik) | [yarramate](https://github.com/yarrasys/yarramate) | [stacklit](https://github.com/glincker/stacklit) | [Eidos](https://github.com/mchawa/eidos) |
|---|---|---|---|---|
| H1 OSI license | native (`LICENSE`) | native (`LICENSE`) | native (`LICENSE`) | native (`LICENSE`) |
| H2 repo files are the truth | native (`.archik/main.archik.yaml`, `src/cli/commands/init.ts:121-133`) | native (`.yarramate/architecture/main.yaml`, `src/cli.ts:177-229`) | native (`stacklit.json`, `DEPENDENCIES.md`, `internal/config/config.go:79-82`) | native (AsciiDoc under `eidos/`; SQLite cache gitignored, `src/eidos/core/lifecycle/initializer.py:20-36`) |
| H3 local, no account or AI | native (network only for a loopback probe and `npm view` on `upgrade`, `src/cli/daemon.ts:180-199`, `src/cli/commands/upgrade.ts:46-60`) | native (editor binds 127.0.0.1, `src/adapters/visual/session-server.ts:1443-1451`) | native: no HTTP client in the Go code; the opt-in `init --summary` runs `claude -p` (`internal/summary/cli.go:26-60`) | native: no LLM calls; `doctor` checks PyPI; the optional semantic extra downloads a model (`src/eidos/plugin/version.py:335-395`, `src/eidos/core/index/semantic.py:30-51`) |
| H4 no automatic merge to the default branch | native (read-only git, `src/cli/git.ts:14-52`) | native (read-only git) | partial: the Action's default `auto-commit` mode pushes to the triggering branch (`action/action.yml:7-10,85-98`); `mode: check` doesn't | native (read-only git) |
| N1 agents read cheaply | native (MCP and CLI over the YAML) | unverified: briefs, `ask` and an MCP server exist; output size not measured | native: `derive` prints one line per module (`internal/derive/derive.go:13-80`); size grows with the repo | native: `eidos context`, budgets 300 to 2500 tokens (`src/eidos/core/index/context.py:675-679`) |
| N2 visualization | native: canvas, PR comment with a node and edge diff (`action.yml:102-255`), local SVG diff (`src/cli/commands/diff.ts:41-49`) | partial: local editor, LikeC4 export; the Action writes a job summary only | partial: local map page and Mermaid file; no PR view | partial: static portal with Mermaid C4 views (`src/eidos/portal/builder.py:228-287`); no PR view found |
| N3 current with the code | partial: fails on mapped paths that don't exist, and on unmapped first-level folders under `src/`, `services/`, `packages/` and `apps/` (`src/drift/detector.ts:8,68-124`); imports checked for TS/JS only (`src/drift/edge-drift.ts:38,90-111`) | partial: no parser; it checks evidence documents other tools write, sign-off staleness and file coverage (`src/evidence.ts:40-47`, `src/artifact-coverage.ts:26-84`); `reconcile` exits 0 (`src/cli.ts:146-152`) and only `check --strict` fails | native: derived on each scan; a staleness gate only in the Action's `mode: check` (`action/action.yml:74-84`), since `stacklit diff` always exits 0 (`internal/cli/diff.go:15-71`); `stacklit check` fails on rule violations (`internal/cli/check.go:18-76`) | native: co-change drift over a git diff, failing unless `--warn-only` (`src/eidos/cli/drift_commands.py:195-196`) |
| N4 plain files, git review | native | native | partial: one large JSON file | native |
| N5 tasks link to components | extensible: free-form node `metadata` (`src/domain/schema.ts:101`) | partial: ArchiMate work packages inside the model only (`src/profile.ts:153`) | unsupported (schema listing in the record) | partial: change deltas name component IDs (`assets/schemas/v1/delta/delta.schema.yaml:77-192`), in Eidos's own format only |
| N6 coexists with LID and mdBook | unverified: a second hierarchy, and `init` writes a `CLAUDE.md` block; its Markdown reader (`src/io/markdown.ts`) wasn't read | partial: second hierarchy | unverified: a derived index beside the docs; coexistence not checked further | partial: a second, competing intent system (its own spec tree and IDs, `src/eidos/core/spec/models.py:9-28`) beside LID's |
| Languages (Py, TS, Rust, sh) | partial: TS/JS only for imports | extensible: parses no code itself; code facts come through adapters (`src/adapters/graphify.ts:1-40`) | native: tree-sitter for TS, Python and Rust; regex for shell (`internal/parser/treesitter.go:17-23,146-147`) | partial: no shell (`src/eidos/core/index/ast_indexer.py:818-839`) |
| Doesn't commit or push itself | native | native | unsupported by default: the Action pushes; the post-commit hook runs `git add` (`internal/git/hooks.go:13-16`) | native |
| Leaves `AGENTS.md` alone | partial: writes `CLAUDE.md`, not `AGENTS.md` (`src/cli/commands/init.ts:186-248`) | unsupported: writes both, opt out with `--no-pointer` (`src/cli.ts:178-273`) | unsupported: `setup` writes both and `.mcp.json` (`internal/setup/tools.go:49-94`) | partial: only `plugin install` writes them (`src/eidos/plugin/installer.py:1405-1423`) |
| Maturity | partial: v0.22.2, 3 contributors, created 2026-04-26 | partial: v1.41.1, pre-release, 2 contributors, created 2026-07-28 | partial: v0.5.0, 5 contributors, created 2026-04-09 | partial: v0.24.5, 1 contributor, created 2026-10-11 |

**Matrix for the next candidates, from README reads.** Values here are docs only, and "unverified" means the README didn't say.

| Criterion | [easement](https://github.com/mokevnin/easement) | [archlens](https://github.com/tushar-mahalya/archlens) | [inixiative/atlas](https://github.com/inixiative/atlas) | [SextantDrift](https://github.com/blacktea1526/SextantDrift) | [graphruntime](https://github.com/tryboy869/graphruntime) |
|---|---|---|---|---|---|
| H1 | native | native | native | native | native |
| H2 | native (`easement.yml`) | native (Markdown) | native | unverified | native (`graph.json`) |
| H3 | native | partial: pages written by an agent | native | unverified | partial: LLM needed for explain, goal and merge only |
| N1 | partial (a skill) | native (405-token page map) | native (`MAP.md`) | native (MCP) | partial (`inspect`) |
| N2 | unverified | partial | unverified (none described) | native (red and green diff) | partial (`diff` of two graph files; no PR view) |
| N3 | native (CI gate) | native (stale fingerprints) | native (CI freshness) | native | native (`diff`, `validate`) |
| N4 | native | native | native | unverified | partial (one JSON file) |
| N5 | unverified | unverified | unverified | unverified | unverified |
| N6 | unverified | partial (own pages directory) | partial (annotations like `@spec`) | unverified | unverified |

**Blends considered:**

- **LID native + the lookup rule** (the verdict).
  - Covers use 1 with no new tool.
  - Covers use 2 in part, through Mermaid diagrams kept in the design docs.
  - Covers use 3 in part: tasks point at segments, but nothing lists a component's tasks.
- **LID native + groma.md.**
  - Covers everything on paper.
  - Costs a second hierarchy to curate, a modified-file record kept up after every edit, an `AGENTS.md` block, a possible global Backlog.md install, and a prototype whose format can change.
  - Worth a trial (AD-320) only where code-derived diffs matter.
- **LID native + LikeC4 + diff action.**
  - Gives a reviewed picture with PR diffs, but no link to code.
  - Drift would need asbuilt (Rust), Archtrace (TS/JS), or a custom check against `@spec` segments.
  - The fallback if a hand-written model is enough.
- **LID native + a Yggdrasil- or easement-style relation check.** A segment may depend only on the segments its LLD names, and the empty `docs/arrows/index.yaml` (`arrows: {}`) is where declared relations would go. This borrows the best idea from Yggdrasil and easement, but it is new work with no current demand.

**Scenario walk.** Each finalist and blend, through the three common uses first, then four change scenarios.

| Scenario | LID + lookup rule (verdict) | LID + [groma.md](https://github.com/MrLesk/groma.md) | LID + [LikeC4](https://github.com/likec4/likec4) + [diff action](https://github.com/novibe-org/likec4-architecture-diff-action) | [Yggdrasil](https://github.com/krzysztofdudek/Yggdrasil) | [faultline](https://github.com/halleylabs/faultline) | [asbuilt](https://github.com/padamson/asbuilt) |
|---|---|---|---|---|---|---|
| Use 1: an agent finds the owner of `skills/prior-art-search/scripts/harvest.py` | `git grep -n "@spec"` gives `PRIOR-SCR-001` (line 18); a second grep finds `docs/intent/prior-art-search/`; read that LLD | `groma view <file>`, once someone has curated the map | No file-level answer | `yg owner <file>` after the nodes map the file | MCP `place` or `map` after `faultline.yml` names the system | No Python front-end |
| Use 1, a file with no `@spec` (`.github/workflows/check.yml`) | HLD Components table, then grep the path in LLDs (`check-workflow-design.md` names it) | Owned only if a scanner reads YAML workflows; none listed | No | Only if a node maps it | Glob in `faultline.yml` | No |
| Use 2: a reviewer checks what an agent's PR did to the structure | Diff of the LLD and Mermaid changes; nothing if the PR changed code only | A preview link in a PR comment, through the repo's own publisher if Pages hosts the mdBook | Inline Mermaid diff, but only of hand-edited views | No PR view | Sticky comment with the structural diff | Its Action fails on drift; no picture |
| Use 3: a task shows its components | `references` holds spec IDs or LLD paths | The agent records every modified file in the task after each edit (`docs/agent-instructions/backlog.md:23-37`) | No | No | No | No |
| A new requirement adds a component | New LLD, spec IDs and diagram edit through LID's arrow | A scan adds a stand-alone component; an agent folds it in with `groma edit --combine` and commits `groma/` with the code | Hand edit to the `.c4` model | Add a node and relations, or `yg check` fails | Add a system glob, or the files go unmapped | A survey adds it; `check` fails until the model is committed |
| A fresh CI clone | Nothing to install beyond the pinned tools | npm or a binary, plus scanner plugins from npm | `npx likec4` (pin it as an npm package) | npm package, Node 22 or later | npm package | cargo binary, plus `npx likec4` to render |
| Renovate bumps the tool | LID and lidc bumps follow the LID exception in the HLD | A minor release may change the stored format with no migration (`AGENTS.md:87`) | A pinned npm package Renovate already handles | npm bump; 28 commands to re-check | npm bump | cargo bump |
| A reader opens the map on GitHub | Rendered Markdown and Mermaid | Rendered Markdown per element; the map itself needs `groma web` | `.c4` text; views need the CLI or a site | YAML | YAML | `.c4` text |

## Limitations checked in source

Verified:

- **LID native** (this repo at 72dfa75):
  - `@spec` coverage. *verified by listing (`git grep -c "@spec" 72dfa75 -- ':!*.md'`: 697 lines in 82 files)*
  - `mise run lid` runs `lidc check --only reverse-orphan,coverage,spec-id-format --fail-on warning`. *verified in source (`mise.toml:72-73`)*
  - The HLD's Mermaid component diagram and Components table. *verified in source (`docs/high-level-design.md:120,159`)*
  - Backlog.md 1.55.3 has `--add-ref` and `--modified-file`. *verified by running the pinned CLI's `backlog task edit --help`*
- **[groma.md](https://github.com/MrLesk/groma.md)** (at 587a806):
  - `init` writes a managed block into `AGENTS.md` and `CLAUDE.md`. *verified in source (`src/agent-instructions.ts:6-13,67-79`; caller `src/initialize.ts:110`)*
  - It runs `backlog init` only if Backlog.md is selected and not yet initialized. *verified in source (`src/init-command.ts:142-154`)*
  - When Backlog.md is selected, it installs a global Backlog.md CLI if none is on PATH, and `groma plugin update` upgrades it. *verified in source (`src/work/backlog-cli.ts:13-17`, `src/plugins/management.ts:52-59,82,116`)*
  - It calls itself an experimental prototype with no compatibility promises, no migrations and no legacy formats. *verified in source (`AGENTS.md:82-89`)*
  - It plans to detach from the filesystem. *verified in source (`AGENTS.md:264`)*
  - It has no shell scanner. *verified by listing (`ls plugins/scanners`)*
  - Its source has no git commit or push. *verified by listing (`grep -rn "'commit'\|'push'" src packages --include=*.ts`)*
  - `groma lint` reports only possible duplicate logic. *verified in source (`src/lint-command.ts:1-34`)*
  - Scans keep curated text and refresh code references. *docs only, at the pinned commit (`docs/component-markdown.md:226-238,311-329`)*
- **[groma.md-action](https://github.com/MrLesk/groma.md-action)** (at 8529a2e): its bundled publisher refuses to replace another Pages site, and an existing site can run its own publisher. *docs only (`README.md:17-29`)*
- **[faultline](https://github.com/halleylabs/faultline)** (at c983fdcb):
  - `init` calls Anthropic whenever the key is set. *verified in source (`src/cli.ts:93-104`, `src/propose.ts:472-509`)*
  - `setup` writes agent files, hooks and a pre-commit hook without asking. *verified in source (`src/setup.ts:51-243`)*
  - Unmapped files don't fail `check`. *verified in source (`src/cli.ts:137-162`, `src/maintain.ts:186-226`)*
- **[Yggdrasil](https://github.com/krzysztofdudek/Yggdrasil)** (at 45d1a51c):
  - `init` writes git merge drivers and a post-merge hook without confirming. *verified in source (`source/cli/src/cli/init-scaffold.ts:205-250`)*
  - Undeclared relations fail `yg check`. *verified in source (`source/cli/src/relations/verifier.ts:9-21`)*
- **[asbuilt](https://github.com/padamson/asbuilt)** (at 2aefbeb2):
  - It has a Rust front-end only. *verified in source (`crates/asbuilt/src/commands.rs:197-200`)*
  - `check` diffs the generated model. *verified in source (`crates/asbuilt/src/commands.rs:261-342`, `crates/asbuilt-core/src/check.rs:25-36`)*
- **[LikeC4](https://github.com/likec4/likec4)** (at 9f6ff0cd): `build` and `serve` check npm for updates daily outside CI. *verified in source (`packages/likec4/src/cli/check-update/utils.ts:18-57`)*
- **[likec4-architecture-diff-action](https://github.com/novibe-org/likec4-architecture-diff-action)** (at 7a92157d) needs only the GitHub token and npm. *verified in source (`action.yml:1-73`)*
- **[codealmanac](https://github.com/AlmanacCode/codealmanac)**: `DEFAULT_AUTO_COMMIT = True`, a prompt policy. codealmanac itself doesn't commit. *verified in source (`src/codealmanac/services/config/models.py:23` at 0f15350)*
- **[OpenKnowledge](https://github.com/inkeep/open-knowledge)** is GPL-3.0 and ships an OKF skill pack. *verified (`LICENSE`, `packages/server/assets/skills/packs/okf/SKILL.md` at d04de0e)*
- **Licenses read whole:**
  - groma.md, groma.md-action, LikeC4, likec4-architecture-diff-action, asbuilt (both files), Yggdrasil, faultline and OpenKnowledge;
  - 23 further candidates, among them [archik](https://github.com/bacharSalleh/archik), [yarramate](https://github.com/yarrasys/yarramate), [stacklit](https://github.com/glincker/stacklit), [easement](https://github.com/mokevnin/easement), [archlens](https://github.com/tushar-mahalya/archlens), [inixiative/atlas](https://github.com/inixiative/atlas), [treedocs](https://github.com/DandyLyons/treedocs), [arc42-language](https://github.com/docToolchain/arc42-language), [codealmanac](https://github.com/AlmanacCode/codealmanac), [Eidos](https://github.com/mchawa/eidos), [SextantDrift](https://github.com/blacktea1526/SextantDrift), [nolli](https://github.com/ioleit/nolli), [archify-pr-action](https://github.com/arvindand/archify-pr-action), [trestle](https://github.com/timimsms/trestle) and [graphify](https://github.com/Graphify-Labs/graphify).
  - [archilens (saurabh-oss)](https://github.com/saurabh-oss/archilens)'s `LICENSE` is a 15-line Apache-2.0 header stub, while its README says MIT (contents API, read 2026-11-17).
  - The round 9-10 candidates' licenses, read whole on 2026-11-18. None adds or changes a term:
    - [uigraph](https://github.com/uigraph-oss/uigraph), [tiepoint](https://github.com/knoxgraeme/tiepoint), [ontology-atlas](https://github.com/wlsdks/ontology-atlas), [projections](https://github.com/githubnext/projections), [floorplan](https://github.com/haydenschmitty/floorplan), [oh-my-mermaid](https://github.com/oh-my-mermaid/oh-my-mermaid) and [radical.tools](https://github.com/radicaltools/radical.tools);
    - [archify](https://github.com/tt-a1i/archify), [ctx-optimize](https://github.com/muthuishere/ctx-optimize), [ArchMesh](https://github.com/Tranz007/ArchMesh), [c4x](https://github.com/jpantsjoha/c4x-vscode-extension), [archy](https://github.com/hslee16/archy) and [pacta](https://github.com/pacta-dev/pacta-cli);
    - the code indexes in the reject row, and [dekko](https://github.com/aahlijia/dekko), [likec4-discover](https://github.com/LiberiFatali/likec4-discover), [fractal](https://github.com/marcus/fractal) and [repolens](https://github.com/CHAPIBUNNY/repolens).

    Their NOTICE files carve out bundled third-party assets (c4x's vendor icon packs, fractal's font), or keep parts under MIT ([archify](https://github.com/tt-a1i/archify)).
- **[archik](https://github.com/bacharSalleh/archik), [yarramate](https://github.com/yarrasys/yarramate), [stacklit](https://github.com/glincker/stacklit) and [Eidos](https://github.com/mchawa/eidos)** (at the commits above): the cells of their matrix. *verified in source*. Each README or help text claims more than the code does:
  - archik's README says `drift` shows that the model "matches the code". It checks only path existence and unmapped first-level folders, plus imports for TS/JS (`src/drift/detector.ts:8,68-124`).
  - yarramate's "drift" is against evidence documents, not code (`src/evidence.ts:40-43`).
  - stacklit's "no LLM" has an opt-in `claude -p` path (`internal/summary/cli.go:26-60`).
  - Eidos's `context` help states smaller token budgets than its code uses (`src/eidos/cli/context_command.py:140` against `src/eidos/core/index/context.py:675-679`).

Could not verify:

- **[Yggdrasil](https://github.com/krzysztofdudek/Yggdrasil)'s language list.** It lives in the external `@chrisdudek/runes` package. *docs only*
- **[faultline](https://github.com/halleylabs/faultline)'s claim of about 50 tokens per agent answer**, and the size of [groma.md](https://github.com/MrLesk/groma.md)'s `groma view` output. Neither was measured.
- **Every candidate below the six finalists, except archik, yarramate, stacklit and Eidos, and the four skills read as skill source.** Their claims are docs only, from README reads that were often head-plus-keyword.
- **Two licenses in the reject rows:** [novgraph](https://github.com/Novaya-AI/novgraph) and [pr-lens](https://github.com/coldteadotai/pr-lens) were read at header depth only.
- **Two licenses:** stratalint (no link found) returned 404 from PyPI's JSON API. [tetragram](https://www.npmjs.com/package/@uyuutosa/tetragram)'s MIT rests on its package metadata, since its repository returns 404.
- **Hosted services** (IcePanel, Structurizr cloud, Swimm, CodeSee and others; no links found) were seen only through search snippets. All fail H2 or H3 as services.

## Papers

| Paper | Read state | Evidence strength | Review status | Class | Claim (tag) |
|---|---|---|---|---|---|
| [Formal Architecture Descriptors as Navigation Primitives for AI Coding Agents](https://arxiv.org/abs/2604.13108) | read in part (abstract, results, threats, conclusion) | experiment | preprint | borrow ideas | A descriptor cut navigation steps 33-44% on 24 localization tasks in a 22K-line project. The effect was smaller with a stronger model. No significant difference between formats was detected (low power). The authors expect larger gains on bigger repos, untested (paper-reported) |
| [How Should Agents See Code?](https://arxiv.org/abs/2611.07286) | read in part (abstract, method, results, threats) | experiment | preprint | borrow ideas | Map views raised fault-localization recall with 25-39% fewer tokens. SWE-bench Pro resolution was mixed, and test generation gained little. Map-build cost was excluded (paper-reported) |
| [RepoAtlas](https://arxiv.org/abs/2609.16936) | read in part (abstract, results) | experiment | preprint | borrow ideas | Evolving repository views raised the SWE-bench Verified resolve rate 2.4 points over the strongest graph baseline, with 5.8% fewer input tokens (paper-reported) |
| [Evaluating AGENTS.md](https://arxiv.org/abs/2602.11988) | read in part (abstract, intro, 4.2, cost) | experiment | preprint | borrow ideas | Context files didn't generally raise success, and added about 20% cost. The repository overviews in them weren't helpful (paper-reported) |
| [Do Context Files Help Coding Agents? A Two-Agent Ablation Study on Real Repositories](https://doi.org/10.18653/2026.realm-1.5) | abstract only | experiment | peer-reviewed | borrow ideas | The abstract reports no measurable correctness effect from context strategy across 288 runs (paper-reported) |
| [CodeCompass](https://arxiv.org/abs/2602.20048) | read in part (abstract, introduction) | weak experiment | preprint | borrow ideas | A dependency-graph tool helped on hidden-dependency tasks, while BM25 was best on keyword-findable ones. Agents used the tool in 42% of trials (paper-reported) |
| [Repository Intelligence Graph](https://arxiv.org/abs/2601.10112) | read in part (abstract, scope) | experiment | preprint | borrow ideas | A deterministic component graph from build files improved accuracy 12.2% and cut completion time 53.9%, on 30 build-structure questions per repo across 8 repos (paper-reported) |
| [LLM Agents Can See Code Repositories](https://arxiv.org/abs/2606.14061) | read in part (abstract, method) | experiment | peer-reviewed | borrow ideas | A visual structure graph alongside text cut input tokens by up to 26%, with resolution kept or improved; the body shows one 2.2-point dip (paper-reported) |
| [Theory of Code Space](https://arxiv.org/abs/2603.00601) | read in part (abstract, results) | experiment | preprint | borrow ideas | Agents build architecture maps of a codebase unevenly. It measures building a map, not the benefit of being given one (paper-reported) |
| [The Code of Theseus](https://arxiv.org/abs/2610.20068) | read in part (abstract, setup) | experiment | preprint | borrow ideas | Recovered architecture documents didn't significantly change an agent's held-out pass rate (paper-reported) |
| [Rasoi: Visual Diffs for Evaluating Structural Changes Made by Coding Agents](https://arxiv.org/abs/2611.16293) | read in part (abstract, design rationale, findings headings and Likert summaries) | qualitative study | preprint | borrow ideas | 12 developers used a C4-based diff for a week. They reported it helped them judge scope and spot unexpected restructuring (paper-reported) |
| [A Study on the Effect of Traceability Links in Software Maintenance](https://doi.org/10.1109/access.2013.2286822) | read in part (abstract, sections I-IV.A, results and conclusion passages on accuracy) | experiment | peer-reviewed | borrow ideas | 28 subjects did five maintenance tasks. Those given trace links were significantly more accurate, "86.06% more accurate" as a relative gain; speed differed significantly on one task only (paper-reported) |
| [Who's Who? LLM-assisted Software Traceability with Architecture Entity Recognition](https://publikationen.bibliothek.kit.edu/1000191991) | read in part (abstract, evaluation setup) | experiment | peer-reviewed | borrow ideas | Documentation-to-code trace links at F1 0.86 from text and code alone (paper-reported) |
| [Sentinel](https://doi.org/10.1145/3786335.3813195) | abstract only | observational study | peer-reviewed | borrow ideas | The abstract reports that agents checking commits against ADRs and design docs found 18 drift instances, at 83% true positives (paper-reported) |
| [Recovering Software Architecture Intent from Historical Work Items using Generative AI](https://arxiv.org/abs/2608.28403) | abstract only | qualitative study | preprint | borrow ideas | The abstract reports C4 diagrams generated from work items, rated accurate and useful by practitioners (paper-reported) |
| [LocAgent](https://arxiv.org/abs/2503.09089) | abstract only | experiment | peer-reviewed | borrow ideas | The abstract reports up to 92.7% file-level localization from a code graph (paper-reported) |

Published artifacts weren't evaluated as software: [How-Should-Agents-See-Code](https://github.com/MelikaSepidband/How-Should-Agents-See-Code), [Spade](https://github.com/Greenfuze/Spade), [research-codecompass](https://github.com/tpaip607/research-codecompass), [tocs](https://github.com/che-shr-cat/tocs), [LocAgent](https://github.com/gersteinlab/LocAgent), [RepoGraph](https://github.com/ozyyshr/RepoGraph) and [code-theseus](https://github.com/SasCezar/code-theseus).

No recent controlled experiment was found on C4 or component diagrams for human comprehension (N2). The older diagram experiments are those the 2026-10-27 note cites.

Some of the paper data came from [Semantic Scholar](https://www.semanticscholar.org/).

## Worth retrieving manually

- [Do Context Files Help Coding Agents? A Two-Agent Ablation Study on Real Repositories](https://doi.org/10.18653/2026.realm-1.5), DOI 10.18653/2026.realm-1.5.
  - Why it matters: its abstract reports no effect from context files, which is peer-reviewed counter-evidence on N1, and so on the verdict.
  - How to get it: the ACL Anthology page, or ask the authors.

## Coverage ledger

| Route | State | Queries or reason |
|---|---|---|
| The stack itself | searched | `docs/high-level-design.md` (Components table, Mermaid diagram, tenets), `docs/intent/`, `docs/arrows/index.yaml`, `git grep "@spec"`, `mise.toml` (`lid` task), `apm.yml`, `lidc --help`, `backlog task edit --help` (1.55.3) |
| Earlier notes and decisions | searched | Notes from 2026-10-23 (progressive disclosure, docs site), 2026-10-27 (review burden), 2026-11-06 (federated knowledge, decision records), 2026-11-12 (task management), 2026-11-16 (cross-repo coordination); `grep -rn -i` for openknowledge, okf, likec4, structurizr, codeboarding and mermaid over `docs/` and `backlog/` |
| GitHub repository search | searched | Round 1, both sorts: "architecture map", "c4 model", "architecture diagram code", "architecture drift", "codebase map agents", "living architecture". Later rounds, by stars, including: "architecture as markdown", "repo map", "code map agent", "architecture knowledge graph", "architecture diff pull request", "c4 scanner", "component ownership", "module boundaries", "architecture conformance", "arc42 generator", "dependency graph visualization", "architecture snapshot", "dependency structure matrix", "architecture fitness function", "code atlas" |
| GitHub topics | searched | Lookups: c4, architecture-as-code, architecture-diagram, codebase-map, architecture-documentation, drift-detection, docs-as-code, architecture-enforcement, arc42, repo-map, likec4, architecture-governance, architecture-fitness, code-knowledge-graph, diagrams-as-code. Searches (round 1 both sorts): c4-model, c4model, architecture-as-code, codebase-map, codebase-mapping, architecture-documentation. Later: architecture-enforcement, import-boundaries, arc42, likec4, repo-map, repository-map, docs-as-code, architecture-drift, code-knowledge-graph, documentation-as-code, diagrams-as-code |
| GitHub code search | searched | `groma.md` in READMEs; `okf_version groma`; `filename:likec4.config.json`; `filename:workspace.dsl AGENTS.md`; "architecture.md agents drift"; "likec4 structurizr architecture-as-code" |
| GitLab search | searched | "architecture map", "c4 model", "architecture as code", `topic=c4-model`; only mirrors and unrelated projects |
| Codeberg search | excluded | Blocks scripted clients; searched instead with `site:codeberg.org architecture map c4 model` (one course page, no tools) |
| npm | searched | "architecture map", "c4 model", "architecture as code", "codebase map", "architecture drift", "repo map agents"; registry lookups for the candidates found |
| PyPI | searched | Search page not requested (it blocks scripted clients); `site:pypi.org` web searches; JSON API for pacta, archy, stratalint (404), forma-arch, archtest, sextant-drift, codemap, eidos, eidos-ai, archsteer, wingbox, evident-map |
| crates.io | searched | "architecture", "c4", "architecture-map", "c4-model" |
| lib.rs | excluded | Blocks scripted clients; crates.io searched instead |
| libraries.io | searched | "architecture map", "c4 model", "architecture drift", sorted by latest release |
| Homebrew formulae | searched | `jq` over `c4\|architecture\|structurizr\|likec4\|codemap\|repo.?map\|diagram`: likec4, structurizr-cli, overarch, plantuml, d2, calm-cli, adr-tools |
| nixpkgs | excluded | Condition unmet: no brotli decompressor installed |
| LibHunt | searched | Alternatives pages for groma.md, likec4, fallow and the round-9 seeds; structurizr and C4-PlantUML returned 404 |
| AUR | searched | "c4 model", "architecture diagram", "structurizr" |
| ecosyste.ms | searched | Keywords c4, architecture, c4-model, architecture-diagram; the graphruntime and tetragram hits read for AD-319 |
| GitLab search (eidosmd) | searched | `projects?search=` eidosmd, eidos-md, eidos, "eidos md"; `groups?search=eidosmd`; no such project |
| Cross-language equivalents | searched | For asbuilt's Rust-only LikeC4 generator: "likec4 generator", "likec4 from code", "c4 model generator python", "c4 model generator typescript", "structurizr from code", "c4 model from source" (no results). The generators already found are [c4tree](https://github.com/jose-villegas/c4tree) (C/C++) and [Repo2C4](https://github.com/rodri-oliveira-dev/Repo2C4) (.NET); [Archtrace](https://github.com/AdityaNerpagar/Archtrace) checks TS/JS imports against a hand-written model. None was found for Python |
| Awesome lists | searched | "awesome software architecture tools", "awesome architecture as code", "awesome c4 model tools", "awesome code maps for AI agents"; read glue-tools-ai's and jyck613's awesome-codebase-intelligence, mellson/awesome-diagramming, mehdihadeli/awesome-software-architecture, noahbald/awesome-architecture-md; for AD-319, CodeBoarding/awesome-architecture-mds and hesreallyhim/awesome-claude-code, by grep and section reads. No dedicated C4 or architecture-as-code list exists |
| alternativeto.net | excluded | Cloudflare challenge to automated clients; "alternatives to" web searches used instead |
| General web search | searched | "groma.md architecture map review comparison alternatives", "LikeC4 vs Structurizr", "keeping architecture docs in sync with code AI agents", "architecture diagram in pull request github action", "alternatives to codebase-memory-mcp", "alternatives to graphify", "alternatives to code-review-graph", lookups for Eidos, stratalint and kogriv codemap; for AD-319, "Corbell architecture code graph tool for coding agents GitHub" and "Graphified code graph architecture tool GitHub". No independent review of groma.md was found |
| Hosted services | searched | IcePanel, Structurizr cloud, Swimm, CodeSee, Archyl, Archaic AI and Architecto, through snippets; all fail H2 or H3 |
| Skill directories, Claude Code plugin marketplaces, MCP Registry | searched (beyond the triggers) | Not triggered, since the need is a map, not a skill or server. They were searched anyway because many candidates ship as skills or MCP servers. skills.sh: "architecture", "c4", "codebase map". Marketplace file: `jq` for architecture, c4, codebase map, diagram. MCP Registry: "architecture", "c4", "codemap", then architecture-dna, architecture-intelligence-platform and nextjs for AD-319. skills.sh again for AD-319: "c4", "architecture", "codebase map", "likec4-dsl". No in-repo map tool found that wasn't found elsewhere |
| PulseMCP, Anthropic's skills repo, awesome lists for agent skills, GitHub topics for agent skills | excluded | Not triggered: the need is a map, not an agent skill, plugin or MCP server |
| aitoolnet.com | searched | Sitemap slugs grepped for architecture, c4, codebase, codemap, diagram; only diagram generators and tools already found |
| arXiv | searched | Through the harvester, for example `"repository map" AND agent`, `"architecture documentation" AND traceability`, `"architectural drift" AND LLM`, `"architecture diagram" AND comprehension`, `"code knowledge graph" AND "coding agent"`. Recent preprints sorted by date were sent without the harvester, which has no sort option ([AD-322](../../backlog/tasks/ad-322%20-%20Add-a-newest-first-sort-to-the-harvesters-arXiv-search.md)) |
| OpenAlex | searched | Keyword searches on repository maps, architecture documentation, diagram comprehension experiments, erosion, recovery, traceability and task-to-component mapping; citation and reference lookups from the main seeds; open-access lookups for 9 DOIs |
| Semantic Scholar | searched | Recommendations from 2601.10112, 2603.00601, 2611.07286, 2602.11988, 2604.13108, 2606.09090 |
| OpenAIRE | searched | "repository map coding agent", "code graph repository agent localization", "architecture documentation code traceability" |
| Hugging Face papers | searched | "repository map coding agent", "code graph repository agent", "software architecture documentation LLM" |
| papers.cool | searched | "repository map coding agent architecture", "architecture documentation code consistency LLM" |
| Crossref | searched | "architecture erosion drift detection software", "software architecture diagram comprehension experiment" |
| Zenodo | excluded | Only for a paper's artifact; its robots.txt disallows `/api` |
| Europe PMC | excluded | Not a life-science need |

## Snowball rounds

1. **Round 1:** the six phrasings and six topics found [groma.md-action](https://github.com/MrLesk/groma.md-action), [LikeC4](https://github.com/likec4/likec4), [Structurizr](https://github.com/structurizr/structurizr), [faultline](https://github.com/halleylabs/faultline), [archlens](https://github.com/tushar-mahalya/archlens), [easement](https://github.com/mokevnin/easement), [treedocs](https://github.com/DandyLyons/treedocs), [inixiative/atlas](https://github.com/inixiative/atlas), [readfirst](https://github.com/jeonghun917/readfirst) and the other round-1 rows above.
2. **Round 2:** topic variants and fresh wordings added [Yggdrasil](https://github.com/krzysztofdudek/Yggdrasil), [yarramate](https://github.com/yarrasys/yarramate), [stacklit](https://github.com/glincker/stacklit), [arc42-language](https://github.com/docToolchain/arc42-language), [likec4-architecture-diff-action](https://github.com/novibe-org/likec4-architecture-diff-action), [archlint](https://github.com/muhammetsafak/archlint), [dekko](https://github.com/aahlijia/dekko), [likec4-discover](https://github.com/LiberiFatali/likec4-discover) and [fractal](https://github.com/marcus/fractal).
3. **Rounds 3-6:**
   - On GitHub: [archsteer](https://github.com/einvoice-dev1/archsteer) and [repolens](https://github.com/CHAPIBUNNY/repolens), then [archik](https://github.com/bacharSalleh/archik), [archfit](https://github.com/alexei-led/archfit) and [codealmanac](https://github.com/AlmanacCode/codealmanac) from LibHunt's alternatives pages.
   - From registries and the web: [asbuilt](https://github.com/padamson/asbuilt), [Archtrace](https://github.com/AdityaNerpagar/Archtrace) and other drift checkers.
4. **Round 7:** GitHub added nothing serious. Leads from the registry and web routes in earlier rounds were still unread.
5. **Round 8** (its finds are recorded as round-9 seeds): reading those leads, and the awesome lists, added [Eidos](https://github.com/mchawa/eidos), [kogriv/codemap](https://github.com/kogriv/codemap), [SextantDrift](https://github.com/blacktea1526/SextantDrift), [archy](https://github.com/hslee16/archy), [pacta](https://github.com/pacta-dev/pacta-cli), [graphify](https://github.com/Graphify-Labs/graphify), [nolli](https://github.com/ioleit/nolli), [archify-pr-action](https://github.com/arvindand/archify-pr-action), [trestle](https://github.com/timimsms/trestle), [ArchMesh](https://github.com/Tranz007/ArchMesh), [c4x](https://github.com/jpantsjoha/c4x-vscode-extension) and the derived code indexes.
6. **Round 9:** seeded from round 8, it added [uigraph](https://github.com/uigraph-oss/uigraph), [ontology-atlas](https://github.com/wlsdks/ontology-atlas), [tiepoint](https://github.com/knoxgraeme/tiepoint), [radical.tools](https://github.com/radicaltools/radical.tools), [projections](https://github.com/githubnext/projections), [floorplan](https://github.com/haydenschmitty/floorplan), [oh-my-mermaid](https://github.com/oh-my-mermaid/oh-my-mermaid) and [archilens (saurabh-oss)](https://github.com/saurabh-oss/archilens).
7. **Round 10 (the cap):** one more serious candidate, [ctx-optimize](https://github.com/muthuishere/ctx-optimize), a derived index that serves N1 only.

The search stopped at the 10-round cap while round 10 still added a serious candidate. That doesn't block this verdict, which isn't **build**.

The late rounds added variants of shapes already covered: drift-checked declared models, derived code indexes and PR diff Actions. Two late candidates were flagged as possibly verdict-changing, and neither holds up:

- [Eidos](https://github.com/mchawa/eidos), now read in source, is a second intent system competing with LID's tree.
- [tiepoint](https://github.com/knoxgraeme/tiepoint) links to stories, not components.

**Leads read after the cap** ([AD-319](../../backlog/tasks/ad-319%20-%20Read-the-open-leads-from-the-2026-11-17-architecture-maps-search.md)). Each candidate lead the cap left open is now read and classified in the table above. None changes the verdict:

- [archik](https://github.com/bacharSalleh/archik), [yarramate](https://github.com/yarrasys/yarramate), [stacklit](https://github.com/glincker/stacklit) and [Eidos](https://github.com/mchawa/eidos) were read in source. Each does less than its README says.
- The MCP Registry hits were rejected:
  - architecture-dna (no link found) is a paid hosted endpoint.
  - [architecture-intelligence-platform](https://github.com/michaelegner/architecture-intelligence-platform) needs Neo4j.
  - [nextjs-mcp-architecture](https://www.npmjs.com/package/nextjs-mcp-architecture) is source-available, not open source.
- The ecosyste.ms hits: [graphruntime](https://github.com/tryboy869/graphruntime) is borrow ideas, and [tetragram](https://www.npmjs.com/package/@uyuutosa/tetragram) is rejected.
- The skills.sh skills:
  - [c4-codebase-architecture](https://github.com/lmammino/c4-codebase-architecture-skill) and [c4-architecture](https://github.com/softaworks/agent-toolkit/tree/main/skills/c4-architecture) draft C4 views in Mermaid.
  - [likec4-dsl](https://github.com/likec4/likec4/tree/main/skills/likec4-dsl) goes with LikeC4.
  - [mapping-codebases](https://github.com/oaustegard/claude-skills/tree/main/mapping-codebases) is deprecated.
- The two lists were read by grep and section reads:
  - [awesome-architecture-mds](https://github.com/CodeBoarding/awesome-architecture-mds) lists generated `architecture.md` files, and its only tool is CodeBoarding.
  - [awesome-claude-code](https://github.com/hesreallyhim/awesome-claude-code) added the further leads below.
- "eidosmd" isn't a GitLab project. The name comes from file names inside Eidos.
- [Corbell](https://github.com/Corbell-AI/Corbell) is borrow ideas. [Graphified](https://github.com/pyshine-labs/graphified) has no license file.

Further names these leads turned up are not pursued. The late rounds and these leads kept adding variants of shapes already covered, and none was described as linking repo task files to components:

- from skills.sh: c4-diff, system-atlas, nexus-mapper, c4-structurizr, likec4-architecture, codebase-domain-map, cartography and codebase-study-guide (no links found);
- from awesome-claude-code: [cxpak](https://github.com/Barnett-Studios/cxpak), [faf-cli](https://github.com/Wolfe-Jam/faf-cli), [Upkeep](https://github.com/wei18/Upkeep), [AgentSys](https://github.com/avifenesh/agentsys) and [visual-explainer](https://github.com/nicobailon/visual-explainer);
- [tree-sitting](https://github.com/oaustegard/claude-skills), which replaces mapping-codebases and keeps no artifact;
- [safishamsi/graphify](https://github.com/safishamsi/graphify), most likely the same project as Graphify-Labs/graphify (same commit in the round-8 and round-9 records), already rejected.

The refresh in AD-73 starts from them.

## Refresh trigger

Search again, or run the trial in AD-320, when any of these happens. The dated check is in [AD-73](../../backlog/tasks/ad-73%20-%20Re-run-prior-art-refreshes-at-their-trigger-dates.md).

- [groma.md](https://github.com/MrLesk/groma.md) reaches 1.0, or states a stable on-disk format;
- groma.md drops or delivers its plan to detach from the filesystem;
- a repo needs pull-request architecture diffs derived from code;
- 2027-05-17, six months on, since this field is moving fast.
