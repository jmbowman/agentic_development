# Prior art: decision records alongside LID (2026-11-06)

- **Effort:** full method, because the result shapes how every repo records decisions and may become contributions to LID itself.
- **Already known:**
  - The developer uses [LID](https://github.com/jszmajda/lid)'s decision model (below) and considers its support for decision records decent. They asked whether other tools could supplement it, and what could be suggested or contributed to LID.
  - [The federated knowledge note](2026-11-06-federated-knowledge-and-work-items.md) had already classified [adrkit](https://github.com/mbeacom/adrkit) (mbeacom's, distinct from rvdbreemen's adr-kit below), [skymavis decision-records](https://github.com/skymavis/skills), [zenrei](https://github.com/pikonori/zenrei), [mason](https://github.com/adrianczuczka/mason), [commitlore](https://github.com/MongLong0214/commitlore) and [Lore](https://arxiv.org/html/2603.15566). They keep the classes given there; this note goes deeper on the tools that could work with LID's model, and on the research.

## Need and criteria

**The baseline, LID's decision model** (its decision-doc template as installed here at v1.4.0, which matches the repository at 062d3ac):

- **How much to record.** The template defines three outcomes:
  - a choice that is obvious once landed gets no record;
  - a choice a cold reader might question gets one row in a design doc's Decisions & Alternatives table;
  - a choice a cold reader would re-litigate gets a full decision doc. These are rare.
- **Structure.** Context; Decision Elements (binary gates, and weighted criteria tied to tenets); Options in the Domain (one section per option, with a verdict per element); Selection.
- **Placement.** Named files (not numbered) in `docs/decisions/` or `docs/intent/<segment>/decisions/`, owned by a design node. A decision doc "owns no EARS specs, and carries no spec IDs".
- **Lifecycle.** Frontmatter is only `node:`, with no status field. Merging is acceptance. A superseded doc is deleted and replaced ("mutation, not accumulation"), with git keeping history. Relations between decisions are prose, because "what a decision relates to varies too much to bind to a schema".
- **Tooling.** Nothing checks decision docs; `lidc` checks EARS IDs and `@spec` annotations only.

| Requirement | Underlying need |
|---|---|
| Supplement LID's decision docs with tools | Catch decision rot (broken references, orphaned decisions, code that relies on a replaced decision) and deliver the right decisions to an agent, without changing LID's model |
| Suggest or contribute improvements to LID | Make decisions checkable and deliverable where evidence shows a gain, and confirm which of LID's choices hold up |
| Understand the research | Know what makes decision records useful and maintained, and what helps agents use them |

**Hard criteria for tools:** an OSI-approved license; human-gated (nothing commits, stages or rewrites without review); repo files as the source of truth; local only; coexists with LID's model and mdBook (no required status or numbering, no second navigation hierarchy), or can be configured to.

**Preferences:** standard Markdown links; pre-commit and CI checks; pinnable through mise; maintained.

## Verdict

**Inconclusive.** The developer stopped the search after one focused round plus source verification, while the round was still adding serious candidates. The open leads are under Snowball rounds. The evidence so far points one way.

**No existing tool works with LID's decision docs as they are, except as a plain link checker.**

- [spec-graph](https://github.com/spec-family/spec-graph) reads LID's folders unconfigured and fails on Markdown links to deleted decision docs. The federated note's linters already cover that: rumdl's MD057 relative-link check and [lychee](https://github.com/lycheeverse/lychee) for anchors.
- Every other decision tool read in source requires numbered files, a status field, its own folder or ledger, or global hooks, and several also fail the human gate.

**One configuration fix applies to any repo that runs [mdbook-lint](https://github.com/joshrotenberg/mdbook-lint) over LID decision docs.** Its decision-record rules are on by default and treat any `decisions/` folder as [MADR](https://github.com/adr/madr) records. List at least ADR002-ADR005 under `disabled-rules` in `.mdbook-lint.toml`; no wildcard works ([details](../tool-feedback/mdbook-lint.md)). This repo doesn't run mdbook-lint yet.

**The leading option is a small LID-compatible checker plus suggestions to LID.** The items are ordered by expected value, with the strength of evidence stated for each. Each adds something to a template that deliberately stays light, so each says what it costs.

1. **Decision citations in code, checked like `@spec`.** Code and docs cite a decision by file and heading (`<name>.md § <heading>`, never a line number), and a checker resolves each citation against the real heading. Deleting or renaming a decision doc then fails its stale citations instead of leaving them silently wrong.
   - Evidence: in one project, nine line-number citations silently pointed at the wrong text after an edit, one of them in a tool description agents read. The project now runs a test that resolves every citation by heading ([GetBurrowing/core](https://github.com/GetBurrowing/core); observational, one case).
   - Precedent: [ConDec](https://github.com/cures-hub/cures-condec-jira) tagged decisions in code comments (`@decision`) and issues, with a classifier proposing tags for a person to validate ([Kleebaum et al. 2021](http://archiv.ub.uni-heidelberg.de/volltextserver/29966/1/nlp4re1.pdf)).
   - A survey of decision tooling calls linking decisions to code essential, because linked documentation is easier to keep current ([Mehrpour and LaToza 2023](https://doi.org/10.1145/3607868)).
   - Links *to* decisions rot too: about 21% of decision-record files in a 2022 dataset were no longer at the same path three years later ([Su et al. 2026](https://arxiv.org/abs/2602.07609)).
   - Limits:
     - A replacement written into the same file under the same headings passes the check, while the citation may no longer hold.
     - Every heading rename forces edits wherever it's cited; GetBurrowing keeps a shrink-only list of 60 older citations in a non-conforming form.
     - LID's fixed section names (Context, Selection) mean most citations would point at an option's subheading or at Selection.
   - LID discussion #33 asks what the code-side `@spec` token is worth, so a proposal should say what a citation means (implements vs. mentions).
2. **Tie decisions to the EARS requirements that carry them out, checked by a tool.** This catches a spec rename or deletion that silently orphans a decision. It conflicts with the template's rule that a decision doc "carries no spec IDs", and with LID's arrow running from design to specs, so there are two directions to offer:
   - **(a) The decision cites specs.** An "Enforced by" line in the decision doc lists EARS IDs, and the checker confirms they still exist. [spec-driven-docs](https://github.com/gubasso/spec-driven-docs) does this for its rule IDs (verified in source), and MADR's optional Confirmation section serves a similar purpose. It changes the template rule.
   - **(b) Specs cite the decision.** An EARS spec, or the owning design doc's Decisions & Alternatives row, cites the decision doc, and the checker confirms each decision doc is cited by at least one live spec or row. This keeps the template rule and the arrow's direction.

   Evidence for checkability: in Su et al., about a quarter of the language models' misjudged violations involved principle-style decisions with no operational criteria (infrastructure decisions were the largest share, 42%).
3. **A structure check for decision docs.** The checkable rules: required sections present and not empty; each option's analysis leads with a verdict word; criteria (not gates) carry an importance from the template's vocabulary or a project-declared one; `node:` names a real segment; the owning design doc links the decision doc. The template implies, but doesn't state, at least two options.
   - Precedent: mdbook-lint's ADR rules (non-empty sections, at least two options, required headings), which are hard-coded to MADR and Nygard and would need reimplementing for LID's sections.
   - Evidence that options are what gets left out:
     - 36% of surveyed practitioners never record discarded options ([Tang et al. 2006](https://figshare.com/articles/report/A_survey_of_architecture_design_rationale/26269849)).
     - A preprint reports that Considered Options is the weakest section in mined records ([Miccio Palermo et al. 2026](https://arxiv.org/abs/2609.07375)).
     - The tool-support survey recommends templates that require specific information (Mehrpour and LaToza 2023).
   - There is no evidence that a linter improves outcomes. Rigid checks on rare, judgment-heavy docs risk failing legitimate ones.
4. **Deliver decisions to the agent.**
   - The cheapest step is a SessionStart hook of about 20 lines that lists both decision folders with each doc's H1 title ("Decision: …"). The title names the topic, not the outcome, so an agent still opens the doc to learn what was decided. It ports the idea of [pi-adr](https://github.com/nicknisi/pi-extensions/tree/main/packages/adr)'s "steering veto list".
   - A later step is an optional `scope:` glob list beside `node:`, so a hook can print the decisions governing a file before an edit. [adr-kit](https://github.com/rvdbreemen/adr-kit) and [ank](https://github.com/haksolot/ank) do this in their own formats, and so does [Mneme](https://github.com/MnemeHQ/mneme) according to its docs. It adds a second frontmatter field to a template that keeps only `node:`.
   - Evidence:
     - One preprint reports zero voluntary memory reads by agents, against reliable delivery by the harness ([Delivery, Not Storage](https://arxiv.org/abs/2607.20972), weak experiment).
     - Two 2026 preprints report better results when past decisions are supplied at coding or review time ([Yin et al.](https://arxiv.org/abs/2610.11578), [Zhou et al.](https://arxiv.org/abs/2610.21925); abstracts only).
     - The tool-support survey recommends delivering decisions at the moment of editing.
   - LID issue #39 already plans a generated, always-in-context copy of the tenets, which could carry these pointers.
5. **Name what would reopen a rejected or deferred option.** Each option judged against the selection could carry "revisit if …", which item 3 could check.
   - This overlaps Decision Elements, which already let a reader re-run the judgment; the gain is naming the trigger explicitly.
   - Evidence is weak: practitioner guidance only, [Zimmermann's AD Definition of Done](https://ozimmer.ch/practices/2020/05/22/ADDefinitionOfDone.html) (which includes a revision plan), plus [houserules](https://github.com/DTCurrie/houserules)' and spec-driven-docs' method text.
   - Lowest priority.
6. **Evidence for #79's premise.** LID issue #79 (does the workflow offer a decision doc when one is warranted?) is blocked on a multi-turn harness. A single-turn test of a related question can run now: does a recorded decision change agent behavior?
   - [keep-the-why](https://github.com/oliver-zehentleitner/keep-the-why)'s experiment asked sessions to "simplify" a retry wrapper whose rejected alternative (a plain loop) was or wasn't recorded. With the record, 0 of 10 offered to drop the `Retry-After` handling that the plain loop would lose, against 7 of 10 without (p ≈ 0.003, Fisher's exact test).
   - It is a weak experiment: one task, one model, graded by the tool's author, and the "with record" runs also carried the rationale in a commit message.

[Mehrpour and LaToza's survey](https://doi.org/10.1145/3607868) supports items 1, 3 and 4 from the pre-agent literature, and gives nothing for item 5.

**Next steps:**

1. Disable ADR002-ADR005 in `.mdbook-lint.toml` wherever mdbook-lint runs over LID decision docs.
2. Build the SessionStart index (item 4's first step) locally; it needs no LID change.
3. Build item 1 as a local script run beside `lidc` (for example in `mise run lid`), and offer it upstream once it has run here.
4. Open one upstream discussion pairing item 1 with discussion #33, and with #105, which asks that owner rulings be recorded by reference rather than paraphrased.
5. Raise item 2 (with both directions) and item 3 after the maintainer responds; hold item 5.

**Where LID's choices hold up, and where they don't:**

- **Rationale in decision docs, rules in specs.** The tool-support survey separates design rationale (alternatives and why one was chosen, not checked against code) from design rules (checkable constraints). That matches LID keeping rationale in decision docs and checkable behavior in EARS and tests.
- **No status field.**
  - About half of decision-record files are never edited after their first commit, and only 42 of 921 repos showed sustained use ([Buchgeher et al. 2023](https://doi.org/10.1109/access.2023.3287654)).
  - 109 repos used 20 inconsistent status labels (Su et al. 2026).
  - Readers rated status as needed only about a quarter of the time ([Falessi, Cantone and Kruchten 2008](https://art.torvergata.it/bitstream/2108/57813/1/2008_WICSA_FCK_Value-Based%20Design%20Decision%20Rationale%20Documentation%20Principles%20and%20empirical%20feasibility%20study.pdf)).
  - The abstract of [Santana et al. 2026](https://doi.org/10.1109/icsa66085.2026.00040) reports that 63% of records open directly as "accepted", which matches merge-as-acceptance.
- **Delete and replace: supported, with a real cost.**
  - For: two practitioner posts (web summaries only) report that agents follow stale records more rigidly than people do. Both *keep* superseded records but filter them out of agent context.
  - For: one tool's README says "leaving an obsolete directive in place is worse than removing it" ([adc](https://github.com/dbrattli/adc)).
  - For: one abstract reports retrieval returning superseded values 36-38% of the time, against almost never with deterministic supersession ([Temporal Validity on Real Software Histories](https://arxiv.org/abs/2608.20685), abstract only). A reported filter-versus-flag result is unverified (see Snowball rounds).
  - Against: most human-oriented practice keeps superseded records with a status (Nygard, MADR, every popular decision skill read). Kept records give readers and agents history without git archaeology, and keep supersession links checkable. Items 1 and 2 exist partly to recover that checkability under deletion.
  - A middle path is an archive folder of retired decisions kept out of agent context, which would also let spec-graph's checks fire. They warn when a live doc relies on a retired one ("stale premise") or hands work to one ("ghost handover"). This note didn't evaluate it.
- **Two weights and the cold-reader test.** Independent tools arrived at the same split ([riekelt/technical-writer](https://github.com/riekelt/technical-writer)) and a similar recording bar (houserules), and Falessi et al. recommend tailoring rationale to the reader's purpose. A caveat: a preprint found Nygard's minimal template beat MADR on a combined comprehension, usability and adoption score with 33 students, though the authors' feature analysis ranked MADR slightly higher ([Nogueira et al. 2026](https://arxiv.org/abs/2604.27333)). LID's full template is heavier than MADR, so this is weak evidence against its structure. The two-weights split puts most decisions in a one-line row.
- **Mandatory options.** Items 3 and 6.
- **Prose relations.** Readers rated related decisions as needed only 28% of the time, but Falessi et al. expected relations to matter once tools could navigate them. Agents are such tools, so the case for structured relations grows with agent use. LID's prose choice holds for human readers, and a vocabulary such as [gy](https://github.com/aq2bq/gy)'s (narrows, widens, supersedes, completes) stays available.
- **Named, unnumbered files.** spec-driven-docs uses slug names because number counters collide across parallel worktrees and agents.

**Already active in LID's tracker:**
- [#105](https://github.com/jszmajda/lid/issues/105): rulings recorded as paraphrases drift.
- [#90](https://github.com/jszmajda/lid/issues/90): a table of pending decisions at each stop, agreed by the maintainer.
- [#79](https://github.com/jszmajda/lid/issues/79): an eval for offering decision docs.
- [#39](https://github.com/jszmajda/lid/issues/39): tenets in the instruction file.
- [Discussion #33](https://github.com/jszmajda/lid/discussions/33): the weight of the `@spec` token.

Nothing found in its 65 issues, 33 PRs or 9 discussions (titles listed, a keyword search, and ten bodies read) proposes decision linting, decision citations from code, or delivery by path.

## Candidates and matrix

Ranked shortlist:

1. **A LID-compatible checker, built locally first (custom).** Items 1-3. It ranks first because no tool checks LID's docs as they are. It would be displaced if LID adopted equivalent checks in `lidc`.
2. **[spec-graph](https://github.com/spec-family/spec-graph) as a CI check.** It works unconfigured and tolerates status-free docs, but for LID it duplicates MD057 and lychee today. It would move up if LID kept retired decisions in an archive folder.
3. **A SessionStart decision index (custom, about 20 lines).** Item 4's first step. It ranks below spec-graph only because it adds a hook rather than reusing a check. It would move up if #39's generated instruction-file block could carry the index, and drop if Claude Code gained native per-path context.

| Candidate | Class | License (file:line at commit) | Reason |
|---|---|---|---|
| [spec-graph](https://github.com/spec-family/spec-graph) | borrow ideas | MIT (`LICENSE:1-21` at fc5bec6) | Reads LID's folders unconfigured; only its broken-link check fires on LID docs (verified in source) |
| [mdbook-lint](https://github.com/joshrotenberg/mdbook-lint) | adopt (with ADR rules disabled) | MIT or Apache-2.0 (`LICENSE-MIT:1-21`, `LICENSE-APACHE` at a1c27e5) | Already in the federated blend; ADR002-ADR005 fail LID docs; its ADR rules are a design template (verified in source) |
| [spec-driven-docs](https://github.com/gubasso/spec-driven-docs) | borrow ideas | MIT for code (`LICENSE-MIT`), CC-BY-4.0 for method text (`LICENSE:1-26`), in the 0.15.0 crate | "Enforced by" check; slug names; never deletes, requires a status (verified in source) |
| [adr-kit](https://github.com/rvdbreemen/adr-kit) (rvdbreemen) | reject | MIT (`LICENSE:1-21` at ce18f6b) | Requires `ADR-NNN` names, one folder, a status and its own fixed sections (verified in source) |
| [trailstone](https://github.com/vishwamdhavale/trailstone) | borrow ideas | Apache-2.0 (`LICENSE:1-202` at 00bcf60) | Staleness of code under a replaced decision; a second ledger; global hooks; binds agent-reported "user" decisions without review (verified in source) |
| [pi-adr](https://github.com/nicknisi/pi-extensions/tree/main/packages/adr) | borrow ideas | MIT (`LICENSE:1-21` at b6c8f5f) | Filenames injected as a veto list; numbered files only; pi agent only (verified in source) |
| [aval](https://github.com/fredericrous/aval) | borrow ideas | MIT (`LICENSE:1-21` at 5be8e09) | Detects two live answers to one question; needs status and topic keys in frontmatter (verified in source) |
| [ank](https://github.com/haksolot/ank) | borrow ideas | Apache-2.0 (`LICENSE:1-201` at dc21fbd) | Path-scoped decisions served at edit time; its own store; pushes custom git refs (verified in source) |
| [archgate](https://github.com/archgate/cli) | borrow ideas | Apache-2.0 (`LICENSE.md:1-201` at f65d99f) | An executable rule per decision; one directory; telemetry on by default (verified in source) |
| [keep-the-why](https://github.com/oliver-zehentleitner/keep-the-why) | borrow ideas | MIT (`LICENSE:1-21` at 28bfdc9) | Experiment design for an eval; supersedes rather than deletes (verified in source) |
| [GetBurrowing/core](https://github.com/GetBurrowing/core) | borrow ideas | Apache-2.0 (`LICENSE:1-201` at 913287c) | A test that resolves heading citations to decisions; bans line numbers (verified in source) |
| [adc](https://github.com/dbrattli/adc) | borrow ideas | MIT (`LICENSE`, opening lines, at 995fb46) | `decision:` comments; remove obsolete directives; no checker (verified by listing: 7 files, no checker) |
| [adrkit](https://github.com/mbeacom/adrkit) (mbeacom) | borrow ideas | Apache-2.0 (`LICENSE:1-201` at 9513165) | `affects` globs and `@adr` markers; strict frontmatter (verified in source, per the federated note) |
| [beagle](https://github.com/existential-birds/beagle) decision extraction | borrow ideas | Apache-2.0 (`LICENSE`, opening lines, at d1a7489) | Mines sessions for decisions with confidence levels; read-only (docs only) |
| [riekelt/technical-writer](https://github.com/riekelt/technical-writer) | borrow ideas | MIT (`LICENSE`, opening lines, at 85e5372) | Two weights of record; strongest-argument rule; append-only (docs only) |
| [houserules](https://github.com/DTCurrie/houserules) | borrow ideas | MIT (`LICENSE`, opening lines, at 57e3537) | Recording bar close to LID's; a revisit trigger; gitignored ledger (docs only) |
| [adrs](https://github.com/joshrotenberg/adrs) | reject | MIT or Apache-2.0 (`LICENSE-MIT`, opening lines, at d3b1bdd) | Numbering and status checks; only its broken-link check fits LID (docs only) |
| [log4brains](https://github.com/thomvaill/log4brains), [adr-tools](https://github.com/npryce/adr-tools), [MADR](https://github.com/adr/madr) | reject | not read (Apache-2.0; GPL-3.0-or-later; MIT or CC0 per the forge records) | Numbered files and kept superseded records; log4brains is stale and builds its own site (docs only); MADR's Confirmation section is worth borrowing |

Structurizr's decision support and dotnet-adr were seen and judged not serious: Structurizr's CLI is archived, and dotnet-adr is a numbered-files .NET tool.

Matrix (✓ native, ◐ partial, ⊕ extensible, ✗ unsupported, ? unverified; H marks hard criteria). It covers the candidates verified against the hard criteria; every other row fails one as its Reason states, or is kept for ideas only.

| Criterion | spec-graph | mdbook-lint (ADR rules) | adr-kit | trailstone | Custom LID checker |
|---|---|---|---|---|---|
| License (H) | ✓ (see table) | ✓ (see table) | ✓ (see table) | ✓ (see table) | ✓ (design) |
| Human-gated (H) | ✓ writes only a baseline, no git (`src/cli.ts:1356-1382`) | ✓ reports only (`registry.rs:156-211`) | ◐ hooks active once enabled; init sets `core.hooksPath` (`skills/init/SKILL.md:344-351`) | ◐ global hooks (`trailstone.mjs:1783-1992`); agent-reported "user" decisions bind (`trailstone.mjs:950-959`) | ✓ (design) |
| Repo files as source (H) | ✓ reads `docs/**/*.md` (`src/runner.ts:24-31`) | ✓ | ✓ (`bin/adr_catalog.py:41-90`) | ✗ second YAML ledger (`trailstone.mjs:64-81`) | ✓ (design) |
| Local only (H) | ✓ no dependencies (npm `package.json`) | ✓ | ✓ | ◐ background `git fetch` every 30 s (`trailstone.mjs:441-480`) | ✓ (design) |
| Coexists with LID's model and mdBook (H) | ◐ broken links only (`src/rules.ts:439-469`) | ✗ detected as MADR (`format.rs:63-83`); ADR002-005 fire (`adr002.rs`-`adr005.rs`) | ✗ `ADR-NNN` only (`bin/adr_catalog.py:41-90`) | ✗ staleness needs the replaced row kept (`trailstone.mjs:313-326`) | ⊕ (design) |
| Decision delivery by path | ? not found | ? not found | ◐ needs its index and globs (`bin/adr_query.py:184-226`) | ✓ next-edit warning (`trailstone.mjs:673-796`) | ⊕ (design) |
| Pre-commit and CI | ✓ exit 0/1/2, SARIF (`src/cli.ts:1440-1461`) | ✓ | ✓ quality gate exits 1 (`bin/adr_quality_core.py:58-97`) | ✓ pre-push block (`trailstone.mjs:869-959`) | ⊕ (design) |
| Pinnable through mise | ✓ npm 0.21.0 | ✓ crate | ? not found | ✓ npm 0.3.9 | ⊕ (design) |
| Maintained | ◐ young, released 2026-10-29 | ✓ | ◐ young | ◐ young | — |

**Blends considered:**

- **mdbook-lint (ADR002-ADR005 disabled), MD057 and lychee, plus a custom LID checker and the SessionStart index:** the leading option. It reuses what the federated note adopts, and adds only LID-specific checks.
- **The same with spec-graph in place of MD057 for decision links:** no gain for LID as it stands. It becomes worthwhile if LID adopts an archive folder for retired decisions.
- **adr-kit or trailstone beside LID's docs:** each would need a second record of every decision (numbered files or a YAML ledger), which LID's "one home per decision" rules out.

**Scenario walk:**

1. **A decision doc is deleted and replaced under a new name.** Leading blend: MD057 and lychee fail on Markdown links to the old file, and the custom checker fails on code citations to it. spec-graph would add nothing. trailstone would need the old decision kept in its ledger.
2. **A spec named by a decision is renamed.** With item 2(a), the checker fails on the decision's "Enforced by" line. With item 2(b), it fails because the decision is no longer cited by a live spec. Without item 2, nothing notices.
3. **A fresh CI clone.** mise installs mdbook-lint and the existing linters at pinned versions, and the local checker runs in `mise run lid`. The same checks fail CI as fail pre-commit.
4. **An agent edits a file a decision governs.** The SessionStart index lists decision titles, so the agent knows the decision exists but must open it. With `scope:` globs, a pre-edit hook would name it directly.

## Limitations checked in source

Readings are from shallow clones or registry archives at the commits given; nothing was installed or run.

- **[spec-graph](https://github.com/spec-family/spec-graph)**, with no configuration, reads `docs/**/*.md`, puts any file under a `decisions` folder in the decision family, names a numberless file by its filename, and treats a missing status as unknown with no finding. Its ghost-handover and stale-premise checks need the target document to exist and be marked retired, so they can't fire under delete-and-replace. A Markdown link to a deleted decision doc is a broken-reference error. *Verified in source* (`src/runner.ts:24-31`, `src/identity.ts:24-43,101-222`, `src/lifecycle.ts:193-253`, `src/rules.ts:286-418,439-469` at fc5bec6).
- **[mdbook-lint](https://github.com/joshrotenberg/mdbook-lint)** treats any `adr`, `adrs`, `decisions` or `architecture-decisions` path segment as a decision record. Its ADR rules are on by default, and ADR002-ADR005 (status, date, two MADR headings) fail a LID decision doc. They are disabled only by listing each ID under `disabled-rules`; the documented wildcard has no effect. *Verified in source* (`crates/mdbook-lint-rulesets/src/adr/format.rs:63-83,107-147`, `registry.rs:156-211`, core `config.rs:26-32` at a1c27e5).
- **[adr-kit](https://github.com/rvdbreemen/adr-kit)** keeps only files named `ADR-<1-4 digits>-*.md` in one non-recursive folder, and treats a missing status as historical, which `adr-context` drops by default. Its quality check requires its own seven sections (Status, Context, Decision, Alternatives Considered, Consequences, Related Decisions, References) and a `# ADR-NNN` title. *Verified in source* (`bin/adr_catalog.py:41-90,335-345`, `bin/adr_query.py:184-226`, `bin/adr_quality_core.py:58-97` at ce18f6b).
- **[trailstone](https://github.com/vishwamdhavale/trailstone)**'s install writes four hooks to the global `~/.claude/settings.json`, a pre-push hook and an `AGENTS.md` block. It records an agent-reported user choice as binding without review, and it never commits in user repos. *Verified in source* (`trailstone.mjs:735-752,869-959,1783-1992` at 00bcf60).
- **[pi-adr](https://github.com/nicknisi/pi-extensions/tree/main/packages/adr)** injects only the paths of files matching `^\d{4}-` directly under `docs/decisions/`. *Verified in source* (`packages/adr/index.ts:1-66` at b6c8f5f).
- **[spec-driven-docs](https://github.com/gubasso/spec-driven-docs)** checks, across all decision docs, that every backtick-quoted rule ID in an "Enforced by" paragraph is still defined in a spec. Its reopening-condition rule exists only in its method text. *Verified in source* (`src/gates/adr_cites_a_live_rule.rs:1-137`; `method/decisions.md:30-76` in the 0.15.0 crate).
- **[GetBurrowing/core](https://github.com/GetBurrowing/core)**'s test resolves every `NNNN-name.md § heading` citation in code against a real heading, bans line-number citations, and keeps a shrink-only list of 60 older citations in a non-conforming form. *Verified in source* (`apps/platform/test/platform/regression/adr_citation_audit_test.exs`, read in full; `apps/platform/AGENTS.md:46-110` at 913287c).
- **[archgate](https://github.com/archgate/cli)** reads one decision directory, non-recursively. It runs a paired `.rules.ts` per decision, sends telemetry by default, and adds a global git credential helper on login. *Verified in source* (`adr.ts:32-46`, `project-config.ts:260-281`, `telemetry-config.ts:5,101` at f65d99f).
- **[keep-the-why](https://github.com/oliver-zehentleitner/keep-the-why)**'s driver runs headless sessions with permission checks skipped, and the author graded the transcripts by hand. *Verified in source* (`run.py:30-120`, `drivers/claude.py:11-31`, `results/SUMMARY.md:11-48` at 28bfdc9).

Verified:
- the licenses of every candidate in the table marked "verified in source", each read in full and grepped for riders, restrictions, the Commons Clause and additional terms;
- the other licenses, from the named file's opening lines or, where marked "not read", only from the forge records;
- the source claims above.

Could not verify:
- the full texts of [Santana et al. 2026](https://doi.org/10.1109/icsa66085.2026.00040) (its server refused scripted downloads) and [Ahmeti et al. 2024](https://doi.org/10.1007/978-3-031-70797-1_22) (paywalled);
- three practice pages central to the supersession question, which returned 404;
- the practitioner reports on agents and stale records (web summaries only);
- Mneme's path-scoped delivery (docs only);
- PyPI's search page and IEEE Xplore (unavailable; see the ledger).

## Papers

Every claim is paper-reported; preprint claims are the authors' and not established. Some search data came from Semantic Scholar.

| Paper | Read state | Evidence strength | Review status | Class | Claim (tag) |
|---|---|---|---|---|---|
| [Using Architecture Decision Records in Open Source Projects (Buchgeher et al. 2023)](https://doi.org/10.1109/access.2023.3287654) | read in full | observational study | peer-reviewed | borrow ideas | 921 repos, 6,362 records: about half never edited after the first commit; 42 repos show sustained use (paper-reported) |
| [Evaluating LLMs for Detecting Architecture Decision Violations (Su et al. 2026)](https://arxiv.org/abs/2602.07609) | read in full | observational study | peer-reviewed (ICSA 2026) | borrow ideas | Best models about 0.91 accurate; errors concentrated in infrastructure (42%) and principle-style (26%) decisions; 20 inconsistent status labels; about 21% of decision-record files moved or deleted within 3 years (paper-reported) |
| [A Survey of Tool Support for Working with Design Decisions in Code (Mehrpour and LaToza 2023)](https://doi.org/10.1145/3607868) | read in full, §1-9 (from a CC BY copy the developer supplied) | qualitative study (a narrative review of tools; predates LLM agents) | peer-reviewed (ACM Computing Surveys) | borrow ideas | Separates design rationale (not checked against code) from design rules (checkable). Calls linking decisions to code essential, but notes most tools keep only one-way, unchecked links. Recommends templates requiring specific information, delivery at the moment of editing, and flagging divergence at first violation (paper-reported) |
| [Value-Based Design Decision Rationale Documentation (Falessi, Cantone and Kruchten 2008)](https://art.torvergata.it/bitstream/2108/57813/1/2008_WICSA_FCK_Value-Based%20Design%20Decision%20Rationale%20Documentation%20Principles%20and%20empirical%20feasibility%20study.pdf) | read in full | weak experiment | peer-reviewed (WICSA 2008) | borrow ideas | Readers needed the issue 91% of the time, alternatives and arguments 73%, status about 25%, related decisions 28% (paper-reported) |
| [A Text Mining and Classification Approach for ADRs (Miccio Palermo et al. 2026)](https://arxiv.org/abs/2609.07375) | read in full | observational study | preprint | borrow ideas | Considered Options is the weakest section; decision drivers often misplaced (paper-reported) |
| [One Size Fits All? Comparing ADR Templates (Nogueira et al. 2026)](https://arxiv.org/abs/2604.27333) | read in full | weak experiment | preprint | borrow ideas | Nygard's template beat MADR on a combined comprehension, usability and adoption score with 33 students; the authors' feature analysis ranked MADR slightly higher (paper-reported) |
| [Continuous Rationale Identification, ConDec (Kleebaum et al. 2021)](http://archiv.ub.uni-heidelberg.de/volltextserver/29966/1/nlp4re1.pdf) | read in full | weak experiment | peer-reviewed | borrow ideas | Inline `[decision]` and `@decision` tags, with classifier proposals that a person validates (recall 0.97, precision 0.65) (paper-reported) |
| [A Survey of Architecture Design Rationale (Tang et al. 2006)](https://figshare.com/articles/report/A_survey_of_architecture_design_rationale/26269849) | read in part (§4.4-4.5, conclusions) | observational study | unreviewed report (the technical-report version of the peer-reviewed JSS 2006 paper) | borrow ideas | Barriers to recording rationale: no time 60.5%, no standards 42%, no tool 29.6%; 36% never record discarded options (paper-reported) |
| [AI Assistance for Architectural Decision Making (Zimmermann and Seiger 2026)](https://alexandria.unisg.ch/bitstreams/3e77ee2d-825c-4bb3-8a62-d6e5b878824d/download) | read in part (§1, 2, 4) | untested proposal | peer-reviewed | borrow ideas | A five-criterion review prompt, and revision reminders as a use case (paper-reported) |
| [Delivery, Not Storage (2026)](https://arxiv.org/abs/2607.20972) | read in part (abstract, §5.2), per the federated note | weak experiment | preprint | borrow ideas | Zero voluntary memory reads in 114 turns; delivery triggered by the harness always worked (paper-reported) |
| [Chronos Enables Code Agents to Reason over Software History (Yin et al. 2026)](https://arxiv.org/abs/2610.11578) | abstract only | experiment | preprint | borrow ideas | The abstract reports that distilling merged PRs into linked experience cards, retrieved at coding time, raises agents' resolution rate (paper-reported) |
| [Benchmarking and Enhancing Design-Aware Code Review (Zhou et al. 2026)](https://arxiv.org/abs/2610.21925) | abstract only | experiment | preprint | borrow ideas | The abstract reports that design-aware review is hard for agents (best baseline F1 0.213), and that design decisions extracted from past review threads improve it (paper-reported) |
| [Temporal Validity on Real Software Histories (2026)](https://arxiv.org/abs/2608.20685) | abstract only | experiment | preprint | borrow ideas | The abstract reports that retrieval returns superseded values 36-38% of the time, deterministic supersession almost never (paper-reported) |
| [Architecture Decision Records: Adoption, Impact, and Developer Engagement (Santana et al. 2026)](https://doi.org/10.1109/icsa66085.2026.00040) | abstract only | observational study | peer-reviewed (ICSA 2026) | borrow ideas | The abstract reports that 63% of records open directly as accepted (paper-reported) |
| [Architecture Decision Records in Practice (Ahmeti et al. 2024)](https://doi.org/10.1007/978-3-031-70797-1_22) | abstract only | qualitative study | peer-reviewed (ECSA 2024) | borrow ideas | The abstract reports that where records are stored strongly affects their perceived usefulness (paper-reported) |

About 25 further papers were seen and not tabled. They are mostly abstracts on classic design rationale (QOC, gIBIS, DRL, Kruchten's ontology) and on LLM-drafted decisions, which are broad but noisy and often miss the why.

## Worth retrieving manually

- [Architecture Decision Records: Adoption, Impact, and Developer Engagement (Santana et al. 2026)](https://doi.org/10.1109/icsa66085.2026.00040) (DOI 10.1109/icsa66085.2026.00040). It bears on the status-field and acceptance questions. IEEE's server refused scripted downloads. Legal routes: IEEE Xplore's pay-per-article page, a library, or an author request.
- [Architecture Decision Records in Practice (Ahmeti et al. 2024)](https://doi.org/10.1007/978-3-031-70797-1_22) (DOI 10.1007/978-3-031-70797-1_22). It bears on whether decision docs belong beside design docs. It is paywalled. Legal routes: Springer's pay-per-article page, a library or interlibrary loan, or an author request.

## Coverage ledger

| Route | State | Queries or reason |
|---|---|---|
| The stack itself | searched | LID's decision-doc and HLD templates (v1.4.0); `lidc` checks; mdbook-lint's ADR rules |
| Earlier notes and decisions | searched | The federated knowledge note and its round-1-5 records |
| GitHub repository search | searched | 34 queries, e.g. "adr lint", "adr linter", "adr tooling", "decision records agents" |
| GitHub topics | searched | 7: `topic:adr`, `topic:architecture-decision-records`, `topic:decision-records`, madr, design-rationale, adr-tools, log4brains |
| GitHub code search | searched | 16 queries, e.g. `"## Decision Elements" path:decisions`, `"node:" "## Decision Elements"`, `@adr` and `@decision` annotations |
| LID's repository | searched | 65 issues, 33 PRs and 9 discussions listed; keyword search (decision, supersede, status field); bodies of 8 issues, 1 PR and 1 discussion read |
| GitLab and Codeberg search | searched | 6 and 5 queries, e.g. "architecture decision records", "adr tool", "decision record" |
| npm | searched | 9 queries, e.g. "adr", "decision record", "design rationale" |
| crates.io | searched | 7 queries, e.g. "adr", "decision record", "architecture decision" |
| Language registries | searched | Go: 3 pkg.go.dev searches ("architecture decision records", "decision record markdown", "adr lint"); NuGet: "adr" |
| PyPI | searched | Exact-name lookups for the established tools (adr-viewer, pyadr) |
| PyPI search page | unavailable | Every query (4) returned a JavaScript challenge page; keyword queries went through libraries.io |
| libraries.io | searched | 7 queries, e.g. "adr", "decision record", "design rationale" |
| Homebrew formulae | searched | Regex over names and descriptions: adr, decision record, architecture decision |
| AUR | searched | "adr", "architecture decision", "decision record" |
| ecosyste.ms | searched | 9 keywords, e.g. adr, adrs, architecture-decision-records, decision-records |
| LibHunt | searched | npryce/adr-tools, thomvaill/log4brains; nothing new |
| Cross-language equivalents | excluded | The strongest finds are standalone CLIs used as CI checks, where implementation language doesn't matter to the need |
| Awesome lists and catalogs | searched | adr.github.io's tooling post, MADR's tooling page, five awesome lists for skills and MCP servers |
| alternativeto.net | excluded | It challenges automated clients |
| aitoolnet.com | excluded | No end-user AI product sought |
| General web search | searched | 9 practice and critique phrasings ("architecture decision records anti-patterns", "ADR superseded vs delete decision record git", "architecture decision records for AI coding agents") and 9 on tools and hosted services, plus Nygard's post, ozimmer.ch and adr.github.io |
| Hosted services | searched | Fabric, Decision Records, EventCatalog, Confluence decision log (docs only; all fail the local criterion) |
| Skill directories | searched | skills.sh: "adr", "architecture decision", "decision record", "design rationale", "rfc", "decision log", "tradeoff analysis" |
| Claude Code plugin marketplaces | searched | The official marketplace file, regex `\badrs?\b\|decision[- ]?(record\|log\|doc)`; no decision plugins |
| MCP Registry | searched | adr, decision, decisions, rationale, rfc |
| PulseMCP | excluded | robots.txt disallows ClaudeBot |
| Anthropic's skills repo | searched | No decision skill |
| GitHub topics for agent skills | excluded | Skill repos were reached through skills.sh, the marketplace file and awesome lists; the GitHub topic searches above also return skill repos tagged adr or decision-records |
| arXiv | searched | 19 queries, e.g. `abs:"architecture decision record"`, `abs:"architectural decision records"`, plus references from four seed papers |
| OpenAlex | searched | 16 keyword searches (e.g. "architecture decision records", "architectural knowledge management"), 7 title lookups, DOI lookups and citers of five hub papers |
| Crossref | searched | DOI lookups for three papers |
| OpenAIRE | searched | "architecture decision records"; noise only |
| Semantic Scholar | searched | Bulk search on "architecture decision records"; two 429 responses, then success on the third try |
| Hugging Face papers, papers.cool | searched | "architecture decision records"; nothing new |
| Venue program pages | searched | The ICSA 2026 program, which added the federated-knowledge paper; the ECSA 2026 program page wasn't found (the guessed URL returned 404), so its papers were sought through OpenAlex |
| IEEE Xplore | unavailable | Refused a scripted download of a CC BY paper, after a retry; the abstract came through OpenAlex |
| Zenodo, Europe PMC, nixpkgs | excluded | robots rules disallow the API; no life-sciences angle; no brotli decompressor |

## Snowball rounds

1. **Snowball round 1 (run as round 6 of the federated search, narrowed to decision records):**
   - Added [spec-graph](https://github.com/spec-family/spec-graph), [spec-driven-docs](https://github.com/gubasso/spec-driven-docs), [trailstone](https://github.com/vishwamdhavale/trailstone), [adr-kit](https://github.com/rvdbreemen/adr-kit), [aval](https://github.com/fredericrous/aval), [pi-adr](https://github.com/nicknisi/pi-extensions/tree/main/packages/adr), [ank](https://github.com/haksolot/ank), [archgate](https://github.com/archgate/cli), [keep-the-why](https://github.com/oliver-zehentleitner/keep-the-why), [adc](https://github.com/dbrattli/adc), [beagle](https://github.com/existential-birds/beagle) and [riekelt/technical-writer](https://github.com/riekelt/technical-writer), and the papers above.
   - Verification in source reduced every tool to borrowed ideas, except spec-graph's link check and the mdbook-lint configuration fix.

The developer stopped the search after this round, short of the 10-round cap, with candidates still coming. Open leads:
- [repo-memory](https://github.com/Semeton/repo-memory): falsifiable evidence checks; agents can only propose.
- [snubber](https://github.com/snubber-dev/snubber): named IDs; claims checked against the tree.
- [decision-guardian](https://github.com/DecispherHQ/decision-guardian): path globs mapped to decisions in PR comments; telemetry on by default (docs only).
- [mnema](https://github.com/mnema-work/mnema)'s hooks.
- Zimmermann's work on embedding decisions in code ([e-adr](https://github.com/adr/e-adr)).
- The source of a reported drop from 43.1% to zero in superseded records returned to agents when old records were filtered rather than flagged.

## Refresh trigger

- Before the LID-compatible checker is designed: check the open leads under Snowball rounds.
- When LID responds to a contribution on decision citations, spec links or decision delivery.
- When mdbook-lint makes its ADR rules opt-in or path-configurable.
- When spec-graph supports a retired-decisions folder, or LID adopts one.
- On 2027-05-06, whichever comes first.
