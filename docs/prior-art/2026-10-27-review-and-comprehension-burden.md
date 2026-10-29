# Prior art: reducing the cognitive burden of reviewing and understanding software (2026-10-27)

- **Effort:** full method. The findings shape the template defaults, the review wave and the spec conventions that every repo inherits, and the developer asked for every angle.
- **Already known:** an earlier search covered how to present a finished diff. Its main levers were:
  - a size ceiling of about 400 changed lines per slice;
  - grouping related parts, and putting declarations before their uses;
  - the riskiest group first;
  - importance tiers that never drop a part;
  - context and rationale first;
  - offering structure rather than forcing a step-by-step walk;
  - comprehension questions as retrieval practice.

  The tools it found for writing review tours were CoRT, code-review-tour, comprehension-review, diffity and pr-walkthrough. The developer named nothing else as known or dismissed.
- **Omitted:** that earlier search lives in a private repository. This note restates what it needs from it and gives no link.

## Need and criteria

The bottleneck is how fast a developer can understand a change well enough to approve it with confidence. Agents write the code. At work, every change gets careful human review.

| Angle | Underlying need |
|---|---|
| A. Less and simpler software | Fewer, simpler lines to read for the same outcome, through language, libraries, complexity limits and deletion |
| B. Tests that are easy to review | A reviewer can tell what a test pins and whether it would catch a break, without tracing its code |
| C. The right number of tests | Each spec gets enough tests to be trusted and no more. Every extra test costs reading time |
| D. Faster-to-read specs and docs | Designs and EARS lists carry the same information in less reading time, through diagrams, tables and structure |
| E. Reviewer skill | The reviewer gets faster and more accurate, and gets feedback on how accurate they are |
| F. How changes are structured, and the tooling around them | The change arrives with noise hidden, split by concern, and linked to its specs |

**Hard criteria:**
1. An OSI-approved license, for anything installed or built on. For research, ideas and commercial products, the license doesn't apply.
2. No hosted service is required for the default path. Commercial and hosted options are reported as springboards.
3. Fits the stacks in use: Python with pytest, ruff and ty (copier-python and agentic_development); C++/Qt with QTest and qmake ([PortaBase](https://github.com/jmbowman/portabase)); Markdown specs rendered on GitHub and by mdBook.
4. Keeps the human in charge. Nothing may hide part of a change from review (the earlier search's coverage rule), and nothing may replace human review with an agent verdict.

**Preferences:**
- evidence from a controlled experiment or large-scale mining over vendor claims;
- maintained and mature;
- updatable by Renovate through mise or uv;
- works the same locally, in CI, and for agents.

## Verdict

**Blend.** No single tool or technique covers the need. The search found:
- seven cheap moves that can be adopted now;
- four built on existing libraries;
- three custom pieces that nothing found provides.

**Adopt now (low cost, evidence-backed):**
1. **Cognitive-complexity ratchets on changed code** (angle A).
   - copier-python: add [complexipy](https://github.com/rohaquinlop/complexipy)'s git-diff gate. It fails only functions that are new or have got worse.
   - PortaBase: clang-tidy's `readability-function-cognitive-complexity` already runs through `readability-*` (`.clang-tidy:6`), but at its default threshold of 25 and with `WarningsAsErrors: ''` (`.clang-tidy:16`). Lower the threshold and make the check an error.
   - Evidence: cognitive complexity tracks comprehension time and perceived difficulty, not correctness (Muñoz Barón et al. 2020). Treat it as a cheap guardrail.
2. **Deletion and duplication checks** (A): [vulture](https://github.com/jendrikseipp/vulture) at confidence 80 or higher, with a whitelist; jscpd for duplicated blocks. Code size and vocabulary are the most robust predictors of comprehension load (Peitek et al. 2021). Agent-written code skews toward copy-paste (GitClear 2025, [vendor]).
3. **Inline snapshots for output-shaped tests** (B): [inline-snapshot](https://github.com/15r10nk/inline-snapshot) in copier-python's scanner and render tests. Reviewers judge partial or incorrect assertions badly (Kaufman et al. 2026), so one complete expected value beside its input is easier to check than scattered `in` asserts.
4. **Mermaid in LLDs, rendered by [mdbook-mermaid](https://github.com/badboy/mdbook-mermaid)** (D). Add a picture to the prose, don't replace it: in the experiments, diagrams added to text improved requirements comprehension with no time cost (Scanniello et al. 2014; Abrahão et al. 2013). Use a state diagram for lifecycles, a sequence diagram with `alt` branches for call chains with failure paths, and a flowchart for component edges.
5. **Decision tables beside EARS lists, and worked-state tables in place of narrative histories** (D, C). Tables win for lookup tasks (Vessey's cognitive fit). A decision table also shows where tests are missing or duplicated.
6. **Hide generated noise at the source** (F): mark lock files, dependency sidecars and vendored skill copies `linguist-generated` in `.gitattributes`, which none of the three repos has. Use [difftastic](https://github.com/Wilfred/difftastic) as the local diff driver for code and config. Markdown gets `--word-diff` instead, because difftastic doesn't parse Markdown.
7. **Form your own view before reading any AI review or explanation** (E, F). This is a reviewing habit, not a tool. AI review comments anchor reviewers on what they flag, saved no time and gave no confidence gain (Tufano et al. 2025, [exp]). Low-quality natural-language explanations of tests lowered reviewers' accuracy and raised their confidence (Kaufman et al. 2026, [exp]).

**Build on (existing libraries, some glue):**
- **Properties instead of hand-picked example tables, where a spec is universally quantified** (B, C): [Hypothesis](https://github.com/HypothesisWorks/hypothesis) in Python, [RapidCheck](https://github.com/emil-e/rapidcheck) in C++. RapidCheck goes inside QTest through `QVERIFY(rc::check(...))`; it has no QTest integration of its own. PortaBase ROW-DB-002, -011 and -012 are the first candidates: one property, or one stateful model of add, delete and compress against a list of IDs, would replace three hand-built `_data` rows.
- **Diff-scoped mutation testing as a reviewer signal** (B): mutate only the changed lines, cap the mutants per line, and show only the survivors. This is Google's pattern (Petrović et al. 2021). The tool depends on the stack:
  - [cosmic-ray](https://github.com/sixty-north/cosmic-ray) for copier-python, which runs its code under test in subprocesses, where mutmut can't record which tests reach a mutant;
  - [Mull](https://github.com/mull-project/mull) for PortaBase, which needs a Clang build.
- **Pairwise generators only when three or more factors interact** (C): PICT for QTest `_data` rows, allpairspy or pypict for pytest. No current spec in the example repos has more than two factors.
- **The input-space modelling rule** (C): borrow [Tcases](https://github.com/Cornutum/tcases)'s rule that each failure value appears in exactly one test case. Each EARS "If … then" clause becomes one failure class with one test.

**Custom pieces (nothing found does these):**
1. **A spec-ID review certificate and spec-anchored diff** (F, C). Group the slice by EARS ID: each spec line's diff, then the tests that cite the ID, then the code under its `@spec` annotation. End with a mandatory "unanchored hunks" bucket, so nothing is hidden. Build it on `lidc`'s spec-to-test-to-code links.
   - Borrow the "changed entities, static callers left unmodified, tests that reach the change" shape of [sem](https://github.com/Ataraxy-Labs/sem)'s `certify`.
   - Borrow the per-requirement mutation proof from [musthold](https://github.com/RachidChabane/musthold).
   - Neither covers EARS IDs at line granularity. sem splits Markdown into whole heading sections (verified in source). musthold expects requirement IDs in test names or pytest markers, and has no C++ support.
2. **Per-spec test reduction by marginal contribution** (C). For each EARS ID, find the mutants each citing test kills. Show reviewers the smallest subset that kills the same mutants, and collapse tests that add nothing unique as review candidates; never delete them automatically. Reduction on killed mutants cut about 51% of tests with no loss of kills, while reduction on statement coverage lost up to 20.5% (Shi et al. 2014). Add a lint for specs tested at two levels with the same scenario, the main redundancy found in the example repos.
3. **A seeded-defect "review gym"** (E). An agent plants one to three realistic defects in a copy of a real slice. The reviewer reviews it blind, and hits, misses and time are logged by defect category. This is the only route found to feedback on review accuracy, and confidence doesn't track accuracy (Kaufman et al. 2026; Perry et al. 2023). Borrow the scoring loop from CodeReview-Coach and the attacker role from Code Defenders. No tool that builds drills from one's own codebase was found on any route that could be reached.

**Don't adopt, on the evidence:**
- **AI review bots or summaries as a way to save reviewer time.** In a controlled experiment they saved no time (Tufano et al. 2025, [exp]). In industry, mean PR closure time rose 42% with one (Cihan et al. 2025, [obs]). Showing AI patches to reviewers raised review time by 6.7% at Meta (secondary source).
- **Changing language to cut review burden.** Language effects on defects are tiny or null at scale (Berger et al. 2019). Strict, enforced type checking matters instead, and both stacks already have it or can turn it on.
- **BDD/Gherkin for readability.** No controlled evidence was found, and it adds a step-binding layer to read.
- **Reviewing only specs plus tests and skipping the code.** Programmers judged incorrect LLM-written assertions correctly only 49% of the time, at the same confidence as for correct ones (Kaufman et al. 2026). A mining study of 88k PRs found spec artifacts didn't reduce defects (Hill 2026, [obs]; its "specs" were mostly ticket links).

## Candidates and matrix

Ranked shortlist, by how much each cuts review burden per unit of cost for these repos:

1. **Hidden generated noise and difftastic.** No risk, immediate. Wouldn't rank first if a slice rarely touched lock files or vendored files.
2. **Complexity ratchets (complexipy, clang-tidy).** Both are already in or next to the stack. Their evidence links them to comprehension time, not to defects.
3. **Mermaid with mdbook-mermaid, and decision tables in LID docs.** These target spec review, where the developer spends the most time. The evidence for diagrams is uneven: the benefit goes mostly to experienced readers, and one 2026 study found a detection cost for them.
4. **inline-snapshot.** Adoptable now for output-shaped tests; it doesn't fit behavioural tests.
5. **Hypothesis and RapidCheck properties.** High leverage where a spec says "for any …". Generators cost effort to write, and every copier-python test uses function-scoped fixtures, which trip Hypothesis's health check.
6. **Diff-scoped mutation (cosmic-ray, Mull).** The strongest signal about whether tests are adequate, but the slowest to run. PortaBase would need a Clang build.
7. **The spec-ID review certificate (custom).** The biggest gap in what exists. It would rank higher once `lidc` exposes its link data in a reusable form.
8. **The review gym (custom).** The only accuracy feedback loop found. Unproven, so it starts as a trial.

| Candidate | Class | License (file:line at commit) | Reason |
|---|---|---|---|
| complexipy | adopt | MIT (`LICENSE:1` @710ee3a) | Python cognitive complexity with a diff gate (`crates/complexipy-core/src/diff.rs:603-611`) |
| clang-tidy cognitive complexity | adopt (native) | Apache-2.0 with LLVM exception (not read from file) | Already enabled in PortaBase; tighten the threshold |
| lizard | adopt (report) | MIT-style (`LICENSE.txt:11` @ff2f984) | One cross-language cognitive-complexity report; no diff mode |
| vulture | adopt | MIT (`LICENSE.txt:1` @edd5806) | Dead code; default confidence 60 is noisy (`vulture/core.py:15`) |
| jscpd | adopt (optional) | MIT (secondary listing, not read) | Duplicated blocks in C++ and Python |
| inline-snapshot | adopt | MIT (`LICENSE:2` @5471fe0) | One literal oracle per test, updated as a source diff |
| Hypothesis | build on | MPL-2.0 (`LICENSE.txt:3-4` @8fca8fd) | Properties and stateful models for Python |
| RapidCheck | build on | BSD-2-Clause (`LICENSE.md:4-8` @2c3c436) | C++ properties; glue through QVERIFY |
| ApprovalTests.cpp | borrow ideas | Apache-2.0 (`LICENSE:1-3` @f90a718) | Approved state dumps; no QTest integration |
| cosmic-ray | build on | not read (PyPI copyright line; GitHub reports MIT) | Mutation on disk works with subprocess-based tests |
| mutmut | borrow ideas | BSD-3-Clause (`pyproject.toml:11` @c37062f) | Records test-to-mutant hits in process only |
| Mull | build on (later) | Apache-2.0 (`LICENSE:1-2` @dab0b59) | C++ mutation testing; needs Clang/LLVM 16 or later |
| kalku | borrow ideas | MIT OR Apache-2.0 (`LICENSE-MIT`, `LICENSE-APACHE` @aec0cd1) | Agent-oriented mutation testing across languages, including C++, but C++ needs CMake; beta, created 2026-09 |
| ripr | borrow ideas | MIT OR Apache-2.0 (`LICENSE-MIT`, `LICENSE-APACHE` @ec2fcfe) | Static "tests run this change but don't check it" analysis; Rust first, Python in preview |
| musthold (+ Shallnot) | borrow ideas | Apache-2.0 (`LICENSE:1` @97032f3) | Per-requirement mutation proofs inside the agent loop; repo created 2026-10-26; pytest yes, C++ no |
| PICT | build on | MIT (`LICENSE.TXT:3` @ab76c25) | t-way generation with constraints; no adapter for QTest or pytest |
| coverwise | build on | Apache-2.0 (`LICENSE:2` @fa1f897) | Reports a suite's uncovered tuples; never removes rows |
| Tcases | borrow ideas | MIT (`LICENSE.txt:3` @bb00b90) | Failure-class modelling; Java/JUnit output only |
| recov / TestIQ | borrow ideas | MIT (`LICENSE:1` @9f9af9c / @26ec8e3) | Coverage-based test redundancy; each has a counting flaw (below) |
| Mermaid + mdbook-mermaid | adopt | mdbook-mermaid MPL-2.0 (`LICENSE:1`, `Cargo.toml:6` @bfc8839); Mermaid not read | GitHub renders Mermaid natively; mdBook needs the preprocessor |
| LikeC4 | borrow ideas | MIT (`LICENSE:1` @1512779) | Model diffs that list the views a change affects; overkill for one app |
| CodeBoarding | borrow ideas | MIT (`LICENSE:1` @13adc4a) | LLM architecture maps of code, not specs; telemetry on by default |
| difftastic | adopt | MIT (`LICENSE:1` @0b92338) | Structural diff; no Markdown |
| sem | borrow ideas | MIT OR Apache-2.0 (`LICENSE-MIT:1`, `LICENSE-APACHE:1` @76f97a9) | Entity diffs and a review certificate; Markdown granularity is per section |
| PR-Agent | borrow ideas | MIT (`LICENSE:1` @3871eda) | Priority-file and can-be-split options; evidence for AI review is negative |
| gh-stack / jj / git-absorb | adopt when slices outgrow one commit | MIT / Apache-2.0 / BSD-3 (API metadata, not read) | Stacking and fixup folding; no controlled evidence that stacking speeds review |
| Code Reading Club | borrow ideas | MIT (`LICENSE:1` @e531ea8) | Comprehension exercises for a group; nothing on finding defects |
| CodeReview-Coach | borrow ideas | MIT (`LICENSE:1` @e3bdf58) | Scoring loop for seeded-defect drills; fixed content, no C++ |
| OWASP Secure Coding Dojo | borrow ideas | Apache-2.0 (`LICENSE:1` @b362860) | Format for a known-answer drill; 17 tiny questions |
| CodeScene, Graphite, CodeRabbit, Greptile, SemanticDiff, Secure Code Warrior | reject as defaults; springboards | commercial | Vendor evidence only, apart from CodeScene's Code Red study (also vendor-authored) |
| deadcode, pytest-deduplicate | reject | AGPL-3.0 (`LICENSE:1` @ea26bcb) / GPL (PyPI field) | License is awkward for a template default; vulture covers the need |
| pytest-bdd, radon/wily, GraphWalker, DeepWiki/GitDiagram | reject | MIT (PyPI or API fields) | No comprehension evidence (BDD); weaker metric (radon); Java GUI-flow oriented (GraphWalker); no link to specs (DeepWiki/GitDiagram) |

**Matrix** (hard criteria 1-4 and the stack-fit preference). Abbreviations: `n` native, `p` partial, `e` extensible, `u` unsupported, `?` unverified.

| Candidate | 1 License | 2 Local | 3 Python | 3 C++/Qt | 3 Markdown | 4 Human in charge | Evidence |
|---|---|---|---|---|---|---|---|
| complexipy | n | n | n | u (`Cargo.toml:27-28`, ruff parser) | — | n | [obs] metric validity |
| clang-tidy CogC | n | n | — | n (`.clang-tidy:6`) | — | n | [obs] |
| vulture | n | n | n | u | — | n (whitelist) | [exp] size |
| inline-snapshot | n | n | n | u | — | n | [exp] Kaufman (indirect) |
| Hypothesis | n | n | n | u | — | n | [qual] Goldstein |
| RapidCheck | n | n | — | e (no QTest; `extras/` listing) | — | n | [qual] |
| cosmic-ray | ? | n | n | u | — | n | [obs] Petrović |
| Mull | n | n | — | p (needs Clang build) | — | n | [obs] |
| musthold | n | p (host agent answers some proofs) | n (pytest marker, `discpower.md:128`) | u (README language list) | p (Shallnot spec format) | p (an agent loop gate) | [untested] |
| PICT | n | n | e | e | — | n | [obs] Kuhn |
| mdbook-mermaid | n | n | — | — | n (html renderer only, `src/lib.rs:34-35`) | n | [exp] Scanniello |
| difftastic | n | n | n | n (`guess_language.rs:30`) | u (listing) | n | [exp-weak] RAID |
| sem | n | n | n | n (`languages.rs:730`) | p (per section, `markdown.rs:22,105`) | n | [untested] |
| PR-Agent | n | p (needs an LLM API) | n | n | p | p (anchoring risk) | negative ([exp] Tufano) |
| CodeReview-Coach | n | n | p | u (listing) | — | n | [untested] |

**Blends considered.**
- complexipy plus clang-tidy for complexity: adopted, one tool per language.
- Hypothesis plus mutation testing, rather than either alone: properties shrink the test text, and mutants show whether it still bites.
- musthold plus `lidc`, as a ready-made spec-ID certificate: rejected for now. musthold cites requirements in test names, not through `@spec` comments; has no C++; and is days old.
- sem plus `lidc`: kept as the seed of custom piece 1.

**Scenario walk.**
1. *A new EARS requirement in PortaBase* (ROW-DB-0xx, "for any batch delete…"). The LLD gets a state diagram and a state × operation decision table. The test becomes one RapidCheck property under QVERIFY. clang-tidy flags a function that got more complex. The reviewer reads one table row, one property line and the code. Nothing here breaks the qmake build. Mull is the step that needs a Clang build.
2. *An automated Renovate upgrade PR*. The lock-file and sidecar diffs are collapsed as `linguist-generated`. No reviewer action is needed beyond CI.
3. *A copier-python scanner change*. An inline snapshot shows the full expected output. complexipy's diff gate catches a new nested function. cosmic-ray survivors on the changed lines list what the tests miss. mutmut would have shown no coverage, because the code runs in a subprocess.
4. *A reviewer on GitHub reading an LLD*. Mermaid renders natively on GitHub. On the mdBook site it needs mdbook-mermaid. A Mermaid syntax error doesn't fail the mdBook build (verified), so CI needs its own render check.

## musthold and Shallnot in depth

Both were read at source: [musthold](https://github.com/RachidChabane/musthold) @97032f3 and [Shallnot](https://github.com/RachidChabane/shallnot) @397e092. Both are Apache-2.0 (`LICENSE`); musthold's `NOTICE` lists MPL-2.0 Go dependencies, used unmodified. Each has one author, with 646 and 58 commits. The musthold repo went public on 2026-10-26 with its history already in place, and it has no issues or outside contributors yet.

**What each does.**
- **Shallnot** is a traceability gate. A requirement counts as covered only when a test that cites it ran and passed, as read from the runner's JUnit XML. A requirement's revision is part of every citation (`ID~REV`), so a change of meaning invalidates the tests written against the old one.
- **musthold** adds per-requirement proofs on top:
  - **discriminating power** (blocking): mutants of the requirement's footprint (operator mutants, behaviour-neutral sentinels, and realistic faults written by an LLM) must be killed by the tests bound to it;
  - **alignment** (escalates): a blind judge checks that each test checks what its requirement says;
  - **completeness** (advisory): what the spec leaves unstated about the change.

  The binaries never call a model themselves. They write requests that the host agent answers in isolated subagents, and only execution decides a block (`docs/usage/discpower.md:12-60`).

**Close to LID:**
- Shallnot's Markdown declaration grammar reads LID's spec lines as they are written: a list marker, an optional `[ ]`/`[x]` checkbox, optional `**` emphasis, then `ID:` (`internal/adapters/spec/markdown.go:14`).
- It recommends EARS wording (`docs/spec-format.md:40-45`). Its ID pattern is configurable (`docs/spec-format.md:48-70`).
- musthold's per-mutant kill vectors (`musthold-dp facts show`) are exactly the data that per-spec test reduction (custom piece 2) needs.

**Gaps against LID and these repos:**
- *Citation form.* A test cites a requirement in its name or a pytest marker as `[verifies ID~REV]`, and every citation needs a revision. A tag inside a comment never binds (`docs/binding.md:15-16,23-30`). LID's `@spec ID` comments carry no revision. Using Shallnot would mean either a second citation per test or a Shallnot mode that reads `@spec` comments and treats the missing revision as 1.
- *ID shape.* The default pattern `[A-Z][A-Z0-9]*-[0-9]+…` doesn't match multi-segment IDs such as `ROW-DB-001`, so a custom `id_pattern` is needed (configurable; not tested).
- *Deferred specs.* `[D]` isn't an accepted checkbox (`markdown.go:14`), so a deferred line isn't read as a declaration at all. That is probably the right outcome for LID, but only by accident.
- *Subprocess tests.* The pytest adapter traces what each test reaches in process only. `scripts/coverage_plugin.py` uses `sys.settrace`/monitoring, and `grep -n "subprocess\|fork"` over it finds nothing. copier-python's scanner tests run their code through `subprocess.run`, so the footprint would come out empty. That consequence is inferred, not run.
- *No C++.* musthold covers pytest, Go, Jest, Vitest and JUnit 5 (`discpower.md:124-140`). A QTest/qmake ecosystem would need:
  - an ecosystem adapter: build, select tests, read JUnit XML, record per-test coverage. The pytest adapter is about 1,600 lines of Go, and the Node one about 4,000.
  - a C++ mutation adapter. The Python one is about 1,000 lines, and C++ needs a real parser. QTest's JUnit output would also have to carry the citation, for example in a data-row name, which is untested.
- *Weight.* About 270k lines of Go including tests, and 47k non-test lines in `discpower` alone. Each requirement proof costs several host-agent subagent calls. CONTRIBUTING requires spec-first changes traced by Shallnot, conventional commits, and no AI attribution in commits.

**Assessment.**
- Shallnot is the more reusable piece: small, focused, and close to LID's spec format. Two upstream proposals would let it read LID repos without a fork: `@spec`-comment binding with an implicit revision, and multi-segment ID examples in the docs.
- musthold's discriminating-power proof is the strongest test-adequacy check found, but it is too heavy and too young to depend on yet. Try `musthold-dp scan`, which needs no spec, on a pytest repo whose tests run in process (7 of agentic_development's 12 test files don't use `subprocess`) before deciding whether to contribute, fork or borrow.
- Contributing C++ support would be a large change to a single-author codebase with strict process rules. Ask the author first.

## Follow-up quick passes (2026-10-28)

### Render checks for Mermaid in CI

- **[merman](https://github.com/Latias94/merman)**: MIT OR Apache-2.0 (`LICENSE-MIT`, `LICENSE-APACHE` @8eba295).
  - A Rust re-implementation of Mermaid that its docs call the "strict semantic and rendering authority" (README).
  - It has a `lint` command, a Markdown batch mode and a mermaid-cli-compatible mode (`docs/FEATURES.md:199,429,438-443`; *docs only*).
  - The CLI's render and batch commands propagate errors (`crates/merman-cli/src/commands.rs:95-117`).
  - **Best fit** for failing CI on a diagram that doesn't parse.
- **[mermaid-rs-renderer](https://github.com/1jehuang/mermaid-rs-renderer)**: MIT (`LICENSE:1` @3726ccb).
  - It exits 1 on an error (`src/main.rs:2-4`) and extracts every Mermaid block from a Markdown file (`src/cli.rs:143-152`).
  - But the CLI calls the lenient `parse_mermaid` (`src/cli.rs:6,173,255,288`), not the validating `parse_mermaid_strict` (`src/lib.rs:290-295`). So a malformed diagram can still render, and only some errors fail the run, such as an unknown diagram header (`src/parser.rs:61`).
- **mermaid-cli** (`mmdc`), the official renderer, needs a headless Chromium. It is heavier than either, and wasn't read.

### Markdown diffs that look like tracked changes

The need: review prose changes in long sentences and paragraphs, seeing exactly which words changed, rendered with strikethrough and highlighting rather than as raw line diffs.

| Candidate | Class | License | Notes |
|---|---|---|---|
| GitHub rich diff (native) | adopt | — | In commits and PRs, the file header's rendered-view button shows removed text struck through on red and added text on green. Changed link URLs appear in tooltips. Very large changes may fail to render, and comments must be added in source view ([GitHub docs](https://docs.github.com/en/repositories/working-with-files/using-files/working-with-non-code-files#rendering-differences-in-prose-documents); *docs only*) |
| [markdown-diff-viewer](https://github.com/PiotrTrzpil/markdown-diff-viewer) (`md-diff`) | adopt for local review (trial) | MIT (`LICENSE:1` @072632e) | A rendered side-by-side browser view, with blocks matched by similarity and highlights down to the word or character. Compares between git refs, and against the working tree or the index (`src/git/index.ts:41,113-116`), so it works before a commit. Node, one author, created 2026-02 |
| [pandiff](https://github.com/davidar/pandiff) | build on | MIT (`LICENSE:1` @2631bb9) | Pandoc-based prose diffs. Outputs CriticMarkup, HTML, PDF, or Word with real Track Changes. Has a `git pandiff` difftool recipe (README:91-100). Needs Pandoc. Last commit 2025-05 |
| [rich-markdown-diff](https://github.com/phine-apps/rich-markdown-diff) | borrow ideas, or adopt if VS Code is in use | MIT (`LICENSE:1` @5c78132) | A VS Code extension: rendered inline or side-by-side diffs, including a diff of Mermaid nodes and edges |
| [redlines](https://pypi.org/project/redlines/) | build on | not read (no license in the PyPI metadata) | A Python library that writes Word-style track-changes output, for a custom review page |
| Semantic line breaks ([sembr.org](https://sembr.org)) | borrow ideas | — | A writing convention: one sentence or clause per line, so even a plain line diff isolates the changed sentence. [untested] for review speed. Moving existing docs to it costs one large reflow diff |

Quick pass. Searched GitHub ("markdown diff", "prose diff", "track changes markdown", "rendered markdown diff", "redline diff", "word diff html"), npm ("markdown diff", "prose diff", "htmldiff") and PyPI (redlines), plus GitHub's docs. Snowball from pandiff and md-diff added only small or pre-alpha tools: mddiff, the tom Git client, and an Obsidian plugin.

## Limitations checked in source

Verified:
- complexipy's diff gate fails only functions that are new or regressed *above* the maximum, so a regression below the maximum passes (`crates/complexipy-core/src/diff.rs:603-611` @710ee3a). The default maximum is 15 (`config.rs:10`).
- lizard doesn't count preprocessor conditionals (`lizard_ext/lizardcognitive.py:30-31` @ff2f984), and its options have no diff or baseline mode (`grep -n "diff\|baseline" lizard_core/options.py`).
- inline-snapshot can't update snapshots under pytest-xdist (`src/inline_snapshot/_snapshot_session.py:359-361` @5471fe0). copier-python doesn't use xdist (grep over `pyproject.toml` and `mise.toml`).
- Hypothesis's health check fires when a function-scoped fixture is reused across examples (`_hypothesis_pytestplugin.py:256,290` @8fca8fd).
- RapidCheck has no QTest integration (`grep -rli qtest extras/ include/` @2c3c436). `rc::check` returns `bool` (`include/rapidcheck/Check.h:11`).
- ApprovalTests.cpp has no QTest integration (`grep -rn QTest ApprovalTests/` @f90a718). Its Qt add-on supports Catch2 only.
- mutmut records test-to-mutant hits in process (`src/mutmut/stats.py:150-171` @c37062f). That hits made in a subprocess are lost is an inference, not tested.
- recov flags each test whose coverage is a subset of the union of all the others, so two tests that duplicate each other are both flagged, and deleting both loses coverage (`src/recov/__init__.py:276-282,329-337` @9f9af9c). It has no set-cover step (grep).
- TestIQ compares tests in pairs only (`src/testiq/analyzer.py:158-161` @26ec8e3).
- coverwise reports uncovered tuples but has no output for removable rows (`src/model/test_case.h:65-107` @fa1f897).
- Tcases writes only JUnit, TestNG, HTML and JSON output (`ls tcases-io/src/main/java/org/cornutum/tcases/io/` @bb00b90).
- mdbook-mermaid renders only for the html renderer (`src/lib.rs:34-35` @bfc8839), and doesn't validate Mermaid syntax (`src/lib.rs:53-105`).
- LikeC4's validate checks drift between manual layout and the model, not between the model and the code (`packages/likec4/src/cli/validate/index.ts:84-93` @1512779).
- CodeBoarding analyzes source files by suffix only, so design docs aren't read (`static_analyzer/config.py:100-118` @13adc4a). Its telemetry is on by default (`TELEMETRY.md:5-12`).
- difftastic doesn't parse Markdown (`grep -rni markdown src/parse/` @0b92338). Its JSON output is unstable (`src/options.rs:813-814`).
- sem treats a whole Markdown heading section as one entity (`crates/sem-core/src/parser/plugins/markdown.rs:22,105` @76f97a9).
- PR-Agent caps repo-context files at 500 lines, matched by globs within one directory (`configuration.toml:42,47` @3871eda).
- CodeReview-Coach's exercises are fixed, with no C++ (`src/data/exercises/starterExercisePack.ts:208`; grep @e3bdf58).
- Code Reading Club's exercises include no defect-finding exercise (`grep -n -i -E "bug|defect|review" exercises.md` @e531ea8).
- musthold binds pytest tests through Shallnot's `verifies` marker (`docs/usage/discpower.md:128` @97032f3) and cites requirements in test names (`docs/architecture.md:57-58`). Both are docs in the repo.
- PortaBase's clang-tidy setup enables `readability-*` with `WarningsAsErrors: ''` (`.clang-tidy:6,16`). `docs/book.toml` has no Mermaid preprocessor. None of the three repos has a `.gitattributes` file (listing).

Could not verify:
- kalku's limit that C++ projects must build with CMake, read from its README status table (*docs only*, `README.md:301` @aec0cd1).
- musthold's language list (*docs only*, README).
- gh-stack, Graphite, SemanticDiff, CodeScene, CodeRabbit and the other commercial products: every limitation is *docs only*.
- The licenses of jscpd, cosmic-ray, Mermaid, gh-stack, jj and git-absorb, which were read from metadata only.
- Most research papers were read as abstracts only. Read in full or in their statistics sections: Inozemtseva & Holmes 2014, Shi et al. 2014, and Scanniello et al. 2014. Several 2026 preprints (Kaufman et al., arXiv 2607.08885; Banik et al., arXiv 2606.18168; Hill, ESEM 2026; Belhouchette et al., arXiv 2607.20189) were read from abstracts, or from search summaries where noted below. Two researchers found Kaufman et al. independently.
- Not found: Rong et al.'s study of training with checklists; Kemerer & Paulk's study of review rate; any study of how many tests a reviewer can meaningfully review.

## Research evidence by angle

Strength tags: [exp] a controlled experiment with a significant result; [exp-weak] an experiment without significance; [obs] large-scale mining; [qual] interviews or surveys; [vendor] a vendor case study; [untested] no study has tested it.

**A. Less and simpler software**
- Muñoz Barón, Wyrich & Wagner, ESEM 2020 ([arXiv 2007.12520](https://arxiv.org/abs/2007.12520)): cognitive complexity correlates with comprehension time and perceived difficulty; results are mixed for correctness. Meta-analysis of about 24k evaluations. [obs]
- Peitek et al., ICSE 2021 (fMRI, n=19): text size drives attention and vocabulary size loads working memory; complexity metrics explain little. [exp]
- Scalabrino et al., TSE 2019: no single metric captures understandability. [exp-weak]
- Gopstein et al., FSE 2017, plus the Langhout & Aniche Java replication ([arXiv 2103.05424](https://arxiv.org/abs/2103.05424)): "atoms of confusion" (small confusing code patterns) cause misreadings. Bogachenkova et al., ICSME 2022: reviewers don't flag them reliably, so they belong in a linter. [exp] and [obs]
- Hofmeister et al., SANER 2017: full-word identifiers led to finding defects 19% faster. [exp]
- Berger et al., TOPLAS 2019 ([arXiv 1901.10220](https://arxiv.org/abs/1901.10220)), reproducing Ray et al.: language effects on defects are tiny or null. [obs]
- Gao et al., ICSE 2017, and Khan et al., TSE 2021: type checkers would have caught about 15% of shipped bugs. Di Grazia & Pradel, FSE 2022: without enforcement, typing erodes. Mündler et al., PLDI 2025: type-constrained decoding cuts LLMs' compile errors by more than half. [obs], [exp]
- Tornhill & Borg, "Code Red" ([arXiv 2203.04374](https://arxiv.org/abs/2203.04374)): files with low code health had 15 times more defects and took 124% longer per issue. [vendor/obs]

**B. Tests that are easy to review**
- Kaufman et al., arXiv 2607.08885 (n=86): programmers judged correct LLM-written assertions correctly 74% of the time and incorrect ones 49%, with the same confidence (p<0.001). Low-quality explanations lowered accuracy and raised confidence. [exp]
- Banik et al., arXiv 2606.18168 (86k test patches written by agents): 80.2% have a weak oracle or none, so counting test files overstates verification. [obs]
- Spadini et al., ICSE 2019 (n=93): reviewing the tests first finds more test defects and the same production defects. [exp]
- Petrović et al., TSE 2021 and ICSE 2021 (Google): diff-scoped mutants are actionable in review, and developers shown them write better tests over time. [obs]
- Goldstein et al., ICSE 2024 (30 interviews): property-based testing pays off in a few idioms (round trip, model, differential), and judging a property's effectiveness is the pain point. Tyche, UIST 2024: visualizing the generated inputs helps with that. [qual], [exp-weak]
- Bavota et al., EMSE 2015: comprehension was about 30% better without test smells. Winkler et al., EMSE 2024: 14 factors of test readability. [exp]
- BDD and Gherkin comprehension: no controlled study found. [untested]

**C. The right number of tests**
- Inozemtseva & Holmes, ICSE 2014 (read in full): suite effectiveness tracks suite size; with size controlled, coverage correlates only weakly. [obs]
- Shi et al., FSE 2014 (read in full): reduction on statement coverage cut 62.9% of tests but lost up to 20.5% of killed mutants; reduction on killed mutants lost no kills at about a 51% cut. [obs]
- Kuhn, Wallace & Gallo, TSE 2004 (NIST): the share of field failures triggered by interactions of up to 1, 2, 3, 4 or 6 factors was 66%, 97%, 99%, 100% and 100% for medical devices; no known fault needs more than 6. [obs]
- Spadini et al., ICSE 2018, and a 2026 replication ([arXiv 2603.15935](https://arxiv.org/abs/2603.15935)): test files get less review attention, and in recent PRs the median review probability for test files is zero. [obs]
- Counts in the example repos:
  - copier-python cites all 149 EARS IDs, at a maximum of 6 tests per spec.
  - In agentic_development, CHECK-RUN-008 is tested at both the integration and the unit level. A decision table would take it from about 10 cases to about 6.
  - PortaBase's `addColumn_data` covers one factor exhaustively, so pairwise testing can't shrink it.

**D. Specs and docs**
- Scanniello et al., EASE 2014 (n=87, with a replication): requirement diagrams added to text gave significantly better comprehension at no time cost. [exp]
- Abrahão et al., TSE 2013 (5 experiments, n=112): sequence diagrams help, mostly for high-ability readers. Broccia et al., [arXiv 2601.16009](https://arxiv.org/abs/2601.16009): an interaction with working memory, and high-ability readers found fewer violations with UML. [exp]
- Vessey 1991 (cognitive fit): tables win for symbolic lookup tasks, graphs for relations among many items. [exp]
- Großer et al., Requirements Engineering 2024 (1,764 requirements, plus a usability experiment with n=43): templates such as EARS improve quality over free text, with no clear favourite among them. Nobody has measured how fast EARS is to read. [exp]
- Femmer et al. 2016 (Smella): automated detection of requirements smells at 59% precision and 82% recall, as an aid to review. [obs]
- Diátaxis, C4 and arc42 reading time: no empirical evaluation found. [untested]
- Benchmarks of LLM-generated state machines from requirements (2026): states F1 about 0.90, transitions about 0.75, with guards and actions the weakest. [exp-weak]

**E. Reviewer skill**
- Tufano et al., ICSE 2025 (n=29 experts): an AI-generated review anchors reviewers on the places it flags, with more low-severity findings, no time saved and no gain in confidence. [exp]
- Perry et al., CCS 2023: users of an AI assistant wrote less secure code and rated it more secure. [exp]
- Uwano et al. 2006 and Sharif et al., ETRA 2012: scanning the whole change first goes with faster defect detection. [exp-weak]/[exp]
- Chen et al., FSE 2024: reviews that give their rationale and a sample solution teach more. [qual]
- Han et al., SCAM 2020: review comments remove only a minority of convention violations, so those belong in tools. [obs]
- Dunsmore 2000, via *Making Software*: defect finding drops after 60-90 minutes. [obs, secondary]

**F. How changes are structured**
- Cihan et al., ICSE-SEIP 2025 ([arXiv 2412.18531](https://arxiv.org/abs/2412.18531)): with AI review, mean PR closure time rose 42%. [obs]
- Xiao et al., FSE 2024: PRs with Copilot-generated descriptions needed less review time. [obs]
- Brito & Valente (RAID, field study with n=8): refactoring-aware diffs cut the lines to review for move refactorings from a median of 14.5 to 2. [exp-weak]
- Belhouchette et al., ESEM 2026, read from a search summary of the abstract: changes in a Gerrit relation chain take a median 2.6 times longer to merge than size-matched solo changes. No controlled study of stacking was found. [obs]
- Hill, ESEM 2026 (88k PRs): spec artifacts didn't reduce defects. [obs]

## Coverage ledger

Six researchers searched in parallel, one per angle; the lead then retried the rate-limited GitHub routes. "Searched (A-F)" lists the angles that searched a route.

| Route | State | Queries or reason |
|---|---|---|
| The stack itself | searched | ruff `select=["ALL"]` with no cognitive-complexity rule; ty strict; pytest parametrize; PortaBase `.clang-tidy`; QTest `_data`; mdBook `book.toml`; Mermaid already in two HLDs; `lidc` and `@spec`; no `.gitattributes` |
| Earlier notes and decisions | searched | `docs/prior-art/` (four notes, none on this topic); the developer's earlier review-presentation search (private, restated above) |
| GitHub repository search | searched (A-F, then the lead after a rate limit) | e.g. "cognitive complexity", "mutation testing", "property based testing", "snapshot testing", "test redundancy", "pairwise testing", "stacked diffs", "structural diff", "code review training", "ears requirements", "requirement mutation tests", "review certificate diff" |
| GitHub topics | searched (lead's retry) | `topic:mutation-testing`, `topic:property-based-testing`, `topic:code-review topic:llm`, `topic:agent-skills code review`; plus C's pairwise-testing, combinatorial-testing, model-based-testing and requirements-traceability |
| GitLab | searched (A-F) | "cognitive complexity", "mutation testing", "snapshot testing", "pairwise testing", "diagram as code", "requirements smell", "stacked diffs", "code review training"; nothing serious |
| Codeberg | searched (A-F) | single-word queries (complexity, mutation, snapshot, pairwise, mermaid, stacked, code review); nothing serious |
| npm | searched (A-F) | "cognitive complexity", "snapshot testing", "mutation testing", "pairwise testing", "mermaid diagram diff", "ears requirements", "stacked pull requests", "code review training" |
| PyPI | searched (A, B, C by direct JSON lookup); unavailable for keyword search (D, E, F) | the search page returns a JavaScript challenge; names were checked directly through `pypi.org/pypi/<name>/json` and `site:` web search |
| crates.io | searched (A-F) | "cognitive complexity", "mutation", "proptest", "pairwise", "mermaid", "ears requirements", "structural diff", "code review training" |
| C++ registries (vcpkg, Conan) | searched (B, C); excluded (A) | B found RapidCheck and ApprovalTests.cpp on Conan/vcpkg; A: C++ complexity tools ship as CLIs, not packages |
| Cross-language equivalents | searched | Hypothesis → RapidCheck; ApprovalTests → ApprovalTests.cpp; mutmut → Mull and kalku; PICT → allpairspy and pypict; RAID (Java) → difftastic and sem |
| Awesome lists | searched (A, B, C, D, E); excluded (F) | awesome-static-analysis, awesome-mutation-testing, awesome-code-review, diagramming lists; F excluded the route because its candidates were already found by other routes |
| alternativeto.net | searched (D, F) | Mermaid, difftastic, Graphite (through web search) |
| General web search | searched (A-F) | more than 80 queries in all, including named papers, "X vs Y" comparisons and vendor evidence |
| Hosted and commercial services | searched (A-F) | CodeScene, SonarQube, GitClear, Graphite, CodeRabbit, Greptile, Copilot review, SemanticDiff, Swimm, AppMap, Secure Code Warrior, TESTONA/CTE, Keploy, Testomat.io, Diffblue |
| aitoolnet.com | unavailable | HTTP 403 (Cloudflare) on every fetch, retried; `site:` web searches returned no aitoolnet pages |
| Skill directories (skills.sh) | searched (E, F) | "code review", "review practice", "seeded bugs", "stacked pr", "split commits", "pr description" |
| Claude Code plugin marketplaces and anthropics/skills | searched (F) | review and simplification skills; Anthropic's Code Simplifier plugin noted by A |
| Research literature | searched through web search, OpenAlex and arXiv abstract pages; the Semantic Scholar API was unavailable (HTTP 429) and the arXiv API intermittently so (503, empty responses) | per-angle queries listed in each research section above |

## Snowball rounds

- **Round 1** (route queries in every angle): complexipy, lizard, vulture, Hypothesis, RapidCheck, inline-snapshot, ApprovalTests, mutmut, cosmic-ray, Mull, PICT, recov, Mermaid, mdbook-mermaid, CodeBoarding, LikeC4, difftastic, PR-Agent, gh-stack, Code Reading Club and CodeReview-Coach, plus the core papers.
- **Round 2**: Tcases, coverwise, TestIQ, Tyche, agentic-pbt, sem, semantic-review, jj-hunk, OWASP Dojo, project-teach, Code Defenders, and the oracle-strength and anchoring papers from 2025-26.
- **Round 3**: no new serious candidate in any angle (Mewt, Poodle, atestcov, code-maat and others were minor).
- **Round 4** (the lead's GitHub retry after the rate limit): musthold and Shallnot, kalku, ripr and oxlint-plugin-complexity-hints. musthold, kalku and ripr were read at source.
- **Round 5** (seeded from round 4: "requirement mutation tests", "spec tests agent proof", "oracle strength tests", "review certificate diff", "ears requirements", "seeded defects review"): only ears-parser and small EARS traceability projects. No new serious candidate, so the search stopped.

## Refresh trigger

- When a custom piece is designed, re-run this search for that piece.
- musthold and kalku are weeks old and moving fast: recheck them by 2027-04, or sooner if musthold adds C++ or `@spec`-style citations, or kalku adds qmake support.
