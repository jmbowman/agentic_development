# System synthesis: assembling an agentic development process from best-of-breed parts (2026-11-10)

A design proposal for review, not yet adopted intent. It maps what the prior-art search in [the companion note](2026-11-09-agentic-development-process.md) found onto the software lifecycle and LID's arrow, says which piece is best at each stage and how the pieces fit, and lists the decisions that need the developer. Decisions taken from it flow into the HLD and LLDs through LID.

## The aim

One developer directing coding agents should be able to deliver high-quality, maintainable software quickly. Building a complete process from nothing would take years. Assembling the best existing piece for each lifecycle stage ("diamonds") and filling the gaps between them should give something useful early that improves with use. LID (HLD → LLD → EARS → edge audit → tests first → code) is the first diamond and stays the spine. At the current stage the developer reviews closely and makes every commit. Agent commits, pull requests and stacked pull requests come later. Agent work never merges to the default branch without the developer.

## How to read the evidence

Every claim carries a tag for how it is known:

| Tag | Meaning |
|---|---|
| **[S]** | Verified in source: the files were read in full at the commit listed in the appendix |
| **[s]** | Source read at snippet depth only |
| **[D]** | Documentation only (closed-source products, and tools whose source was not read) |
| **[P]** | Reported in a paper; the paper table gives how much of each was read |
| **[X]** | Practitioner or vendor report, usually without a control |
| **[R]** | This repo's own records (`docs/review-log.md`, `docs/process-lessons.md`) |
| **[dev]** | Reported by the developer |

Three limits apply throughout:

- Almost no candidate measures outcomes in real projects. "Measured" nearly always means a tool's own guards or its own small eval.
- Claude Code's own features (hooks, the sandbox, permission rules, path-scoped rules, the Workflow tool, `/code-review`) are documentation only. Nothing about the sandbox has been tested here, and the one experiment on it is macOS-only, with one to three runs per cell, on a proprietary plugin, unreviewed.
- A tool's source being verified says its mechanism exists and works as described. It says nothing about whether the mechanism improves outcomes; several of the best-built tools report null or unfavorable results of their own.

## Summary

| Stage | Now | Best piece found | Verdict |
|---|---|---|---|
| 1. Intent (HLD) | LID, prior-art search skill | No diamond beyond LID | Keep; borrow an expiry field for decision evidence |
| 2. Design (LLD) | LID, spikes, LLD probe | BMAD's edge-case lens used on plans | Borrow and reimplement the lens |
| 3. Requirements (EARS) | LID, `lidc` ID format | letspecify's deterministic EARS lint | Propose to `lidc` |
| 4. Spec and plan review | Review waves by convention | letspecify's gate on critic verdicts; closed defect lists | Build, as part of the review orchestrator |
| 5. Edge audit | LID's blind divergence probes | LID is the diamond | Keep unchanged |
| 6. Tests first | Prose | red-first-gate's baseline-red proof; qikly's withholding of the implementation from the test writer | Borrow and reimplement both: a property check, and independence by context |
| 7. Implementation loop | Prose | superpowers' scoped fix loop; Habit Hooks (lint findings as fix guidance) | Borrow the loop; trial Habit Hooks; adopt native path-scoped rules |
| 8. Tests against requirements | `lidc coverage` (a citing test file exists) | promptwheel's source-only re-run; runner-proven coverage | Borrow and reimplement the re-run for CI; propose coverage to `lidc` |
| 9. Review waves and triage | Prose, hand-kept log | craftsman (dispatch), Compound Engineering and BMAD (triage) | Build on borrowed designs; craftsman trial is a decision |
| 10. Stopping | Judgment | craftsman's coded wave trigger and cap | Borrow and reimplement |
| 11. Traceability and staleness | `lidc` three checks | Habeas Codicem, 2119, musthold (hash-bound evidence) | Propose upstream; build a shim only if declined |
| 12. Commit, PR, merge | Developer commits | dev-process-toolkit's ratchet; DAW's sealed approval; disensor's witness gate | Borrow and reimplement, rung by rung |
| 13. Enforcement and calibration | One SessionStart hook; `lidc` gate | Claude Code's sandbox and permission rules (native); a2dlc (base-commit judging); cairn (guard fixtures) | Adopt the native layer after a test; borrow the two house rules; defer the phase state machine |
| 14. Learning capture | session-wrap-up skill | Compound Engineering's form ladder | Borrow into session-wrap-up |
| 15. Evaluating the process | `claude plugin eval`, review log | agentops (pre-registration, A/A bar); layered-code-review (revert-mined evals) | Adopt the methods |

The enforcement design has two layers, and neither is a custom hook framework:

- **Protect the process's own files at the OS layer.** Claude Code's sandbox stops shell commands writing to protected paths whatever the command looks like, and permission deny rules do the same for the file-editing tools. In the one experiment found, a text-level hook guard let every attack through and the sandbox let none through.
- **Check properties of the result at commit and pull-request time, judged with the base commit's configuration.** This layer works in cloud sessions, where the sandbox can't be relied on, and against anything the first layer misses.

In-session hooks give fast feedback on top of those two. Policing the order of work inside a session with a phase state machine is deferred until the data shows a need. Decision 3 covers this.

## The lifecycle, stage by stage

### 1. Intent: the HLD

**Now.** LID's Phase 1 is native: an HLD with tenets, two or three sketched options for consequential choices, and decision docs [S: installed `SKILL.md:75-89,190-198`]. This repo adds the prior-art search skill, which runs after the goal is clear and before detailed design. All of it is skill prose plus the developer's review at the stop.

**Best found.** No candidate has a stronger intent layer. Every framework compared (Spec Kit, OpenSpec, BMAD, GSD, cc-sdd, Kiro's format, srs-dd, spec-engine) lacks a persistent design tree that owns the requirements [S for all but Kiro, which is D]. Two small ideas are worth lifting:

- [haft](https://github.com/m0n0x41d/haft) gives the evidence behind a decision an expiry date; expired evidence stops counting [S: `reff.go:24-231`]. No measurement shows it helps.
- [Ouroboros](https://github.com/Q00/ouroboros) scores requirement clarity per dimension with floors [S: `ambiguity.py:36-59,299-336`]. The score is a model's self-rating with uncalibrated thresholds, so it is not recommended.

**Verdict: keep LID.** Borrow one field: a "valid until" or refresh trigger on the evidence behind a decision doc. Prior-art notes here already carry a refresh trigger; decision docs would follow the same convention.

**Composes.** In: the developer's intent and the prior-art note. Out: the HLD and decision docs, which every later stage reads. State lives in `docs/`. All judgment; the only deterministic part is `lidc`'s format check.

**Gaps.** Nobody measures whether a better HLD predicts better outcomes. One paper scores 114 repos' spec artifacts and finds the top third spent fewer commits on bug fixes [P: EPIC, abstract only, correlational]. A practitioner report from a rollout to hundreds of engineers warns that a research-plan-implement flow "became a way to outsource thought" [X: HumanLayer, snippet]. LID's rule that judgment always reaches the user answers the same risk.

### 2. Design: the LLD

**Now.** LID's Phase 2, with an LLD-level edge-case probe [S: `SKILL.md:91-113`]. This repo's lessons add spikes before EARS, recorded as facts in the LLD [R].

**Best found.** BMAD's edge-case lens. It is a method, not a persona: enumerate every branch and boundary in the content, report only the paths that lack handling, then read the author's claims and try to falsify them [S: [BMAD-METHOD](https://github.com/bmad-code-org/BMAD-METHOD) `skills/bmad-review/references/lens-edge-case-hunter.md:1-72`; the code-review variant is `skills/bmad-build/review-prompts/edge-case-hunter.md:1-112`]. BMAD's changelog records blind validation that changed it: a named-set pass raised the catch rate on one real regression from 50% to 100% at 19% more tokens, and the "cynical reviewer" persona made no difference [s: `CHANGELOG.md:93,112-116,153,160`; the measurements themselves are not in the repo]. The developer uses this lens heavily for stress-testing plans before implementation and finds it more useful there than in code review [dev]. In BMAD it runs on documents as a single pass with no triage or loop [S: `skills/bmad-review/SKILL.md:8,33-38`].

Second: GSD's decision-coverage gate, deterministic code that fails when a recorded decision reaches no plan [S: [get-shit-done](https://github.com/gsd-build/get-shit-done) `sdk/src/query/check-decision-coverage.ts:1-97`]. The LID analog is "every row of an LLD's Decisions table is reflected in at least one EARS line".

**Verdict: borrow and reimplement the lens** (MIT) as the prompt for LID's LLD probe, run by a blind subagent. BMAD's planning chain would duplicate LID, so nothing else is taken.

**Composes.** In: the LLD draft and spike results. Out: a list of unhandled paths, triaged like any review finding (stage 9), each of which becomes an LLD edit, an EARS line, or a fork for the developer. Judgment throughout; the decision-coverage check would be code.

**Gaps.** No candidate checks that a design is feasible on the platform before specs are written. This repo's spikes do that by hand.

### 3. Requirements: EARS

**Now.** LID's Phase 3: one-line EARS specs with path-concatenated IDs beside each leaf LLD [s: `references/ears-syntax.md:14-16,42-58`]. `lidc` reads each spec with one regex per line and checks that IDs are unique and match the file's declared prefix. Two parsing quirks matter: a spec-shaped line whose ID has no digit aborts the whole run, and an ID with a lowercase letter is silently not a spec [S: [lid-tooling](https://github.com/EtaCassiopeia/lid-tooling) `crates/lid-core/src/parse/markdown.rs:31-58,184-287`]. EARS form itself is checked by review lenses, in prose. This repo's lesson: specs grow in review (8 became 38), so count after the coverage review and re-cut near 40 [R].

**Best found.**

- [spec-engine](https://github.com/spec-engine/spec-engine) parses EARS in code and lints for one promise per requirement (no second clause, no "because" or "so that") [S: `packages/shared/src/ears.ts:1-123`, `packages/engine/src/check/grammar.ts:16-88`]. It cannot read LID's multi-segment IDs or comma lists [s: `packages/shared/src/domain.ts:12`, `packages/engine/src/scanner/tags.ts:13`], so it is a model, not a dependency.
- [2119](https://github.com/Unsupervisedcom/2119) tags a requirement that no test can check as `[review]`, `[manual]` or `[verify: cmd]` [S: `README.md:101-125`]. This repo already has specs moved to manual runs because an eval can't exercise them [R].

- [letspecify](https://www.npmjs.com/package/letspecify) has the fullest rule set, all deterministic, with stable codes: one obligation per criterion, one of the five EARS forms, no term the project has declared imprecise, near-duplicates by shingle overlap, a near-duplicate pair that differs only in a negation or a number, a group of criteria with no "If ... then" guard, and a While-state that nothing exits [S: `lib/spec-properties.js:214-414`, `lib/spec-metrics.js:45-333`]. Its rule governance is worth copying too: a rule with a missing input reports "not evaluated", never a pass; rules can be raised but not lowered; disabling one needs a reason printed on every run; a baseline freezes old findings [S: `lib/spec-rules.js:12-186`]. Its thresholds come from a sweep on the author's corpus that is not in the package [D]. Its own spec format is weaker than LID's, so it is a design to borrow, not a tool to adopt.

Run against this repo's 438 spec lines, the candidate rules behave as follows [R: counted during the source read]. EARS form: every line has "shall" and all 40 "If" lines have "then", so the rule passes today and guards against regressions. Single obligation: 80 lines have more than one "shall" or "shall not", so that rule needs a baseline before it can gate.

**Verdict: propose to `lidc` and LID upstream.** `lidc`'s design admits the lint as one more check over text it already loads: roughly 150-250 lines without configuration, more with a term list, since `lidc` has no config file yet [S: `crates/lid-core/src/checks/mod.rs:1-62`]. The EARS-form and one-obligation rules replace two review lenses with code. The unguarded-group and While-exit rules are cheap hints for the edge audit. A verification-method tag makes "no test cites this spec" a declared state, not a coverage failure someone must explain.

**Composes.** In: the LLD. Out: spec files, the unit of everything downstream: tests cite IDs, review claims come from spec text, staleness hashes spec lines. Deterministic: ID format, and EARS form if upstream takes it. Judgment: coverage of the design, and whether a line admits two readings.

**Gaps.** Requirement-to-requirement dependency is absent from LID by design (the prefix tree stands in for it). Papers on LLM-written EARS exist but were read at abstract depth only [P].

### 4. Spec and plan review

**Now.** Review waves with lenses chosen per phase (coverage, contradiction, cold read, testability, two readings, fact-check), run as parallel subagents by convention, with results logged by hand [R]. LID allows a delegated inspector at each stop and forbids applying its findings silently [S: `SKILL.md:30-36`]. Nothing is code.

**Best found.** No single diamond. The useful parts:

- Compound Engineering's document review always runs coherence and feasibility lenses and adds others by condition [S: [compound-engineering-plugin](https://github.com/EveryInc/compound-engineering-plugin) `skills/ce-doc-review/SKILL.md:45-65`, `references/depth.md:3-33`].
- BMAD's intent-alignment lens enumerates the defensible readings of the stated intent, the same move as LID's divergence probe [S: `skills/bmad-build/customize.toml:93-186`].
- A gated spec-driven workflow gives the reviewer a closed, stage-specific defect list and tells it that "no defect found" is the expected answer. The reviewer found a blocking defect in the first review of 15 of 20 artifacts, and re-reviews the workflow had not asked for used 75% of reviewer tokens [P: arXiv 2611.05094, read in part; observational, authors' own projects].
- letspecify turns the closed defect list from an instruction into a check. Its engine calls no model. It validates the verdict a critic returns against a versioned catalogue of six defect types, limited to what rules can't decide. One unknown type, or a finding with no remedy or provenance, rejects the whole verdict as "not critiqued". A finding is kept only when a strict majority of passes report it, and a critic from the author's model family is rejected [S: `lib/verdict.js:73-299`, `lib/critique.js:49-233`].

**Verdict: build**, as the document mode of the review orchestrator in stage 9. Lenses are files. Each phase gets a closed defect list, and reviewers return structured findings that a small script validates against it (the letspecify gate), so a finding outside the list voids that reviewer's output instead of padding the wave. The stop rule comes from stage 10.

One change to the stop itself: **the developer reads the artifact first and sees the reviewers' findings after.** The stop summary should not lead with an agent's summary, and a clean wave is not grounds for a lighter read.

**Composes.** In: the artifact under review, plus the artifact one level up as the claims to check against. Out: findings in the review ledger (stage 9). Fixes that keep meaning are applied and listed; anything that chooses between readings goes to the developer as a numbered fork, as the project rules already say.

**Research behind that change.** In a crossover experiment, 34 students inspected requirements documents with and without a chat assistant. Detection was about 8% lower with the assistant, but the credible intervals overlap, so that effect is uncertain despite the paper's title. The firmer finding is that students who started with the assistant improved about half as much between periods. The authors advise using the model only after a manual pass [P: arXiv 2608.21298, read in full; novices, simplified documents, n = 34]. The study measures a person inspecting with an assistant. It is not evidence against an autonomous review wave that fixes the text before the developer sees it, and it matters less for an experienced reviewer.

**Gaps.** No candidate measures spec-review recall.

### 5. Edge audit

**Now.** LID's Phase 4: a compositional audit across specs, and a per-line divergence probe by blind readers who see only the spec text [S: `SKILL.md:135-149`]. In this repo's log the edge audit is where the developer's judgment is spent: 57 of 114 findings across five audit rows became forks, against 15% of findings overall [R].

**Best found.** LID is the diamond; no candidate has an equivalent stage. One paper uses the same principle with a solver: disagreement between independent formalizations of a requirement signals ambiguity [P: arXiv 2605.13817, abstract only].

**Verdict: keep unchanged.** LID suggests a reader from another provider where the platform allows. The evidence is thin: a second model finds partly different errors, but a top-tier second model's accuracy did not differ significantly from a fresh same-model session [P: arXiv 2610.01471, abstract only]. Cloud sessions would need a second login. Not now.

**Composes.** In: the LLD and specs together. Out: narrowing edits and new atomic spec lines, each fork resolved by the developer before tests are written. All judgment.

**Gaps.** No measure exists of how many implementation divergences the audit prevents. Stage 15 proposes one: count intent gaps that review or evals later find in code whose specs passed the audit.

### 6. Tests first

**Now.** LID's Phase 5 is prose: write tests citing EARS IDs, and "do not proceed to code until tests exist and fail in the expected way" [S: `SKILL.md:151-160`]. Nothing checks it.

**Best found.**

- [red-first-gate](https://github.com/ekinkilickaya95-byte/red-first-gate) runs the new tests against the previous revision's tree and requires them to fail there, instead of trusting a recorded red run [S: `red_first_gate.py:244-278`]. It parses results fail-closed: empty, duplicated or stale result files are errors [S: `:145-213`]. Its weakness is that the list of new tests comes from a file the agent could write; the list should come from the diff.
- [spec-flow-plugin](https://github.com/IgnacioMarin402/spec-flow-plugin) counts a run as red only when the runner reports a failing test, not a load error [S: `decisions/053`].
- [a2dlc](https://github.com/falsable/a2dlc) has the same "test teeth" gate, and a rule learned from its own refuted benchmark: a check that is out of scope must read inconclusive, never pass [s: `e2e/bench-swe-abs/RESULTS.md:1-30`].
- [Probity](https://github.com/nizos/probity) enforces order at edit time with a model judging each write, fail-closed [S: `src/rules/enforce-tdd.ts:10-158,251-322`]. Writes through Bash escape it unless extra rules forbid them [S: `:268-272`]. It needs Node 22.
- [qikly](https://github.com/gal-a/qikly) separates the test writer from the implementer by information, in code. The acceptance criteria are cut from the coder's prompt, and a leak check refuses to hand over a prompt in which any criterion text survives; a test proves the check can fail [S: `agent_interface.py:194-239,307-399`]. Decisions go in requirements that both agents see, and checkable consequences go in criteria that only the test author sees, so withholding can't leave the coder stuck [S: `design_3_mechanism.md:62-73`]. Its effect is unmeasured: its own findings file says the withheld-versus-sighted comparison has not been run, and the README's claim of 4 bugs across 50 libraries has no committed data [S: `FINDINGS.md:116-118`]. It is a standalone pipeline with its own task format and API keys, so the split is what to take.

**What the research says** (both papers now read in full).

- **Independence is the clearest effect.** Across five models and three benchmarks, tests generated with the implementation in the prompt detected 9-18% fewer faults than tests generated from the spec alone, and a fresh-context spec-only workflow beat a same-session code-then-tests workflow by 11.7% on average, significant for every model. The variable manipulated was whether the implementation was in the test writer's context, not when the tests were written [P: arXiv 2607.05139; function-level tasks, moderate].
- **Order alone is small.** A "write tests, then code" prompt gained 0.6 to 1.7 points at function level and 1.5 to 2.9 at repository level, with no significance tests and no arm that swaps the order [P: arXiv 2608.16742, peer-reviewed].
- **Iteration on execution feedback carries most of the gain** in that study, and most remaining failures were code that passed its own tests and failed the repository's: tests that drifted toward the implementation.
- agentops's claim that ordering "did not survive" rests on a practitioner's blog post that was not read here; its design and sample size are unknown [X: secondhand].

**Verdict: borrow and reimplement two things, and enforce neither as an ordering rule.**

1. **A baseline-red check** (red-first-gate is MIT, about 300 lines of stdlib Python) at commit time and in CI: each test the diff adds that cites an EARS ID fails on the base tree and passes on the candidate. The list of new tests comes from the diff, never from a file the agent writes.
2. **Independence by context:** in LID's Phase 5, a test-writing subagent gets the EARS lines and the interface and never the implementation; the coding subagent gets the failing tests. A prompt builder enforces what each sees, as qikly's does. After code exists, an edit to a test is flagged for review as possible drift toward the implementation.

Failing-tests-first stays LID's default in prose, since the tests stop gives it at almost no cost and it is the cheapest way to get independence. Decision 2 covers this.

**Candidate design: a testable design first, then tests and code in parallel.** Agents, unlike people, can be given exactly the prior knowledge a job needs. So independence doesn't have to come from order: it can come from what each agent is told, and the test writer and the implementer can then work at the same time.

1. **A testable-design agent runs first, in sequence.** For each EARS ID in the slice it records:
   - the entry point and its signature;
   - the observable outcome a test checks;
   - the seams where test doubles go;
   - the fixtures the tests need.

   A deterministic check requires a row for every EARS ID in the slice. This is the test-facing half of an interface contract. LID's LLD template covers external API contracts (`references/lld-templates.md:114`), but not how each requirement is observed or where the seams are. The step is developer-reported practice [dev]: a separate "produce a testable design" agent before TDD has given good results, and some such sequential step was needed for good results even with plain TDD. It is also where interface problems are cheapest to fix, before any test or code exists.
2. **A test agent and an implementation agent then run in parallel.** Both see the EARS lines and the testable design, and neither sees the other's output. The prompt builder enforces what each sees, as qikly's leak check does. A permission deny on test paths for the implementer makes "the implementer doesn't edit tests" mechanical, with stage 8's source-only re-run as the backstop.
3. **Integration runs the baseline-red check and then the tests against the code.** Each failure is triaged as a test bug, a code bug or a spec gap. A spec gap walks back up the arrow, like BMAD's intent-gap routing. If tests must change after integration, a fresh test agent re-derives them from the spec, rather than the original agent editing them with the failing code in view. That keeps the independence that tests revised in context lose.

What could make it slower instead of faster:
- **Interface drift** between the two agents, which the testable design is there to prevent.
- **Reconciliation cost** on every mismatch. The secondhand Finster report puts a standing coder and tester split at up to three times the cost [X].
- **Narrow evidence.** The independence effect is measured only at function level [P: 2607.05139].

So it should be trialed before it becomes the rule (Decision 2, "What to measure"). The testable-design step is general enough to propose upstream to LID, as an LLD section or a step between the edge audit and failing-tests-first.

**Composes.** In: the diff, the base commit and the test runner's report. Out: pass, fail or inconclusive per added test. Fully deterministic. State is git objects only, so there is nothing for the agent to edit. It needs a runner that reports per-test results (pytest's JUnit XML). Stage 8's source-only re-run is the companion check: this one proves the tests were red, that one proves the green came from source changes.

**Gaps.** No study isolates order with independence held fixed in an agentic, repository-level setting. One secondhand report says splitting coder and tester into two long-lived agents cost up to three times more with no consistent gain [X: via agentops], so the split should be a fresh subagent for the tests, not a second standing agent, and its cost should be measured (stage 15). Once agents commit, order can also be read from history: the commit adding the tests comes before the one that makes them pass.

### 7. The implementation loop

**Now.** The main session or a delegated subagent implements against the spec, with LID's delegation rules in the dispatch prompt [S: `SKILL.md:60-64`]. Lint, type and test checks run through `mise run check`, in commit-time hooks and CI. Path-scoped authoring rules are planned.

**Best found.**

- [superpowers](https://github.com/obra/superpowers) has the best-designed task loop. Findings go back to the same implementer for up to three rounds, then to a fresh one. Every re-review is scoped to the findings and the fix diff, and anything outside that scope goes to a ledger instead of widening the loop [S: `skills/subagent-driven-development/references/fix-loop.md:20-77`, `re-review-prompt.md:1-116`]. Small scripts do the hand-off plumbing (one task extracted to a brief, a range-guarded diff package). All gates are prose: its only hook is SessionStart [S: `hooks/hooks.json:1-18`].
- spec-flow-plugin's Stop gate runs lint and the whole test suite outside the model, fails closed if it crashes, and hands off to a human after an attempt cap [S: `internal/hooks/gate.go:149-478`]. It supports Node projects only, and lets a dirty working tree stop unjudged [S: `gate.go:262-302`]. [foreman](https://github.com/michalzan/foreman) has the same "stop must be earned" idea [S: `hooks/stop_gate.py:233-366`].
- Claude Code's path-scoped rules load a rule file when a matching file is read or edited [D].
- [Habit Hooks](https://github.com/habit-hooks/habit-hooks) turns a strict linter's output into something the agent can act on without gaming the metric. A deterministic pipeline maps each violation to a named code smell and a coaching guide that states the gaming anti-pattern and a done condition. It exits 1 for enforced smells and 2 when the run was incomplete, never a false pass [S: `src/habit_hooks/mapper.py:23-91`]. A content-hash ratchet keeps findings already in the backlog accepted until their file changes [S: `src/habit_hooks/snooze_lapse.py:25-51`]. It is Python, uv and ruff, which matches this stack, and never touches git. It cites an independent pre-registered study in which a bare linter message produced genuine fixes in 6-29% of trials and coaching in 83% [D: `README.md:29-51`; the study's repo was not read]. Its integration ships only as instruction-file prose, so it would be wired as a mise task and a Stop hook.
- ast-grep lets a repeated review finding become a structural lint rule [D: Thoughtworks Radar].
- [stop-that-shit](https://github.com/lennney/stop-that-shit) checks a task's declared authority before each tool call: review and answer modes deny writes, writes outside the declared files are denied, and a subagent budget is enforced [S: `src/decision.cjs:53-231`]. It is weaker than its README: re-reviewing unchanged code is not guarded, the hook fails open, and its own pilots show no improvement over baseline [S]. The idea of keeping review subagents read-only is the part worth keeping, and the sandbox and permission rules can do that natively (stage 13).

**Verdict.** Adopt native path-scoped rules. Borrow superpowers' scoped re-review for fix loops. Trial Habit Hooks on this repo's own strict profile, since the HLD already names "relax a check rather than fix the code" as a failure and this is the only tool found aimed at it. Borrow the earned stop as a small Stop hook that runs the fast checks, advisory only (stage 13). Trial a Showboat demo per slice as the artifact for the ease-of-human-review lens (below).

**Composes.** In: approved specs and failing tests. Out: a diff with `@spec` annotations. Deterministic: lint, types, tests, `lidc`. Judgment: the code. State: the working tree.

**Gaps.** Maintainability under repeated agent edits is unsolved. Agents extending their own code over staged checkpoints produced code that eroded structurally in 77% of trajectories, and quality prompts did not slow it [P: SlopCodeBench, search summary only]. Tests cannot reward maintainability [X]. A review lens for ease of human review is this repo's only counter. Two additions for that lens:

- [Showboat](https://github.com/simonw/showboat) is adoptable as is (Apache-2.0, one binary through uvx, no git operations). An agent builds a demo document only through `exec`, which records each command's real output, and `verify` re-runs every block and fails on any byte difference [S: `exec/runner.go:13-33`, `cmd/verify.go:27-73`]. One demo per slice gives the developer something to read that CI can re-check. A hand edit to the document is caught only when `verify` runs and the output is deterministic. No measurement of its effect exists.
- [brooks-lint](https://github.com/hyhmrright/brooks-lint) offers a finding format (symptom, source principle, consequence, remedy) and a "what not to flag" list per decay risk [S: `skills/_shared/common.md:6-58`]. Its own evals are not favorable yet: single-run pilots range from +0.71 to -0.57, with severity overcalls [S: `evals/PILOT-LOG.md`]. Take the format and the guard lists into one maintainability lens; leave severity to triage.

Also unmeasured here: orchestration cost. One experience report found a multi-stage orchestrated lifecycle cost 4-8 times more on large tasks and gave no measurable gain on small or medium ones [P: SSRN 7675938, read in full; one developer, one to three runs per cell]. For rule files, one large study found that every individually helpful rule was a negative constraint and every harmful one a positive directive [P: arXiv 2604.11088, read in part, one model and benchmark]. Write rules as "don't", each traced to a real failure [X: Hashimoto, Osmani].

### 8. Verification of tests against requirements

**Now.** `lidc coverage` warns for each implemented spec that no test file cites; this repo fails on warnings. It checks presence only: nothing checks that the test ran, passed, or would fail if the behavior broke [S: lid-tooling `crates/lid-core/src/checks/coverage.rs:1-71`]. Two defects in how `lidc` classifies a citation weaken even that [S: `crates/lid-core/src/parse/source.rs:114-169`, `repo.rs:91,109-114`]:

- The kind (test or code) comes from the absolute path, so a checkout under any directory named `test` or `tests` makes every code citation count as a test, and coverage passes vacuously.
- Citations in `.sh` and `.yaml` files are neither code nor test, so this repo's citations in its session-start hook and its eval case files are invisible to both `coverage` and `reverse-orphan`.

This repo's review waves cover discrimination with a "grader discrimination" lens [R].

**Best found.**

- **Runner-proven coverage.** A requirement counts as verified only if a test citing it was reported as executed and passed [S: spec-engine `packages/engine/src/check/proven.ts:1-120`; spec-flow-plugin `decisions/001`]. [Shallnot](https://github.com/RachidChabane/shallnot), musthold's companion, binds tests to requirements only from JUnit results [S: `docs/binding.md:1-41`], but it needs a revision suffix on every reference and can't parse LID's deferred-spec lines, so it is a model, not a dependency [S: `internal/adapters/spec/markdown.go:13-37,194-223`].
- **Source-only re-run.** [promptwheel](https://github.com/promptwheel-ai/promptwheel) reverts every edit to tests, config, graders and golden files, re-runs the gate on the base plus the source changes alone, and calls the result gamed if less than half the gain survives [S: `bin/promptwheel.mjs:487-544`]. Thresholds, protected paths and setup are read from the base commit, so loosening the gate in the same change cannot pass [S: `bin/promptwheel.mjs:630-660,781-799`]. It uses no model, never writes to the repo, and ships a committed red-team bench with a map of what it cannot see [S: `bench/REDTEAM.md`; synthetic, small]. One caveat: a commit trailer can override the gate unless `allowTrailer` is set to false, and an agent can write trailers [S]. It needs Node 18 or later.
- **Check-weakening detection.** [agent-roast](https://github.com/Nari-Ab/agent-roast) has diff-aware rules for loosened assertions, skipped or deleted tests, lowered coverage thresholds and CI steps allowed to fail, with its policy read from the base commit [S: `src/tampering.ts`, `src/review.ts:69-70,154-183`]. It reports recall on 71 labelled cases and noise over about 13,000 real commits [s: `docs/benchmarks.md`]. Its Stop hook is weak (fails open, sees only uncommitted work); the pull-request check against the base is the layer that holds.
- **Discriminating power.** [musthold](https://github.com/RachidChabane/musthold) asks whether a requirement's tests fail on code that violates it, using mutants that must build and pass every other requirement's tests [S: `README.md:50-77`]. It has the deepest design record in the set (17 decision records, pre-registered studies). Its own results are not yet favorable: the first study was inconclusive (0 of 18 escapes in either arm), with 4 of 18 false rejections and 1.82 times the cost per accepted change [S: `experiments/loop-1/results/REPORT.md`].
- **Verification-gap lens.** BMAD asks, per behavior, whether any test would fail if it broke; prompt-only false gaps fell from 2 of 2 to 0 of 2 across 16 runs [S: `skills/bmad-build/review-prompts/verification-gap.md:1-101`; numbers s, from the changelog].
- **Tamper detection as a studied problem.** [tamperward](https://github.com/hamsasoftware/tamperward) separates steering (fail-closed hooks in the loop) from adjudication (after the session, re-run against pristine tests restored from the base, with policy pinned to the base, then protected CI) [S: `README.md:91-104`, `docs/architecture.md:44-70`]. It runs pre-registered paired experiments and publishes failed predictions. Its latest and largest round did not replicate the prevention effect (p = 0.73 over 79 valid pairs), though no weakening survived to the final tree in the gated arm and there were no strict bypasses across 201 measured trajectories [S: `harness/taskbench/round4/ROUND4-ANALYSIS.md:42-145`; aggregates only]. Its threat model for the pristine re-run (case folding, file modes, replaced git objects, child processes) is the checklist any such check should copy [S: `SPEC.md:358`]. It is Node, Linux-only for its run envelope, and JavaScript-first.
- **Tests that cannot fail.** [falsegreen](https://github.com/vinicq/falsegreen) is a static scanner for Python tests that protect nothing: constant asserts, swallowed assertion errors, uncollected tests, misspelled mock asserts. Its precision is locked in CI by one legitimate look-alike per blocking rule [S: `scanner.py`, `tests/test_precision_corpus.py`]. It is MIT, pure Python with no dependencies. Its precision and recall figures are assertion only.
- Mutation testing itself is rated Adopt in the Thoughtworks Radar [X].

**Verdict.**

- **Borrow and reimplement promptwheel's source-only re-run** as a CI and commit-time check in Python, beside stage 6's baseline-red check, using tamperward's threat model as the test list. Reimplementing avoids a Node dependency and the trailer override; adopting promptwheel in CI is the fallback if the reimplementation proves fiddly.
- **Adopt falsegreen as a check on newly written tests** at the tests stop, wired fail-closed through this repo's own task and not through its fail-open pre-commit hook, after a trial for false alarms.
- **Propose runner-proven coverage to `lidc`** (stage 11), and file the two classification defects.
- Take the verification-gap lens into the review wave.
- **Do not adopt musthold.** By its own evidence the mechanism costs more than it has been shown to buy, and using it under LID is not a format conversion: musthold calls the Shallnot binary itself and relies on Shallnot's gate to enforce its proofs, so the minimal route is real Shallnot fed generated specs and test tags, losing revisions, non-pytest tests and accurate locations [S: musthold `discpower/internal/adapters/shallnot/gateway.go:1-102`].

**Composes.** In: spec files, the runner's JUnit report, the diff against base. Out: per-spec status (cited, ran, passed) and a list of weakened checks. All deterministic except the lens.

**Gaps.** A cheap, reliable way to prove that tests discriminate, per requirement, does not exist yet. Agent-written tests also show more unrecognized assertion patterns and more flakiness than human ones [P: arXiv 2607.12068, snippet].

### 9. Review waves and triage

**Now.** Per slice, parallel reviewers split by lens, then triage (deduplicate, verify, drop what isn't worth its cost), with fixes going back through the spec. All by convention; counts are logged by hand. Across 36 logged waves: 817 findings, 707 applied, 119 forks, 3 that failed verification [R].

**Best found.** Three candidates each do one part better than anything else.

*Dispatch:* [craftsman](https://github.com/BuczynskiRafal/craftsman) computes the review plan in code from the frozen diff. Each hunk owes lenses by its kind and risk signals, coverage is credited by hunk digest, and a re-round reviews only changed or referencing hunks [S: `craftsman/huntplan.py:186-241`]. Elsewhere the wave's size and lenses are the model's choice. It ships a seeded-defect eval (27 defects, 18 decoys) with recall 89-96% and precision 71-86% per version [S: `docs/benchmark.md:46-79`; small, synthetic]. It never commits, needs only Python 3.10 or later, and keeps state in `.git/craftsman` [S]. It reviews code diffs only.

*Mechanics and validation:* Compound Engineering dedupes by fingerprint in a script, requires each finding to quote the line, and refuses to count agreement between same-model reviewers as corroboration. One independent validator must cite refuting evidence to reject a finding in eight protected subjects; otherwise the finding stays unresolved [S: `skills/ce-code-review/scripts/findings-mechanics.py:67-131,222-229`, `references/validator-batch-template.md:24-54`].

*Triage routing:* BMAD verifies every finding at its cited line before any grouping, logs every finding, groups only by shared root cause, and routes each to intent gap, bad plan, patch or defer. The first two send the work back up through the plan [S: `skills/bmad-build/step-04-review.md:51-103`, `skills/bmad-code-review/step-03-triage.md:1-98`]. Those routes map directly onto walking back up LID's arrow.

Also: [judicata](https://github.com/philippmelikidis/judicata)'s fingerprint by category and structural address (function, or Markdown heading), which survives line shifts [s: `scripts/judicata_core/findings.py:1-30,64-69`]; [Alibaba's open-code-review](https://github.com/alibaba/open-code-review), whose filter may only delete a finding and must cite a refuting line [S: `agent.go:1565-1615,1800-1925`]; and Claude Code's Workflow tool for running parallel agents from a script [D].

**Research.** A design where rules decide which files and criteria each reviewer gets, with a filter-only falsifier, more than doubled a review-quality score against plain Claude Code on the same model [P: arXiv 2608.09290, read in part, one benchmark]. Two independent reviewers with findings pooled did not beat one beyond noise, while one reviewer plus a critic who audits the review did [P: arXiv 2608.18167, read in part]. In the field, 56% of an agentic reviewer's comments were rejected [P: arXiv 2607.03316, abstract only], and models often judge correct code non-compliant [P: arXiv 2603.00539, abstract only]. Review is also expensive: in one fully read experience report it was 40-50% of a run's cost [P: SSRN 7675938; one developer]. Together these say the verification step earns more than extra reviewers. Review depth can also follow risk: Meta's funnel routes diffs by a risk score and reports a revert rate one third that of other diffs across 331,000 landed [P: arXiv 2605.30208, abstract only], and "risk-tiered human oversight" is at Trial in the Thoughtworks Radar [X]. One practitioner model puts a person's review capacity at about 1,200 lines a day, or roughly two agents' output [X: Kinney], which is why the ease-of-human-review lens and small slices matter as much as recall.

**Verdict: build the orchestrator, small, on borrowed designs.** It needs four parts:

1. Lenses as files (edge case, verification gap, intent alignment, cold read, ease of human review), each a method with a closed defect list.
2. A dispatch plan computed in code from artifact kind and change size.
3. Triage in BMAD's order with Compound Engineering's mechanics: verify at the cited line, fingerprint, one refuting validator, route to an arrow level.
4. A review ledger in code (below).

Whether to trial craftsman as-is for code diffs is Decision 4.

**Composes.** In: a frozen diff or document, plus the claims to check it against (EARS lines for code; the LLD for specs). Out: a review ledger, one JSON Lines record per finding: fingerprint, lens, verdict with evidence, disposition, a "caused by a fix" flag, and the content hash of what was reviewed. The ledger replaces hand counts: `docs/review-log.md` becomes generated from it. It is also what stage 10 computes the stop from, what stage 12 checks before a merge, and what stage 15 scores. Deterministic: dispatch, fingerprints, dedupe, routing table, ledger. Judgment: finding, refuting, severity. The ledger has two parts with different writers: raw reviewer output and the hash of what was reviewed, captured by a hook into the protected directory (stage 13), and the triage rulings, which are the orchestrating agent's judgment and stay agent-written.

**Gaps.** Nobody learns across waves except [rigour](https://github.com/rigour-labs/rigour), which keeps a per-check score from fixed-versus-dismissed outcomes and mutes a noisy advisory check [S: `check-outcomes.ts:1-113`; the mechanism's effect is unmeasured]. The same few lines could score each lens from the ledger. Disposition by cost and value is still judgment everywhere.

### 10. Convergence and stopping

**Now.** Judgment, guided by the lesson that yield fell from 40 to 12 to 5 to 5 across one slice's waves and that two narrow re-checks were the useful stopping point [R]. The HLD says "review waves until convergence".

**Best found.**

- craftsman encodes a rule in code: a further wave is planned only when a verified bug finding of sufficient severity was found, generations are capped at three, and the loop stops at the first wave that adds nothing [S: `craftsman/huntplan.py:590-603,772-896`].
- BMAD's rule is similar but in prose: a follow-up pass only if a high-severity finding was patched; "patch volume is never grounds". It removed a zero-findings halt because that pressured reviewers to invent findings [S: `skills/bmad-build/step-04-review.md:84`; removal s, from the changelog].
- [review-convergence](https://github.com/marcmeezy/review-convergence) keys "clean" to a hash of the reviewed source, so any edit resets the count [S: `convergence.py:277-295`].
- [deep-review-loop](https://github.com/1273984347/deep-review-loop) stops and goes to the user when more than 30% of new findings were caused by fixes [S: `SKILL.md:305-330`; prose only, threshold unmeasured].

**Research and practice.** Letting a reviewer review again cut F1 from 0.376 to 0.303, because later rounds invent findings once real errors run out; three independent parallel reviews did better [P: arXiv 2603.16244, read in part]. Wider review reached similar accuracy to more rounds at lower cost, and a second round helped some models and hurt others [P: arXiv 2610.34577, read in part]. A hook-driven loop with no round cap ran 87 rounds in one case [P: arXiv 2610.08900, read in part]. In another report, review loops did not converge on their own, and a round cap bounded them without ending the churn [P: SSRN 7675938, read in full; one developer]. A cap is therefore necessary and not sufficient: what a later pass may look at has to narrow too. A vendor report on its own code review: a three-round cap, diff-only re-review and no repeated findings raised first-round passes from 65% to 78%, and about 59% of what the reviewer kept flagging predated its first pass; five-or-more-round reviews fell from 8.9% to 1.5% and mean reviews to pass from 2.08 to 1.32. The same report fixes every instance of a bug class at once, tags findings as important, nit or pre-existing, and has verifiers vote before a finding is posted [X: Anthropic, "Solving code review", self-report on internal pull requests]. This is the most direct evidence found for a capped, diff-scoped rule. [no-mistakes](https://github.com/kunchenguid/no-mistakes) takes the stance furthest: its pipeline runs forward once, each step iterates only on its own findings within a budget, and re-running completed steps on a changed tree is refused as having "no honest end" [D: `VISION.md:37-45`; the tool itself fails the cloud-session criterion].

**Verdict: borrow and reimplement** as a function over the ledger:

- One wide wave per phase.
- A further pass only when a verified high-severity finding was fixed, or when the fix rewrote a large share of the artifact. It is scoped to the fix diff and what references it.
- A hard cap of three passes.
- Never "zero findings" as the exit condition.
- A converged result is void when the content hash changes.
- A finding on text the change did not touch is tagged pre-existing and does not trigger a pass; a finding already ruled on is not raised again.

**Composes.** In: the ledger. Out: continue, stop, or escalate to the developer with the reason. Pure code. The orchestrator obeys it; the pull-request gate in stage 12 re-checks it.

**Gaps.** Every threshold in the candidates is unmeasured. This repo's ledger would be the first data: the regression flag gives the fix-caused rate directly.

### 11. Traceability and staleness

**Now.** `@spec` annotations in tests and code; `lidc` checks them, blocking in hooks and CI. LID's own cascade rules are prose [s: `SKILL.md:200-218`]. The arrow overlay is empty here (`docs/arrows/index.yaml` has `arrows: {}`).

What `lidc` does, from its source [S: lid-tooling at `1f5627d`, `crates/lid-core/src/checks/mod.rs:40-62`]:

- It registers thirteen checks. This repo runs three (`reverse-orphan`, `coverage`, `spec-id-format`). The other ten cover the index schema, arrow-doc structure and references, orphaned design files, cited specs that are still marked open or deferred, LLD decision tables, dependency cycles, implementing-artifact paths, decision-doc structure and prefix coherence. Several depend on the arrow overlay, which is empty here.
- **It checks no staleness of any kind.** The index's `audited_sha` is parsed and never read, and its staleness category is never emitted [S: `crates/lid-core/src/model/arrow.rs:60-108`, `checks/mod.rs:195-207`].
- A check is a pure function over the loaded working tree, with no git dependency. Anything that needs test results or a base ref needs a new input [S: `checks/mod.rs:1-62`].
- It is small, clean and well tested (384 tests). Its last commit is from June 2026, five months before this read.

Nothing, then, marks a spec's evidence stale when its text or its code changes.

**Why it matters.** The largest empirical study of spec-driven practice found no tool that checks specs and code still agree after implementation, and practitioners' agent-run consistency checks were unreliable [P: arXiv 2608.25202, read in part, moderate]. A pre-registered study found that only in-code citations of requirement IDs enabled automated detection of hallucinated code (86-88%) [P: arXiv 2606.30689, read in part]. LID's `@spec` already does that; staleness is the open part.

**Best found.** Three implementations of one idea: bind evidence to content hashes.

- [Habeas Codicem](https://github.com/nikomatsakis/habeas-codicem) stores, per requirement, the exact requirement text and the exact source lines the evidence relies on. A change to either fails validation with a diff until an agent reassesses, and refreshing an input resets the determination [S: `src/evidence.rs:363-420,643-692`; `src/add_input.rs:322-330`]. It is tied to mdBook and Cargo. Its author is someone the developer can talk to directly [dev].
- 2119 hashes the requirement text plus the covering test blocks and the file prelude. An edit to the requirement, its tests or shared mocks voids the verdict; unrelated tests in the same file don't [S: `src/hash.ts:12-28`, `src/annotations.ts:61-131`]. Verdict files are committed as an audit trail.
- musthold tracks staleness per proof by digests of the code footprint, the bound tests and the spec statement [S: `docs/adr/0008:20-79`].

Supporting checks: srs-dd's two-way link pairing and its report of files that no requirement claims [S: [srs-dd](https://github.com/CRELLIA-S-L/srs-dd) `srs-dd/tools/srs_check.py:1114-1179`]; spec-engine's loss guard, which fails when a change removes the last implementing or verifying tag of a live requirement [S: `packages/engine/src/guard/losses.ts:1-154`]; [specspan](https://github.com/nripankadas07/specspan)'s query from changed files to affected requirements [S: `src/specspan/analyzer.py:617-654`]. [tracey](https://github.com/bearcove/tracey)'s version suffix on IDs conflicts with LID's rule that revisions change text, not IDs [S].

**Verdict: propose upstream first** (Decision 5). All six proposals fit `lidc`'s design; drafts with designs in its own terms are in [the lid-tooling feedback page](../tool-feedback/lid-tooling.md) [S: sizes are estimates from the source read].

| # | Proposal | Size | Notes |
|---|---|---|---|
| 0 | Fix the two citation-kind defects (stage 8), and the abort on a digit-less ID | Small | Bugs; file first |
| 1 | EARS-quality lint (stage 3) | Small; medium with a term list | Needs a config surface `lidc` lacks |
| 2 | Impact query: changed files to specs to segments | Small to medium | Caller supplies the file list, so no git. Helper files with no citation map to nothing |
| 3 | Runner-proven coverage from JUnit XML | Medium | File-level binding lets an unrelated passing test in the same file prove a spec. Needs a new input path; eval suites write no JUnit |
| 4 | Per-spec staleness: hash each spec's text with its citing test blocks, record a verdict, flag a mismatch | Medium | No git needed. IDs stay fixed, which fits LID. Open: how to stop an agent re-stamping without reassessing |
| 5 | Unclaimed-code report and two-way pairing | Small to medium | Must be informational: LID annotates entry points only |
| 6 | Link-loss guard | Small, then medium | Partly exists already: an implemented spec that loses its last test citation fails `coverage` here. What remains is evasion by flipping a spec to open or deleting it with its citations, which needs a base ref. It can only warn, because LID allows deleting specs |

Habeas Codicem's line-cited evidence is the strongest model for proposal 4 and is worth a conversation with its author before a design is fixed. It and 2119 share the open problem of re-stamping; the answer here is to make the stamp file a protected path (stage 13), so only the developer's commit or a reviewed step can write it.

Independently of upstream, this repo should review the ten checks it doesn't run and turn on those that pass or need small fixes, and fill in the arrow overlay enough for the impact query to have segments to report.

**Composes.** In: spec files, annotations, the runner's report, git history. Out: per-spec states (cited, proven, stale), which block at commit and in CI as `lidc` does today. Deterministic. State: committed verdict or evidence files beside the specs, keyed by hash, so a stale one is detectable from content alone.

**Gaps.** Semantic agreement between an LLD and its specs remains judgment everywhere. No candidate detects that code drifted from a spec whose text didn't change, short of re-running a reviewer.

### 12. Commit, pull request and merge autonomy

**Now.** The agent drafts `commit-message.md`; the developer commits one slice at a time. No commit lint yet. Renovate's dependency updates merge automatically once CI passes (HLD tenet 5); that is tooling, not agent work, and stays.

**Best found.**

- **A tighten-only ratchet.** [dev-process-toolkit](https://github.com/nesquikm/dev-process-toolkit) has a merge policy of offer, auto or never. The default is offer, auto comes only from a line the operator wrote in config, and anything said in conversation can only tighten it [s: `adapters/_shared/src/merge_policy_ratchet.ts:1-35`, `skills/deliver/SKILL.md:247-263`].
- **Approval sealed to content.** [DAW](https://github.com/DiluxOne/dilux-agentic-workflow) lets the agent commit only after the user has seen that exact message. The hook compares digests, and the approval is spent by the act [S: `daw/scripts/hook-gate.py:520-572`]. A developer-made commit also satisfies its closeout gate [S: `validate-transition.py:2066-2084`].
- **A guard that knows the spellings.** foreman's command guard recognizes merges and protected pushes through shells, heredocs, substitutions and `gh api`, and fails closed [S: `hooks/guard.py:792-830`, `tests/test_guard_parsing.py`]. DAW's own gate misses `gh api` and merge-then-push [S]. [sawbuck](https://github.com/sawbuck-ai/sawbuck) has a similar hold that turns `gh pr merge`, publishing and force pushes into a question to the developer; a plain push passes [S: `hold.mjs`]. All of these match command text, which stage 13 shows is a speed bump, not a wall.
- **Approval only from the user's own prompt.** One lifecycle plugin records an approval only from a user-sourced prompt event, never from anything the agent emits [P: SSRN 7675938, read in full; no artifact released]. In Claude Code that is a UserPromptSubmit hook writing to a path the agent cannot write.
- **A review witness on the final tree.** [disensor](https://github.com/NicolasRocchia/disensor)'s CI gate reads only git objects between merge base and head, and passes only if a recorded review saw the final tree per path [S: `src/disensor/gate.py:639-711`]. It is the cleanest mechanical answer found to "converged, then changed". Its review record lists what the review could not close, in six terminal states, instead of a pass badge [S: `rules.py:208-300,380-396`].
- **Commit form.** [lintje](https://github.com/lintje/lintje) requires a blank line and a meaningful body out of the box and rejects Conventional Commits, which fits this repo's format, but it has no first-party pre-commit hook [S]. [git-sumi](https://github.com/welpo/git-sumi) has a hook and a header regex but cannot require a body [S: `src/lint.rs:183-188`].

**Verdict: borrow and reimplement, one rung at a time.**

| Rung | Who acts | What must hold first |
|---|---|---|
| 0 (now) | Developer commits; agent drafts the message | Commit-message lint on the developer's commit |
| 1 | Agent commits on a work branch | Message sealed to what the developer saw, with the seal recorded from the developer's own prompt; test-evidence checks green (stages 6, 8) |
| 2 | Agent opens pull requests, including stacked ones | Review witness covers the final tree; stop rule satisfied; CI judged with base config |
| Never | Agent work merges to the default branch | Forge branch protection. A merge guard hook in session is a courtesy prompt on top |

The rung is a value only the developer writes, read from the base commit, and tightened but never loosened in conversation. Branch protection on the forge is the control that carries the "never" row, because it is entirely outside the agent's reach and works the same in local and cloud sessions. The session's network allowlist is a second barrier where the sandbox is on, though a broad entry such as the forge's own domain leaves the API reachable [D].

**Composes.** In: the review ledger, check results, the drafted message. Out: a commit or pull request, and a gate verdict. Deterministic throughout. State: the forge's settings, git objects, a committed policy file, and seal records in a protected path (stage 13).

**Gaps.** No candidate handles stacked pull requests with per-slice review records. The Thoughtworks Radar lists stacked pull requests and "human-in-the-loop theater" under Caution [X: listing]: an approval step the person cannot realistically perform is worse than none. Rung 2 should therefore be sized to review capacity, with one slice per pull request, before stacking is tried. Whether lintje can be pinned through mise was not verified offline.

### 13. Enforcement and its calibration

**Now.** One SessionStart hook. `lidc` blocks in commit-time hooks and CI. Everything else is prose. LID ships no hooks at all [S: listing at `727ed80`]; its `docs/setup.md:59` says the plugins "automate phase gates", which overstates it.

**The native layer: sandbox and permission rules.** No candidate verified in source relies on it, and it changes what the rest has to do.

*What the one experiment found.* For a proprietary Claude Code lifecycle plugin, a text-level hook guard alone let all 8 attacks that ran get through, and every obfuscation class tried got past the text filter. Claude Code's OS sandbox profile held against all 11, with or without the guard. A crashing hook failed open [P: SSRN 7675938, read in full; macOS only, one to three runs per cell, no artifact, unreviewed]. The developer adds first-hand experience that a centrally managed sandbox configuration, locked so repos can't loosen it, has held up in sustained real use on macOS and Windows [dev: not measured; the docs say native Windows runs commands unsandboxed and WSL2 is the supported path]. Neither source covers Linux, where this work is done.

*What the docs say it covers* [D: Claude Code sandboxing docs, fetched 2026-11-10; nothing tested here]:

| Property | Detail | Consequence |
|---|---|---|
| Scope | Shell commands and their child processes; subagents inherit it. Not the Read, Edit and Write tools (permission rules govern those), not command hooks, not local MCP servers, not commands the user types, not excluded commands | Protecting a path takes two rules: a sandbox write-deny for the shell and a permission deny for the file tools. Hooks run outside the sandbox, so a hook can write what the agent can't |
| Writes | Allowed only in the working directory, a temp directory and added directories. Always denied, even there: `.claude/settings*`, `.claude/hooks`, `.claude/skills`, `.claude/agents`, `.claude/commands`, `.mcp.json`, `.git/hooks`, `.git/config`, shell startup files | Hook definitions and settings are protected already. A `denyWrite` entry for another project path (a gate-state directory) should work, but its precedence over the working-directory grant is not stated and must be tested |
| Reads | Open everywhere by default, including credential directories, unless denied | Add read denies for credentials |
| Network | Through a proxy with an allowlist, empty by default; no TLS inspection | A broad entry such as the forge's domain is still a way out |
| Platforms | Built in on macOS. Linux and WSL2 need bubblewrap and socat installed. Off by default. If it can't start, the session silently runs unsandboxed unless `failIfUnavailable` is set | On Linux it is a setup step, and silent fallback must be turned off |
| Escapes | The model can ask to run one command unsandboxed; `allowUnsandboxedCommands: false` removes that. Excluded commands match on text and run fully unsandboxed | Remove the escape; exclude nothing |
| Who can loosen it | A repo's settings can turn it on, and some keys can't be set from repo files at all. Keys set in managed settings make a repo's attempt to loosen them ignored | The non-negotiable keys belong outside the repo (Decision 9) |
| Cloud sessions | Not documented for this sandbox; they run in a managed VM with its own network allowlist | Cloud sessions can't rely on it. Checks of the result are the backstop there |

The docs call it "not a complete isolation boundary".

*What follows for this design.*

- **Protected state has one kind of writer: hooks.** A review record captured by a SubagentStop hook, an approval recorded by a UserPromptSubmit hook, or a fire-rate log written by a Stop hook can sit in a directory the agent can neither write through the shell (sandbox) nor through the file tools (permission deny). craftsman already attributes reviewer output through SubagentStop hooks and denies writes to its ledger [s: `.claude-plugin/plugin.json:24-83`].
- **Much hook-level machinery becomes unnecessary where the sandbox is on:** fingerprinting hook-held state against tampering, deriving state from the transcript because no file is safe, and parsing command text for every spelling of a write. Those remain speed bumps and useful messages, not defenses.
- **Three things are still needed.** Checks of the result at commit and pull-request time, because the sandbox protects files and judges nothing, and because cloud sessions and other harnesses don't have it. Permission rules for the file tools. And a fixture suite that attacks the configuration, since none of this has been seen to hold on Linux.
- **Paths that change with the phase can't be protected statically.** "Tests are frozen once code starts" is not a sandbox rule. Stage 8's source-only re-run covers it from the result.
- **One side effect to check:** `.claude/skills` is always write-denied to the shell, so an agent that runs this repo's skills-install task through the shell would be refused. The SessionStart hook, which runs outside the sandbox, would not.

**Other pieces, as rules more than tools.**

- **Judge with the base commit's configuration.** a2dlc's check reads config and the test command from the base, so a change cannot narrow its own scope [S: `internal/app/app.go:217-275`]. agent-roast, rigour and layered-code-review independently do the same [S: `src/review.ts:69-70`; `trusted-state.ts:1-40`; s for layered-code-review]. a2dlc's intentional behavior changes need a human SSH signature the agent never holds [S: `app.go:121-152`]. Its hook layer is weaker than its check layer: it reads protected paths from an agent-editable file [S: `app.go:1183-1184`].
- **Every guard ships fixtures.** [cairn](https://github.com/mesutgulecen/cairn) asserts must-reject and must-accept cases for each guard, on exit code and reason, in CI. Its checks carry the history of the vacuous pass that shaped them, such as `grep -q` under `pipefail` [S: `scripts/verify.sh:17-214`, `components/hooks/plan-gate.sh:166-215`]. DAW and dev-process-toolkit go further and mutate each guard to prove it can go red [S: DAW `scripts/mutate.py:1-25`; s for dev-process-toolkit].
- **A hook-held state machine, if one is wanted.** DAW validates transitions against a declared graph in a pre-write hook and protects the method, receipts and journal from the agent [S: `daw/scripts/validate-transition.py:1288-1318,1404-1574`]. It has the deepest rationale of the enforcement set (20 costed decisions). Shell writes are detected, not prevented.
- **State with no file to edit.** Probity keeps no state; its rules read the session transcript, and `requireCommand` blocks a command unless a required earlier command appears with no invalidating write after it [S: `src/rules/require-command.ts:58-77`]. With protected paths available, this trick and Probity's rules against shell writes matter less, and Claude Code's own `onFailure: "block"` makes a PreToolUse command hook fail closed [D]. What Probity alone still offers is a model judging each edit for test-first order, which Decision 2 does not want.
- **Audit before enforce.** [claimcheck](https://github.com/Allan-Nava/claimcheck) logs every decision with a denominator, and a new rule must earn blocking through a measured fire rate [S: `claimcheck.mjs:386-401,564-581`].

**What the failures look like.** Verified in source across the set: gates that fail open on any error, state files the agent can write ([tdd-guard](https://github.com/nizos/tdd-guard)'s off switch sits on its own ignore list, `src/guard/GuardManager.ts:17-38`), hooks that match only some tools, receipts that prove a step ran but not that it passed, and gates that release after three blocks. On the platform side, Claude Code hooks fail open on error by default, exit code 1 does not block, and a Stop hook's blocks are capped [D]. The setting that makes a hook fail closed is reportedly ignored on Stop and SubagentStop hooks [X: secondary source citing the docs], so a Stop-hook gate cannot be made fail-closed by configuration and must not be the only place a property is checked.

**Verdict.** Adopt two house rules now: base-commit judging, and fixtures for every guard. Any exception inside a guard denies. Place enforcement in four layers, strongest first:

1. **Forge and CI:** branch protection and required checks judged with base config. Holds whatever the agent does, locally and in cloud sessions.
2. **Sandbox and permission rules (local sessions):** adopt, after a test on Linux. A protected directory for gate state, written only by hooks; the escape removed; silent fallback off; credential reads denied. Hard keys in user or managed settings (Decision 9).
3. **Git hooks through prek:** commit-message lint, `lidc`, fast checks, on the developer's commits.
4. **In-session hooks:** an earned stop, a merge prompt, state capture. Feedback and record-keeping, at advisory strength. A Stop hook can't be made fail-closed and is never the only check.

Defer the phase state machine, and drop Probity from the plan (Decision 3). The reason for deferring has changed. With hooks as the only writers of protected state, a state machine could hold locally without the self-protection code that makes DAW's large. What is missing is evidence that policing order pays: the one cost measurement found no gain on small and medium tasks at 4-8 times the cost on large ones [P: SSRN 7675938], the test-order effect is small (stage 6), and in cloud sessions every transition would need a result check behind it anyway.

**Composes.** Every gate is a function of artifacts: git objects, runner reports, and records in the protected directory. Agent-written files (triage rulings, draft messages) are inputs to a gate only together with a content hash or a hook-captured record. The first slice (build order) is the configuration plus the fixtures that try to break it.

**Gaps.** No evidence on Linux or in cloud sessions; the precedence of a write-deny inside the working directory is undocumented; local MCP servers run outside the sandbox. Tool-layer hooks miss actions that bypass the tool layer [P: arXiv 2606.25189, abstract only], which is the case the sandbox closes for the shell and leaves open for everything else.

### 14. Learning capture

**Now.** The session wrap-up skill proposes a home for each lesson and writes nothing without approval. `docs/process-lessons.md`, the review log and `docs/tool-feedback/` hold the results. The memory-versus-intent rule sends project intent into the arrow.

**Best found.** Compound Engineering's form ladder: capture a lesson in the cheapest durable form, in order. First a check, proven to fail on the defect's shape in a throwaway copy. Then a coding-standard condition. Then a written learning, only if it passes a counterfactual bar ("would this have changed what was done?"). A script validates the paths, commits and links a learning cites [S: `skills/ce-compound/references/form.md:9-23`, `SKILL.md:33`; validator s].

**Counter-evidence on automation.** agentops built an automatic extract-and-inject memory pipeline and withdrew it: retrieval precision reached 0.13 and 23% of lessons extracted on unattended runs were hallucinated, while short hand-checked notes kept working [S: [agentops](https://github.com/boshu2/agentops) `docs/practice-ledger.md:161-200`; its own measurement]. rigour reports that 0 of 317 extracted lessons verified [s]. This repo's rule of approval before writing matches what survived, and matches the "feedback flywheel" the Thoughtworks Radar moved to Trial: ask at the end of a session whether a shared artifact should change, let agents propose and people choose, and prune as well as add [X]. sawbuck adds one specific memory: it keeps reverted and undone attempts with their reasons and shows them when a prompt names the file [S: `undo.mjs`, `README.md:115-119`]. The effect its README claims for this can't be checked: no harness or data is committed in either of its repos [S: listing].

**Verdict: borrow the ladder into session-wrap-up** as its routing rule: check first (with a must-reject fixture), then a path-scoped rule written as a negative constraint, then a lesson. Keep the approval step. Record the reason with any reverted or rejected approach, where the next session will read it.

**Composes.** In: the session, the ledger, eval results. Out: a new check, rule or lesson, each of which changes an earlier stage. The loop closes here: a review finding that recurs becomes a lint rule and leaves the review wave.

**Gaps.** Nobody shows that captured lessons improve later work. Stage 15's per-lens and per-rule measurements are the nearest substitute.

### 15. Evaluating the process itself

**Now.** `claude plugin eval` suites for the skills, run by the developer; the interactive eval harness; the review log. The lessons already include pre-naming a last round, and re-running a surprise before diagnosing it [R].

**Best found.**

- **Pre-registration with a noise bar.** agentops writes its decision rules before the runs, derives a noise bar from A/A runs (0.15; the 90th-percentile gap between identical arms was 0.13), reports intervals, and keeps a fix only if a rerun meets the preset bar [s: `docs/evals/2026-10-22-plugin-eval-opus-5-5.md:1-120`]. musthold freezes protocols with timestamps and a decision table before any data, and reports inconclusive results as such [S: `experiments/README.md:1-30`, `docs/adr/0017:35-95`]. tamperward runs paired experiments with numeric predictions, sealed results and a deviation ledger, and published the round in which its own effect failed to replicate [S: `harness/taskbench/round4/ROUND4-ANALYSIS.md`]. The counter-example is sawbuck, whose headline numbers have no committed harness or data: a measurement that can't be re-run is treated here as a claim.
- **Reviewer evals from real history.** [layered-code-review](https://github.com/legendtkl/layered-code-review) mines the repo's reverts and fix-forward commits that name a SHA, adds settled clean commits, has a human confirm each case, and scores recall and the clean false-alarm rate [S: `skills/review-eval/scripts/mine_reverts.py:1-116`, `score.py:1-104`]. It also classifies each finding by how the author answered it (fixed, wrong, intentional, not important) [S: `score.py:277-305`]. No results are published. craftsman's seeded-defect suite is the synthetic counterpart, with results.
- **The practice ledger.** agentops labels each engineering practice as held, changed shape, did not survive or still testing, with the evidence class of every row [S: `docs/practice-ledger.md:1-245`]. It is the model for how this repo should record what its own data says about each stage.
- **Skill wording by eval.** superpowers tests a skill against a no-guidance baseline at five or more repetitions and reports its null results [S: `skills/writing-skills/SKILL.md:248-305`; the evals are in another repo].

**Verdict: adopt the methods** (they are practices, not code). The section *What to measure* turns them into a plan.

**Gaps.** Nothing found measures end-to-end outcomes (defects escaped, time to a correct change) for a whole process with a control. The one benchmark comparing spec frameworks on 50 tickets is vendor-run, single-run, with a noise band of about 10 points [X: Uvik]. Agent scores vary between identical runs [P: arXiv 2602.07150, title only], which is why the noise bar comes first.

## Cross-cutting design principles

| # | Principle | Evidence | Strength |
|---|---|---|---|
| 1 | **General prose doctrine does not enforce; a mechanism does. One specific, negative rule can work.** | agentops pilot: doctrine removed 0 of 12 false completions, a deterministic gate 6 of 12 [s]. [steerloop](https://github.com/lukavtz/steerloop)'s 90-cell A/B: most prose rules had no effect over control, but one mandatory disclosure field moved behavior from 0 of 10 to 10 of 10 [S]. A text-level guard let every attack through [P: SSRN 7675938]. Every helpful rule in a large study was a negative constraint [P: 2604.11088]. Coaching text attached to a lint finding raised genuine fixes from 6-29% to 83% [D: cited by Habit Hooks, study not read]. This repo: an output rule held only once moved into the template [R]. LID's gates are all prose [S] | Moderate. Narrower than "prose never works": one tested case of a single specific rule working (steerloop), and specific guidance at the point of failure appears to help. Broad process doctrine does not. sawbuck's claim that one instruction-file line stopped test editing is not counted: its data is not committed |
| 2 | **A gate's state must be outside the agent's write reach. Put that protection at the OS layer where it exists, and derive from artifacts where it doesn't.** | Failures in source: tdd-guard, [preflight](https://github.com/solozerolabs/preflight) (stamp files), [IIKit](https://github.com/intent-integrity-chain/kit) (re-lock), a2dlc (verdict file). Working designs without a sandbox: [ringi-gate](https://github.com/kxmskx/ringi-gate) fingerprints (`agent-review-loop-lib.mjs:2855-2950`), disensor (git objects only), Probity (transcript). Sandbox held 11 of 11 where a text guard held 0 of 8 [P: SSRN 7675938]; sustained real use under a managed configuration [dev]. Theory: a worker's own claim must never decide completion [P: 2609.27871] | Strong that the failure exists. Weak-to-moderate that the sandbox is the fix: one small macOS experiment, one first-hand report, docs; nothing on Linux or cloud |
| 3 | **Judge a change with the base commit's configuration.** | a2dlc, agent-roast, rigour, promptwheel and tamperward, independently [S]; layered-code-review [s] | Six implementations; unmeasured |
| 4 | **Every guard ships must-reject and must-accept fixtures.** | cairn, DAW's mutation harness, dev-process-toolkit's mutation matrix, foreman's canary [S, S, s, S]. A gate that passes when its subject is absent lets a worker finish by deleting the artifact [P: 2609.27871] | Strong as engineering practice |
| 5 | **Know which way each hook fails.** | Claude Code hooks fail open by default and exit 1 does not block [D]. spec-engine's documented hook example would not stop the agent [S: `guard.ts:55-56`] | Docs plus one verified case |
| 6 | **Review wide, not deep: fresh parallel readers, then at most a scoped re-check.** | Papers 2603.16244, 2610.34577, 2603.12123 [P, read in part]; Anthropic's self-report [X]; this repo's yield data [R] | Moderate. Counterpoint: two reviewers did not beat one beyond noise [P: 2608.18167], so width alone is not the gain |
| 7 | **Verify a finding by trying to refute it before acting on it.** | Alibaba's filter, Compound Engineering's validator, BMAD's triage [S]. One reviewer plus a critic beat more reviewers [P: 2608.18167]. 79-83% of candidates killed before disclosure in a field campaign [P: 2604.19049, abstract]. 56% of field review comments rejected [P: 2607.03316, abstract] | Moderate |
| 8 | **Evidence goes stale: bind every approval, proof and review to content hashes.** | Habeas Codicem, 2119, musthold, disensor, preflight (`run.sh:327-345`), review-convergence [S] | Six implementations; unmeasured |
| 9 | **Code for mechanics, agents for judgment, few hand-offs.** | Rule-driven dispatch beat agent discretion [P: 2608.09290]. craftsman computes its plan [S]. agentops withdrew its swarm and control plane [S]. One-run comparisons: a many-agent framework used about six times the tokens for no better output [X]. Orchestration cost 4-8 times more on large tasks with no gain on small or medium ones [P: SSRN 7675938, one developer] | Moderate for review; weak overall |
| 10 | **Start a gate advisory, measure its fire rate, then promote it; retire gates that cry wolf.** | claimcheck [S]; rigour's per-check score [S]; agentops dropped checks that policed the repository's shape and not its behavior [S]; practitioner guidance [X] | Practice, lightly measured |
| 11 | **Pre-register process changes and report nulls. A number with no committed harness is a claim.** | agentops, musthold, a2dlc, superpowers, rigour, tamperward and brooks-lint all publish negative or inconclusive results [S or s]. sawbuck's and qikly's headline numbers have no committed data [S] | Strong as method |
| 12 | **Text matching on commands is a speed bump, not a wall.** | Every obfuscation class tried got past a text filter [P: SSRN 7675938]. Guards verified in source miss spellings (DAW, NTCoding's plugin) or need large parsers to keep up (foreman) [S]. The sandbox applies to child processes whatever the command text [D] | Moderate: one experiment plus several verified misses |

## Tensions and open questions for the developer

Each row states both sides and a recommendation. The developer decides each one.

| # | Question | Evidence against the current process | Evidence for it | Recommendation |
|---|---|---|---|---|
| 1 | **Review until a wave "yields nothing worth implementing", or a coded stop?** | agentops: "Mandatory review never converged here. A reviewer asked to find problems finds one every time, and each repair started another round" (`docs/practice-ledger.md:168`). More rounds added noise [P: 2603.16244]. 75% of reviewer tokens went to unrequested re-reviews [P: 2611.05094]. Here, six waves still left 8 skill-text misses for evals to find [R]. Anthropic's own review loop improved after a three-round cap and diff-only re-review [X]. In one experience report review loops never converged unaided, a cap bounded them without ending the churn, and review was 40-50% of run cost [P: SSRN 7675938] | This repo's reviews look unlike agentops's: 3 of 817 findings failed verification and 87% were applied. First waves produced 603 findings across 24 waves; later passes 214 across 12, of which 142 came from three re-checks after substantial rewrites, so re-checks after big changes do find things [R]. "Applied" is not "valuable", though, and nothing records whether a later finding was caused by a fix | One wide wave per phase. A further pass only after a verified high-severity fix or a large rewrite, scoped to the change, capped at three, computed from the ledger (stage 10). Record the fix-caused flag so the rule can be tuned from data. Reword the HLD's "review waves until convergence" to match. At each stop the developer reads the artifact before the findings (stage 4) |
| 2 | **Test-first as an ordering rule, or as a property of the result?** | agentops: ordering "not supported for agents in the one experiment that isolates them" (`docs/practice-ledger.md:163,221`). That experiment is a blog post, known here only secondhand; its design and sample size are unread. Measured order effects are small: 0.6 to 2.9 points, no significance tests [P: 2608.16742, read in full]. An informal test found no clear gain from a TDD loop at 3-8 times the tokens [X, cited by agentops] | The clear effect is independence: tests written without the implementation in context detected 11-13% more faults across five models [P: 2607.05139, read in full, moderate]. Writing tests first is the cheapest way to get that, and LID's tests stop gives it at almost no cost | Three parts. Keep the order as LID's default, in prose, and build no edit-time enforcement of it. Enforce the properties mechanically: added tests fail on the base tree, the green survives a source-only re-run, citing tests ran and passed. Get independence by context: a test-writing subagent that sees the specs and never the implementation, with later test edits flagged. Measure the split's cost before making it the rule. Trial the stronger variant in stage 6: a testable-design agent first, then test and implementation agents in parallel, reconciled at integration. If it holds up, propose the testable-design step to LID |
| 3 | **A phase state machine in session, or protected state plus checks of the result?** | The HLD plans "a small state machine", and its problem statement is that agents skip steps. DAW shows one can be built well [S]. With the sandbox and permission rules protecting hook-written state, the old objection that the agent can rewrite the state no longer applies locally. A check of the result can't see a skipped step that leaves no trace | Policing order has no evidence of paying: no gain on small and medium tasks at 4-8 times the cost on large ones [P: SSRN 7675938]; small test-order effects (Decision 2); agentops withdrew its in-repo control plane. The sandbox is untested on Linux and absent in cloud sessions, where every transition would need a result check behind it anyway. A state machine is the largest custom piece in the earlier plan | First the sandbox baseline with attack fixtures, then the checks of the result (stages 6, 8, 10, 12). In-session hooks record state and give feedback, at advisory strength. Drop Probity from the plan. Revisit a state machine when the ledger shows skipped steps that the result checks missed; it would then be a thin layer over protected state. This changes a planned HLD component, so it needs the developer's ruling |
| 4 | **Trial craftsman for code review, or build the orchestrator's code mode?** | craftsman does the dispatch, coverage proof, coded stop and a seeded eval already (MIT, Python only, never commits). Building repeats that work | It reviews code diffs only, and most review volume here is specs, skill text and notes. Its plugin hooks don't install in cloud sessions, and its Stop gate would sit beside any others. Its precision (71-86%) still needs a cost-and-value triage | Build the ledger, stop rule and document mode here, since nothing covers them. Before building a code mode, run craftsman and a plain lens wave on the same seeded and escape cases (stage 15) and adopt it for code diffs if it wins |
| 5 | **Traceability upgrades: upstream to `lidc`, with LID's author, or a local checker?** | lid-tooling's last commit is five months old, its manifest names a different repository URL, and two of the proposals (test results, a base ref) need an input path its design doesn't have yet [S]. Tenet 1 weighs active maintenance. A local check is quick | The codebase is small, clean and well tested, with a one-line check registry, and all six proposals fit it [S]. Forking a spec tool splits the ecosystem LID depends on. Habeas Codicem's author is reachable and has built the closest design | File the three bugs and the small proposals first (record them in `docs/tool-feedback/` first, per project rules); the response is the test of whether upstream is alive. Talk to Habeas Codicem's author before fixing a staleness design. If upstream stays quiet for an agreed period, ask LID's author where `lidc` should live before forking, and until then keep any local check a separate script that reads `lidc`'s JSON output, not a patched binary |
| 6 | **Walk the full arrow for every change, including small fixes?** | Practitioners use spec-driven development selectively and skip it for bugs and small tasks [P: 2608.25202]. In one vendor benchmark, specs paid off on features and multi-file tickets and not on bug fixes or refactors [X: Uvik, single run] | Those findings are about per-change spec files, not a living spec tree: with LID, a bug fix edits one or two existing lines. LID is explicit that bugs take no short-circuit | Keep the rule. Measure overhead per change size from the ledger and revisit if small changes cost disproportionately |
| 7 | **Add a reviewer from another model family?** | agentops: a cross-model verdict on every commit "caught real defects and cost more than the work it checked" (`docs/practice-ledger.md:217`). Cloud sessions get a degraded mode | A second model finds partly different errors; one fresh same-model plus one cross-model review found more planted errors than two same-model reviews [P: 2610.01471, abstract only]. A second-vendor reviewer caught a defect two same-vendor reviewers passed [P: SSRN 7675938, a single case]. letspecify rejects a critic from the author's model family by rule [S] | Not as a standing step. Worth one pre-registered trial where a miss is most costly: the edge audit's divergence probe, and the refuting validator in triage, measured against the noise bar |
| 8 | **When does the agent start committing?** | Nearly every framework has the agent commit, and several good mechanisms (red commit before green commit, the review witness) need commits to exist | The index is currently the developer's review record, and close review is how trust is being built | Stay at rung 0 until the stage 6 and 8 checks and the ledger exist and have run on several slices. Then move to rung 1 with sealed messages |
| 9 | **Where do the sandbox's hard settings live?** | Repo settings travel with every clone and reach the template's consumers; a solo developer has no admin to manage a policy file | Repo files can't hold some keys, and a change under review could loosen the rest. Keys in managed settings make a repo's loosening ignored [D]. A managed, locked configuration is what the developer has seen hold in sustained use [dev]. Cloud sessions use neither | Split it. The repo (and the template) carries the sandbox switch, the protected gate-state path, the permission denies and a SessionStart check that reports when the sandbox is not active. The non-negotiable keys (no unsandboxed escape, fail if unavailable, the write-deny on gate state) go in managed settings on the developer's machines, or user settings if managed is impractical. Document the managed file for teams adopting the pattern |

## Build order

Each slice is useful by itself and feeds the next. All are small Python or shell, with fixtures (principle 4).

| # | Slice | Delivers | Needs | Lives |
|---|---|---|---|---|
| 1 | **Sandbox baseline and attack fixtures** | A tested answer to "can the agent write gate state on Linux?": sandbox on, a protected directory, permission denies for the file tools, the escape removed, fail-if-unavailable, credential reads denied. Fixtures that try each bypass (encoded commands, interpreters, heredocs, symlinks, the file tools, the unsandboxed request) and must all be refused. A probe of what a cloud session does | Decision 9. bubblewrap and socat in the setup task. The undocumented write-deny precedence is the first thing to test. A day or two, mostly configuration | Repo and template settings; managed or user settings |
| 2 | **Review ledger and coded stop rule** | Per-finding records, a generated review log, per-lens yield, the stop decision as code | Slice 1 for the hook-captured part; the rest needs nothing. Borrows from review-convergence, layered-code-review, disensor, deep-review-loop | This repo |
| 3 | **Reviewer eval corpus and noise bar** | A labelled set built from this repo's own escapes (what evals found after review) plus seeded defects; an A/A noise bar; a pre-registration template | Slice 2's records. Methods from agentops, layered-code-review, craftsman, tamperward | This repo |
| 4 | **`lidc` housekeeping** | The three bugs filed; the unused checks reviewed and turned on where they pass; the small proposals (EARS lint, impact query) sent | Decision 5. Drafts are in [the lid-tooling feedback page](../tool-feedback/lid-tooling.md) | Upstream; this repo's `lid` task |
| 5 | **Commit-message lint and skill; path-scoped rules; lint coaching** | Already planned. A `commit-msg` hook through prek; rule files written as negative constraints; a Habit Hooks trial on the strict profile | lintje or git-sumi (a quick trial decides); native rules | This repo and the template |
| 6 | **Review orchestrator, first version** | Lenses as files, coded dispatch, a validated verdict format with closed defect types, triage with one refuting validator, routing to arrow levels; document mode first | Slices 2-3. Designs from BMAD, Compound Engineering and letspecify | This repo's skills package |
| 7 | **Test-evidence checks** | Added tests fail on base; the green survives a source-only re-run with base config; a static scan for tests that can't fail; a test-writing subagent that never sees the implementation | Borrows red-first-gate, promptwheel, tamperward's threat model, falsegreen, qikly's split | CI workflow and Phase 5 dispatch here |
| 8 | **Earned-stop hook, advisory** | Fast checks at Stop, logged with a fire rate | Slice 7's checks. Ideas from spec-flow-plugin, foreman, claimcheck | Process hooks, this repo |
| 9 | **Runner-proven coverage and per-spec staleness** | A spec is proven only by a test that ran and passed, and its evidence goes stale when its text or its cited tests change | Upstream design with `lidc` and Habeas Codicem; a script over `lidc`'s JSON output if upstream is quiet. Stamp files in the protected directory | Upstream first |
| 10 | **Autonomy rungs 1 and 2** | Commit messages sealed from the developer's own prompt, the ratchet file, a pull-request gate that the review saw the final tree, branch protection | Slices 1, 2, 7. Designs from DAW, dev-process-toolkit, disensor | Process hooks and CI |
| 11 | **Phase state machine** | Only if the data from slices 2-8 shows skipped steps that the result checks miss | Decision 3 | Deferred |

Slice 1 comes first because it is cheap and its answer decides how much machinery every later slice needs: if protected paths hold on Linux, the ledger, the seals and the stamps are plain files written by hooks; if they don't, each needs a fingerprint and a result check behind it. Slices 2 and 3 follow because they use data the repo already has and every later slice is judged against them. Slices 4 and 5 are independent and can run alongside.

**Propose upstream, don't fork:**

| To | Proposal |
|---|---|
| `lidc` (lid-tooling) | Three bugs: citation kind taken from the absolute path, script and YAML citations invisible, a digit-less ID aborting the run. Then, smallest first: an EARS-quality lint, an impact query, runner-proven coverage from JUnit XML, per-spec staleness by content hash, an unclaimed-code report with two-way pairing, a base-ref link-loss warning |
| LID | A verification-method tag for specs no test can check; a five-way classification of implementation discoveries by the level they re-enter, with an append-only record of proposals and rulings ([spec-kit-reconcile](https://github.com/SuhaibAslam/spec-kit-reconcile) `commands/speckit.intent.decisions.md:40-112` [S]); the wording of `docs/setup.md:59` |
| Habeas Codicem | A conversation, not a patch: whether its evidence model can be host-neutral, and how it would sit under EARS IDs |
| craftsman | Only if adopted: a document mode, and claims supplied from spec IDs |

## What to measure

The process is improving if escapes fall and the developer's attention per slice falls, without cost rising faster than either.

| Measure | Source | Why |
|---|---|---|
| **Escapes per slice:** defects found after a review pass by evals, a later pass, the developer, or a post-commit fix | Ledger, eval runs, fix commits | The main outcome. Each escape becomes an eval case for the reviewer (slice 3) |
| **Per-lens yield and cost:** applied findings and tokens per lens; disposition as fixed, wrong, intentional or not important | Ledger | Retire or rewrite low-yield lenses; score lenses the way rigour scores checks |
| **Fix-caused rate:** share of a pass's findings caused by the previous pass's fixes | Ledger flag | Tunes the stop rule; the candidates' thresholds are guesses |
| **Share of review tokens after the first pass, and passes to stop** | Ledger | Direct check on the stopping rule against the 75% figure in 2611.05094 |
| **Forks per slice and where they arise** | Ledger | Forks at the edge audit are the process working; forks found in code review are intent gaps that escaped |
| **Gate fire rate and false-block rate, per guard** | Hook logs | Decides promotion from advisory to blocking |
| **Attack fixtures refused, per platform** (local Linux, cloud session) | Slice 1's fixture suite, re-run on every Claude Code update | The only evidence that the protected paths hold where this work is done |
| **Cost of the test-writer split:** tokens and escapes with and without a separate test-writing subagent | Pre-registered trial | Decision 2; one secondhand report puts a coder and tester split at up to three times the cost |
| **Testable design plus parallel tests and code:** a three-arm trial on real slices (tests in the same context; a sequential split; testable design then parallel agents). Measure faults caught (mutation kills or musthold), review findings that escaped, mismatches at integration, wall-clock time and tokens | Pre-registered trial | Decision 2; stage 6's candidate design |
| **Named exceptions and suppressed checks over time** | Existing HLD metric, plus the weakening detector | Catches relaxing a check instead of fixing the code |
| **Overhead by change size:** tokens and elapsed time from approved EARS to commit | Ledger and git | Answers Decision 6 |

How to run a process change:

1. **Pre-register.** Before the runs, write the question, the cases, the metric, the number of repetitions, and the keep-or-drop rule. Commit that file first.
2. **Measure noise.** Run the same arm twice (A/A) and take the gap as the noise bar. A difference inside it is not a result.
3. **Use real cases where they exist.** Escapes and reverts from this repo's history, confirmed by a person, scored for recall. Settled clean changes, scored for false alarms. Seeded defects fill the gap while history is thin.
4. **Repeat.** At least three to five runs per cell; a single surprising failure is re-run before it is diagnosed, as the lessons already say.
5. **Report nulls**, and record the outcome per practice in a ledger of held, changed shape, did not survive, still testing.

What cannot be measured yet: long-run maintainability of agent-written code, and whether any of this transfers to another model. Both should be named as open in the HLD, not assumed.

## Appendix A: sources read in source

Commit is the clone's HEAD at the time of reading. License is from the license file.

| Candidate | License | Commit | Used for |
|---|---|---|---|
| [jszmajda/lid](https://github.com/jszmajda/lid) | MIT | 727ed80 (1.4.4; installed here is 1.4.0) | Spine |
| [bmad-code-org/BMAD-METHOD](https://github.com/bmad-code-org/BMAD-METHOD) | MIT (trademark notice on names) | a867e16 | Lenses, triage routing |
| [EveryInc/compound-engineering-plugin](https://github.com/EveryInc/compound-engineering-plugin) | MIT | dd9b792 | Finding mechanics, validator, form ladder |
| [BuczynskiRafal/craftsman](https://github.com/BuczynskiRafal/craftsman) | MIT | 938da91 | Coded dispatch, wave trigger and cap |
| [obra/superpowers](https://github.com/obra/superpowers) | MIT | 22f0b46 | Scoped fix loop, skill evals |
| [boshu2/agentops](https://github.com/boshu2/agentops) | Apache-2.0 | 80313b2 | Practice ledger, eval method |
| [legendtkl/layered-code-review](https://github.com/legendtkl/layered-code-review) | MIT | ef1f114 | Revert-mined reviewer evals |
| [NicolasRocchia/disensor](https://github.com/NicolasRocchia/disensor) | MIT | 1190b97 | Review record, witness gate |
| [falsable/a2dlc](https://github.com/falsable/a2dlc) | Apache-2.0 | 03baa28 | Base-commit judging, signed waivers |
| [mesutgulecen/cairn](https://github.com/mesutgulecen/cairn) | MIT | bf3f4b7 | Guard fixtures |
| [RachidChabane/musthold](https://github.com/RachidChabane/musthold) | Apache-2.0 | 6d45cdd | Discriminating power, pre-registration |
| [nikomatsakis/habeas-codicem](https://github.com/nikomatsakis/habeas-codicem) | MIT OR Apache-2.0 | 2e8083f | Line-cited, stale-able evidence |
| [Unsupervisedcom/2119](https://github.com/Unsupervisedcom/2119) | MIT | 652891f | Hash-bound verdicts |
| [DiluxOne/dilux-agentic-workflow](https://github.com/DiluxOne/dilux-agentic-workflow) | Apache-2.0 | 7b1461f | Transition graph, sealed approval |
| [nesquikm/dev-process-toolkit](https://github.com/nesquikm/dev-process-toolkit) | MIT | e9d6c65 | Merge-policy ratchet |
| [michalzan/foreman](https://github.com/michalzan/foreman) | MIT | 13c771b | Command guard, earned stop |
| [IgnacioMarin402/spec-flow-plugin](https://github.com/IgnacioMarin402/spec-flow-plugin) | MIT | 7b9c40a | Stop gate, runner-proven proof |
| [ekinkilickaya95-byte/red-first-gate](https://github.com/ekinkilickaya95-byte/red-first-gate) | MIT | 339e06b | Baseline-red check |
| [Nari-Ab/agent-roast](https://github.com/Nari-Ab/agent-roast) | MIT | 9c87c3a | Check-weakening detector |
| [nizos/probity](https://github.com/nizos/probity) | MIT | eeac421 | Transcript-based gates |
| [spec-engine/spec-engine](https://github.com/spec-engine/spec-engine) | MIT | 1f844fd | EARS parser, loss guard, proven coverage |
| [CRELLIA-S-L/srs-dd](https://github.com/CRELLIA-S-L/srs-dd) | MIT | 29e38cb | Two-way link checks |
| [marcmeezy/review-convergence](https://github.com/marcmeezy/review-convergence) | MIT | 5d6e0e9 | Hash-keyed stop rule |
| [philippmelikidis/judicata](https://github.com/philippmelikidis/judicata) | MIT | c7b3983 | Structural fingerprints |
| [kxmskx/ringi-gate](https://github.com/kxmskx/ringi-gate) | Apache-2.0 | 4bb60d3 | Tamper fingerprints |
| [EtaCassiopeia/lid-tooling](https://github.com/EtaCassiopeia/lid-tooling) (`lidc`) | MIT OR Apache-2.0 | 1f5627d | What `lidc` checks; the six proposals |
| [RachidChabane/shallnot](https://github.com/RachidChabane/shallnot) | Apache-2.0 | 1434e8a | Runner-proven binding; why a musthold shim is costly |
| [promptwheel-ai/promptwheel](https://github.com/promptwheel-ai/promptwheel) | Apache-2.0 | 3558f77 | Source-only re-run; gate judged at base |
| [letspecify](https://www.npmjs.com/package/letspecify) | MIT | npm package 0.34.0 | EARS lint; verdict gate |
| [habit-hooks/habit-hooks](https://github.com/habit-hooks/habit-hooks) | MIT | 54e2569 | Lint findings as fix guidance |
| [simonw/showboat](https://github.com/simonw/showboat) | Apache-2.0 | d531261 | Re-runnable demo documents |
| [gal-a/qikly](https://github.com/gal-a/qikly) | Apache-2.0 | f1b72fd | Withholding the criteria from the coder |
| [hamsasoftware/tamperward](https://github.com/hamsasoftware/tamperward) | Apache-2.0 | 1832f5b | Threat model for the pristine re-run; study design |
| [vinicq/falsegreen](https://github.com/vinicq/falsegreen) | MIT | 1e4229a | Static scan for tests that can't fail |

Others cited once (deep-review-loop, rigour, haft, Ouroboros, specspan, tracey, spec-kit-reconcile, steerloop, claimcheck, preflight, IIKit, GSD, lintje, git-sumi, Alibaba's open-code-review, tdd-guard) were read the same way; their licenses and commits are in the verification records.

## Appendix B: papers relied on

All are preprints unless noted. "Part" means named sections were read; "abstract" means only that.

| Paper | Read | Used for |
|---|---|---|
| [More Rounds, More Noise](https://arxiv.org/abs/2603.16244) | Part | Stopping; parallel over sequential |
| [Rethinking Verification in Agent Harnesses](https://arxiv.org/abs/2610.34577) | Part | Width over depth; gates versus reminders |
| [Adversarial Review](https://arxiv.org/abs/2608.18167) | Part | A critic beats more reviewers |
| [OpenCodeReview](https://arxiv.org/abs/2608.09290) | Part | Rule-driven dispatch; filter-only falsifier |
| [Cross-Context Review](https://arxiv.org/abs/2603.12123) | Part | Fresh-session reviewers |
| [A Gated Spec-Driven Workflow](https://arxiv.org/abs/2611.05094) | Part | Closed defect lists; cost of re-review |
| [Humanize](https://arxiv.org/abs/2610.08900) | Part | Uncapped review tails |
| [Bounded Loops](https://arxiv.org/abs/2609.27871) | Part | Vacuous gates; self-attestation |
| [Spec-Driven Development as Prescribed and as Practiced](https://arxiv.org/abs/2608.25202) | Part | Spec-code agreement is the open gap |
| [Citation Discipline in Spec-Driven Development](https://arxiv.org/abs/2606.30689) | Part | In-code requirement citations |
| [On the risk of coding before testing](https://arxiv.org/abs/2607.05139) | Full | Test independence |
| [TDD-Agent](https://arxiv.org/abs/2608.16742) (peer-reviewed, EMNLP 2026) | Full | Size of the test-order effect; feedback iteration |
| [Guardrails Beat Guidance](https://arxiv.org/abs/2604.11088) | Part | Negative constraints in rules |
| [When Does a Second Model Help?](https://arxiv.org/abs/2610.01471) | Abstract | Cross-model review |
| [Is Agentic Code Review Helpful?](https://arxiv.org/abs/2607.03316) | Abstract | Field rejection rate |
| [Are LLMs Reliable Code Reviewers?](https://arxiv.org/abs/2603.00539) | Abstract | Overcorrection |
| [Refute-or-Promote](https://arxiv.org/abs/2604.19049) | Abstract | Refutation before acting |
| [Negative Effect of LLMs on Requirements Inspection](https://arxiv.org/abs/2608.21298) | Full | Order of reading at human review stops |
| [Enforcing a Software Lifecycle Around an AI Coding Agent](https://doi.org/10.2139/ssrn.7675938) (unreviewed report; no artifact) | Full | Sandbox versus text guard; review cost and non-convergence; orchestration cost |
| [SlopCodeBench](https://arxiv.org/pdf/2603.24755) | Search summary | Erosion over iterations |
| [Automating Low-Risk Code Review at Meta (RADAR)](https://arxiv.org/abs/2605.30208) | Abstract | Risk-tiered review |

Still unread and bearing on a decision: the blog post agentops cites for test ordering ([Finster, "Agentic Workflows: Do Agents Work?"](https://bryanfinster.substack.com/p/agentic-workflows-do-agents-work)), known only through agentops's description (Decision 2); and the study Habit Hooks cites for lint coaching.

## Appendix C: last-round candidates, README claim against source

These were first seen at README depth and then read in source, except the last row. The table records where the source confirmed the README and where it didn't.

| Candidate | License, commit | README claim | What the source shows |
|---|---|---|---|
| [promptwheel](https://github.com/promptwheel-ai/promptwheel) | Apache-2.0, 3558f77 | Source-only re-run; gate judged at base | Holds in code. An agent-writable commit trailer can override unless disabled. Benches are committed but synthetic |
| [sawbuck](https://github.com/sawbuck-ai/sawbuck) | Apache-2.0, aed58ec | Measured effects on Claude (test editing 85 of 100 to 0 of 100; reverted attempts 26 of 27 to 0 of 27) | Mechanisms exist. The measurements are not reproducible: no harness, transcripts or per-trial data in either repo, and the README states one result two ways. Not used as evidence |
| [gal-a/qikly](https://github.com/gal-a/qikly) | Apache-2.0, f1b72fd | The coder never sees the criteria; 4 bugs in 50 libraries | Withholding is real and fails closed. The comparison with a sighted coder has not been run; the bug count has no committed data |
| [hamsasoftware/tamperward](https://github.com/hamsasoftware/tamperward) | Apache-2.0, 1832f5b | Pre-registered evidence over 201 trajectories | Fails closed; study design is real. The latest round's prevention effect did not replicate (p = 0.73); no strict bypasses observed |
| [letspecify](https://www.npmjs.com/package/letspecify) | MIT, npm 0.34.0 | Deterministic EARS rules; closed defect types for critics | Confirmed, and richer than the README (majority across passes, same-family critics rejected, raise-only rules). Threshold data not shipped |
| [habit-hooks](https://github.com/habit-hooks/habit-hooks) | MIT, 54e2569 | Lint violation to smell to fix guidance, no model | Confirmed. The cited outcome study is in another repo, unread |
| [simonw/showboat](https://github.com/simonw/showboat) | Apache-2.0, d531261 | Demo documents with recorded, re-checkable output | Confirmed; small and simple. No measurement |
| [vinicq/falsegreen](https://github.com/vinicq/falsegreen) | MIT, 1e4229a | Precise static detection of tests that protect nothing, measured against a 517-smell catalog | Rules and a precision corpus exist. 517 is the size of the catalog it scoped against, not a measurement |
| [hyhmrright/brooks-lint](https://github.com/hyhmrright/brooks-lint) | MIT, 019c9cf | Book-grounded review lenses with a 64-scenario eval suite | One agent following prompts in sequence. Its own pilots are mixed to negative. Weaker than claimed |
| [lennney/stop-that-shit](https://github.com/lennney/stop-that-shit) | MIT, 32fff44 | Guards scope, subagent budget and re-review of unchanged code | Scope and budget guards exist. Re-review is not guarded; the hook fails open; pilots show no improvement. Weaker than claimed |
| [hbmartin/catching-jit-tests-vitest](https://github.com/hbmartin/catching-jit-tests-vitest) | MIT, f0155e2 | Generated tests that pass on the parent and fail on the change | Confirmed; finds regressions, not new behavior. TypeScript only; a possible later review lens |
| [kunchenguid/no-mistakes](https://github.com/kunchenguid/no-mistakes) | MIT, e4ab9d4 | Forward-only pipeline | Docs only. Fails the cloud-session criterion (user-level install, state outside the repo) |
