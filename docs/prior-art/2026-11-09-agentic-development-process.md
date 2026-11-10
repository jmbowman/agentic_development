# Prior art: best-of-breed pieces for an agentic development process (2026-11-09)

- **Effort:** full method, because the result shapes the process components this repo plans (review waves, a commit gate, a spec-review loop, path-scoped rules, enforcement hooks) that every host repo will adopt.
- **Already known:**
  - The developer named no candidates up front.
  - The developer uses BMAD's edge-case hunter lens heavily, mainly to stress-test plans before implementation, where they find it more useful than in code review.
  - The developer has used a centrally managed Claude Code sandbox configuration to enforce policy, on macOS and Windows, and reports that it holds up well in practice.
  - The developer has had good results from a separate agent that produces a testable design (entry points, observable outcomes, seams) before tests are written. They found an extra sequential step like this necessary for good results even with plain TDD.
  - Their stance on spec frameworks: catalog and evaluate them all, but one weaker than LID's is unlikely to be adopted.

## Need and criteria

The process searched against is the one in [issue #98](https://github.com/jmbowman/agentic_development/issues/98). The aim behind it is to find the best-of-breed pieces for each part of the software lifecycle, the way LID is for spec-driven design, and to assemble them into one system a single developer can drive. So candidates were judged on what they do better than anything else, not on how many boxes they tick.

| Requirement as proposed | Underlying need |
|---|---|
| Hooks and a small state machine (#98 step 12) | **N1:** the agent can't skip or reorder phases (code before a failing test, skipped review, convergence declared after late changes); gates hold mechanically |
| Review waves split by lens, with triage, stopping at diminishing returns (steps 8-10) | **N2:** parallel reviewers by lens; findings deduplicated, verified, triaged; repeated until a wave yields nothing worth fixing, with a stopping rule |
| Subagent review of plans and specs (step 2) | **N3:** designs and specs reviewed before implementation, iterated to convergence |
| LID (step 1) | **N4:** a spec-driven method with traceability from design to requirements to tests to code; every framework found is compared with LID |
| Consistent commit messages (step 11) | **N5:** a commit-message linter as a cheap check of form. Message and PR-description *quality* (clear style, detail calibrated for review) is a separate need, left to its own search |
| Compact, modular authoring rules (step 5) | **N6:** rules loaded per file touched |
| Small vertical slices; tests first (steps 6-7) | **N7:** slicing and red-green support |

Hard criteria:
- **H1:** a license compatible with use in, and redistribution beside, an Apache-2.0 project.
- **H2:** runs in Claude Code, local and cloud: what a fresh clone needs can be committed; no daemon or machine-global install the repo can't provide.
- **H3:** nothing merges into the default branch without the developer. Agent commits, pushes, PRs and stacked PRs are acceptable designs for later stages.
- **H4:** works alongside or inside LID, or replaces it with a spec framework at least as strong.

Preferences, weighted most first:
- **Depth of design:** rationale, decision records, evals, iteration.
- **Code over agent hand-offs:** deterministic code does the work where it can.
- **Grounded in evidence:** research or the candidate's own measurement.
- **Configurable commit autonomy:** the developer can stay the committer for now.
- **Maintenance, maturity and portability.**

## Verdict

**Blend.** [A companion design proposal](2026-11-10-agentic-development-process-synthesis.md) assembles these pieces stage by stage, with a build order and the decisions they need. Keep LID as the spine. Adopt Claude Code's native features where they cover a need. Assemble the rest from mechanisms verified in source, mostly by reimplementing them in small pieces of this repo's own, or by proposing them upstream, rather than adopting whole frameworks. One of the lifts (torve) was read only at package-page depth and is marked so.

No framework found is a better base than LID plus native features. The big frameworks (BMAD, superpowers, Compound Engineering, GSD, Spec Kit, OpenSpec) each have one or two mechanisms that are best of breed. But their phase gates are prose, their spec layers are weaker than LID's, and most of them pass work between many agents.

The search stopped before the skill's own stopping rule was met; see "Snowball rounds". This verdict rests on 71 candidates read in source out of 520 serious ones, and the open leads are listed there.

| Lifecycle part | Mechanism to lift, and from where | Class |
|---|---|---|
| Spec framework (N4) | [LID](https://github.com/jszmajda/lid), kept as is | adopt (incumbent) |
| Spec and plan stress-testing (N3) | [BMAD](https://github.com/bmad-code-org/BMAD-METHOD)'s edge-case hunter: exhaustive path tracing, reading the claims only after tracing, then trying to falsify them. [letspecify](https://www.npmjs.com/package/letspecify): deterministic EARS lint (form, single obligation, imprecise terms, near-duplicates), and a gate on critic verdicts: findings outside fixed defect types void the verdict, a finding counts only when most passes report it, and a critic from the author's model family is rejected | borrow ideas: run the hunter as LID's edge-audit inspector; propose the EARS lint for `lidc`; use the verdict gate for spec-review subagents |
| Tests first (N7) | [red-first-gate](https://github.com/ekinkilickaya95-byte/red-first-gate) and [a2dlc](https://github.com/falsable/a2dlc): a new test must fail on the base tree. Tests written from the spec in a context that hasn't seen the implementation, which is the effect with the clearest evidence ([On the risk of coding before testing](https://arxiv.org/abs/2607.05139)); the order itself mattered little ([TDD-Agent](https://arxiv.org/abs/2608.16742)). [promptwheel](https://github.com/promptwheel-ai/promptwheel): reverts test, config and grader edits and re-runs the tests from the base commit, calling a change gamed if most of its gain disappears, with the gate as it stood at the base commit. [qikly](https://github.com/gal-a/qikly): withholds the criteria from the coder, enforced in code and failing closed. Its claimed results have no committed data. [torve](https://pypi.org/project/torve/) (package page only): a check must turn red on a plausible wrong implementation | borrow ideas, with the list of new tests taken from the diff, never from a file the agent writes |
| Test adequacy per requirement | [musthold](https://github.com/RachidChabane/musthold): mutants per requirement, with test execution deciding | build on, through a shim that turns LID specs into its input |
| Traceability and staleness | [Habeas Codicem](https://github.com/nikomatsakis/habeas-codicem) and [2119](https://github.com/Unsupervisedcom/2119): staleness per requirement by content hash of the text and its covering tests. [srs-dd](https://github.com/crellia-s-l/srs-dd): two-way pairing and unclaimed files. [specspan](https://github.com/nripankadas07/specspan) and [V-Model](https://github.com/leocamello/spec-kit-v-model): transitive impact | borrow ideas, proposed upstream as `lidc` enhancements |
| Implementation loop | [superpowers](https://github.com/obra/superpowers)' bounded fix loop: re-review scoped to the findings and the fix diff, escalation at a cap, rulings recorded in a ledger | borrow ideas |
| Review waves (N2) | [craftsman](https://github.com/BuczynskiRafal/craftsman): hunk-by-lens slots, coverage credited by hunk digest, new waves only for verified bugs, ending at the first wave that adds nothing, all in code. Triage from [BMAD](https://github.com/bmad-code-org/BMAD-METHOD) and [Compound Engineering](https://github.com/EveryInc/compound-engineering-plugin): verify at the cited line before deduplicating, route findings to intent gap, bad plan or patch, and don't count agreement between same-model reviewers as corroboration | build on craftsman after a trial; borrow the triage |
| Review convergence and audit | [disensor](https://github.com/NicolasRocchia/disensor): a record of what review couldn't close, and an "integration witness" that some review saw the final tree. The [Claude Code team's measured loop rules](https://claude.dev/blog/solving-code-review-at-anthropic/) | borrow ideas |
| Evaluating reviewers | [layered-code-review](https://github.com/legendtkl/layered-code-review): reviewer evals mined from the repo's own reverts | borrow ideas |
| Enforcement (N1) | Either in-session gates or checks of the result at commit and PR time (an open decision, below). [Probity](https://github.com/nizos/probity) fails closed for edit-time rules. [a2dlc](https://github.com/falsable/a2dlc) and [agent-roast](https://github.com/Nari-Ab/agent-roast) judge a change with the base commit's config. Also borrowed: [DAW](https://github.com/DiluxOne/dilux-agentic-workflow)'s graph-validated transitions and sealed approvals, [spec-flow-plugin](https://github.com/IgnacioMarin402/spec-flow-plugin)'s Stop gate with proof from the test runner, and [ringi-gate](https://github.com/kxmskx/ringi-gate)'s fingerprinted state | build on Probity if in-session gates are kept; borrow the rest |
| Calibrating the gates | [cairn](https://github.com/mesutgulecen/cairn): every guard ships fixtures it must reject and must accept, asserted in CI | adopt the discipline for every hook and checker this repo writes |
| Merge autonomy | [dev-process-toolkit](https://github.com/nesquikm/dev-process-toolkit)'s policy (offer, auto, never), which can only tighten during a run; [foreman](https://github.com/michalzan/foreman)'s fail-closed guard over every spelling of a merge | borrow ideas, when agent PRs begin |
| Capturing learnings | [Compound Engineering](https://github.com/EveryInc/compound-engineering-plugin)'s ladder of durable forms: a check proven to fail on the defect, then a coding standard, then a note | borrow ideas, into session-wrap-up |
| Evaluating the process | [agentops](https://github.com/boshu2/agentops)' practice ledger and its eval method (decision rules fixed before runs, a noise bar from runs that compare a skill with itself); [musthold](https://github.com/RachidChabane/musthold)'s pre-registered experiments | borrow ideas |
| Path-scoped rules (N6) | Claude Code's `.claude/rules/*.md` with `paths:` | adopt (native) |
| Commit form (N5) | [git-sumi](https://github.com/welpo/git-sumi): Conventional Commits optional, blank line enforced, a single binary through mise. [lintje](https://github.com/lintje/lintje) if the current format stays: requires a body, but rejects Conventional prefixes | adopt one, once the message format is decided |

Pieces this repo would build:
1. An enforcement layer (N1): a small phase state machine in committed hooks, or checks of the result at commit and PR time, depending on the decision below.
2. A red-on-base check for new tests, with the list taken from the diff (N7).
3. A shim from LID specs to musthold's input.
4. A review-wave runner, unless a trial of craftsman passes (N2).

Proposals upstream to `lidc`: the EARS-quality rules, staleness per spec, and impact queries.

Open decision on enforcement:
- **In-session gates:** Probity plus a phase state machine stop the agent at the moment of a skipped step.
- **Checks of the result:** gates at commit and PR time, judged with the base commit's config, are harder to bypass, because the agent can't write the state they trust.

The evidence favors checks of the result, because most in-session gates verified here could be bypassed. But a pre-commit check can't catch a skipped step that leaves no trace in the result.

Whichever is chosen, the gates' own state should be protected below the level of hooks. That means Claude Code's sandboxed Bash (`denyWrite`) together with permission deny rules for the file tools, with hooks as a speed bump. In the [SSRN report](https://doi.org/10.2139/ssrn.7675938)'s 11-attack test, the sandbox held where a text guard didn't. None of the candidates verified here relies on it.

The sandbox is off by default, covers Bash only, and isn't documented for cloud sessions. So checks of the result at commit and PR time remain the backstop.

## Candidates and matrix

### Ranked shortlist

Ranked by how much each changes what this repo builds, then by strength of evidence:
1. **[LID](https://github.com/jszmajda/lid):** the spine. Only a framework with as strong a design-to-code chain *and* mechanical checks of it would displace it; none was found.
2. **[craftsman](https://github.com/BuczynskiRafal/craftsman):** the only review wave whose sizing and stopping rule are enforced in code. It would drop if a trial against a plain lens wave showed no gain, or if its fail-open hooks matter in practice.
3. **[BMAD](https://github.com/bmad-code-org/BMAD-METHOD)** and **[Compound Engineering](https://github.com/EveryInc/compound-engineering-plugin):** the best triage and lenses, and BMAD's edge-case hunter for plans. They would drop only if their mechanisms can't be separated from their frameworks.
4. **[musthold](https://github.com/RachidChabane/musthold):** the deepest-designed answer to "do the tests prove the requirement?" It would drop if its second pre-registered loop also comes back inconclusive.
5. **[a2dlc](https://github.com/falsable/a2dlc)**, **[cairn](https://github.com/mesutgulecen/cairn)**, **[disensor](https://github.com/NicolasRocchia/disensor):** principles that every gate should follow (judge with the base commit's config; calibrate every guard; witness the final tree). They're small to borrow, so a change in their own state hardly matters.
6. **[Probity](https://github.com/nizos/probity)**, **[DAW](https://github.com/DiluxOne/dilux-agentic-workflow)**, **[spec-flow-plugin](https://github.com/IgnacioMarin402/spec-flow-plugin):** in-session enforcement. They rank lower because their state can be written by the agent, or their hooks fail open on some events. They'd rise if the developer decides on in-session gates.
7. **[superpowers](https://github.com/obra/superpowers)**, **[agentops](https://github.com/boshu2/agentops)**, **[layered-code-review](https://github.com/legendtkl/layered-code-review)**, **[dev-process-toolkit](https://github.com/nesquikm/dev-process-toolkit):** single mechanisms for the fix loop, process evals, reviewer evals and merge policy.
8. The remaining verified candidates each add one idea or fail a hard criterion.

### Verified candidates

71 candidates were read in source, including `lidc` and Shallnot (under "Limitations checked in source"). "Best of breed for" names the part where a candidate's mechanism beat every other one verified.

| Candidate | Best of breed for | Class | License (file:line at commit) | Reason |
|---|---|---|---|---|
| [LID](https://github.com/jszmajda/lid) | spec framework | adopt | MIT, LICENSE:1 at 727ed80 | design tree, path IDs, cascade; enforcement is prose |
| [craftsman](https://github.com/BuczynskiRafal/craftsman) | review waves | build on | MIT, LICENSE:1 at 938da91 | coded wave plan and cap; seeded-suite recall 89-96%, precision 71-86%; hooks fail open |
| [musthold](https://github.com/RachidChabane/musthold) | test adequacy per requirement | build on | Apache-2.0, LICENSE:1-3 at 6d45cdd | execution decides; pre-registered first loop inconclusive at 1.82 times the cost |
| [Probity](https://github.com/nizos/probity) | edit-time rules | build on | MIT, LICENSE:1 at eeac421 | fails closed; Bash writes escape its TDD rule; unpinned `npx` |
| [BMAD](https://github.com/bmad-code-org/BMAD-METHOD) | lenses, triage, plan stress-testing | borrow ideas | MIT, LICENSE:1-3 at a867e16 | spec layer weaker than LID's; always commits locally |
| [Compound Engineering](https://github.com/EveryInc/compound-engineering-plugin) | triage, capturing learnings | borrow ideas | MIT, LICENSE:1-3 at dd9b792 | gates are prose; commits and pushes |
| [superpowers](https://github.com/obra/superpowers) | implementation fix loop | borrow ideas | MIT, LICENSE:1-3 at 22f0b46 | prose gates; its evals are in a separate repo |
| [DAW](https://github.com/DiluxOne/dilux-agentic-workflow) | phase enforcement | borrow ideas | Apache-2.0, LICENSE:2-3 at 7b1461f | a competing pipeline; merge gate misses `gh api` merge |
| [spec-flow-plugin](https://github.com/IgnacioMarin402/spec-flow-plugin) | in-session Stop gate | borrow ideas | MIT, LICENSE:1 at 7b9c40a | state the agent can write; "not a security boundary" by its own docs |
| [a2dlc](https://github.com/falsable/a2dlc) | verifying against the base | borrow ideas | Apache-2.0, LICENSE:1-2 at 03baa28 | needs Docker and a Go binary; its hook layer leaks |
| [cairn](https://github.com/mesutgulecen/cairn) | calibrating guards | borrow ideas | MIT, LICENSE:1 at bf3f4b7 | hooks fail open by policy |
| [disensor](https://github.com/NicolasRocchia/disensor) | review audit record | borrow ideas | MIT, LICENSE:1 at 1190b97 | one reviewer per round; no waves |
| [agentops](https://github.com/boshu2/agentops) | evaluating the process | borrow ideas | Apache-2.0, LICENSE:1-2 at 80313b2 | small n; outside studies unverified |
| [layered-code-review](https://github.com/legendtkl/layered-code-review) | evaluating reviewers | borrow ideas | MIT, LICENSE:1 at ef1f114 | one commit; no published results |
| [dev-process-toolkit](https://github.com/nesquikm/dev-process-toolkit) | merge-autonomy policy | borrow ideas | MIT, LICENSE:1 at e9d6c65 | needs Bun; gates prove a skill ran, not that it passed |
| [git-sumi](https://github.com/welpo/git-sumi) | commit form | adopt (if Conventional Commits) | MIT OR Apache-2.0, Cargo.toml:7 and LICENSE-MIT:1 at 7aa2310 | blank line enforced; can't require a body; opt-in `--commit` |
| [lintje](https://github.com/lintje/lintje) | commit form | adopt (if the current format stays) | MIT, LICENSE:1 at db4bdd1 | requires a body; rejects Conventional prefixes; no pre-commit hook definition |
| [judicata](https://github.com/philippmelikidis/judicata) | | borrow ideas | MIT, LICENSE:1 at c7b3983 | dedupe and a refuting verifier, now superseded by craftsman and BMAD's triage; no lens split; Stop gate fails open |
| [Alibaba open-code-review](https://github.com/alibaba/open-code-review) | | borrow ideas | Apache-2.0, LICENSE:1-2 at b1dcffb | delete-only falsifying filter; external binary and API key |
| [spencermarx open-code-review](https://github.com/spencermarx/open-code-review) | | borrow ideas | Apache-2.0, LICENSE:1-2 at 9fce816 | lens personas; dedupe is prose; no stop across waves |
| [review-convergence](https://github.com/marcmeezy/review-convergence) | | borrow ideas | MIT, LICENSE:1 at 5d6e0e9 | stopping rule only |
| [deep-review-loop](https://github.com/1273984347/deep-review-loop) | | borrow ideas | Apache-2.0, LICENSE:1-3 at 643f514 | cost-and-harm stopping rule, in prose |
| [ringi-gate](https://github.com/kxmskx/ringi-gate) | | borrow ideas | Apache-2.0, LICENSE:2 at 4bb60d3 | runner-owned verdict; external Node 24 CLI |
| [red-first-gate](https://github.com/ekinkilickaya95-byte/red-first-gate) | | borrow ideas | MIT, LICENSE:1 at 339e06b | sound check; reads the agent-written list of new tests |
| [agent-roast](https://github.com/Nari-Ab/agent-roast) | | borrow ideas | MIT, LICENSE:1 at 9c87c3a | 71/71 labelled cheats caught; Stop hook advisory |
| [claimcheck](https://github.com/Allan-Nava/claimcheck) | | borrow ideas | MIT, LICENSE:1 at 6bcb74c | audit-mode-first method; fails open |
| [preflight](https://github.com/solozerolabs/preflight) | | borrow ideas | MIT, LICENSE:1 at 02e4a59 | stamps the agent can write; pushes to main by default |
| [steerloop](https://github.com/lukavtz/steerloop) | | borrow ideas | MIT, LICENSE:1 at dd4ae33 | a committed 90-cell A/B of skill prose |
| [zeroshot](https://github.com/the-open-engine/zeroshot) | | borrow ideas | MIT, LICENSE:1 at b3b4122 | statically checked process graph; fails H2 |
| [Rivet / dev-spec-kit](https://github.com/pratiyush/dev-spec-kit) | | borrow ideas | MIT, LICENSE:1 at aea3af6 | proofs tied to the tree hash; can't be built from a fresh clone |
| [Habeas Codicem](https://github.com/nikomatsakis/habeas-codicem) | | borrow ideas | MIT OR Apache-2.0, Cargo.toml:7 at 2e8083f | staleness per requirement; Rust and mdBook only |
| [2119](https://github.com/Unsupervisedcom/2119) | | borrow ideas | MIT, LICENSE:1-3 at 652891f | verdicts bound by hash; can't parse LID IDs |
| [srs-dd](https://github.com/crellia-s-l/srs-dd) | | borrow ideas | MIT, LICENSE:1-3 at 29e38cb | two-way trace checks; no design tree |
| [Spec Engine](https://github.com/spec-engine/spec-engine) | | borrow ideas | MIT, LICENSE:1 at 1f844fd | link-loss guard; single-segment IDs only |
| [tracey](https://github.com/bearcove/tracey) | | borrow ideas | MIT OR Apache-2.0, LICENSE-MIT:1-3 at 66008a8 | versioned rule IDs clash with LID's stable IDs |
| [specspan](https://github.com/nripankadas07/specspan) | | borrow ideas | MIT, LICENSE:1 at d0c1fe0 | transitive impact; `REQ-` IDs only |
| [V-Model](https://github.com/leocamello/spec-kit-v-model) | | borrow ideas | MIT, LICENSE:1-3 at e050c7b | impact analysis; replaces LID's arrow |
| [Intent Reconciliation](https://github.com/SuhaibAslam/spec-kit-reconcile) | | borrow ideas | MIT, LICENSE:1 at 0805a68 | sorts discoveries by re-entry level, in prose |
| [OpenSpec](https://github.com/Fission-AI/OpenSpec) | | borrow ideas | MIT, LICENSE:1 at 579fcac | delta specs merged by code; no IDs |
| [cc-sdd](https://github.com/gotalab/cc-sdd) | | borrow ideas | MIT, LICENSE:1-3 at e2a0c67 | feature-flag red proof; prose |
| [GSD](https://github.com/gsd-build/get-shit-done) | | borrow ideas | MIT, LICENSE:1-3 at bdcaab2 | goal-backward verification; can merge into the checked-out branch |
| [Spec Kit](https://github.com/github/spec-kit) | | borrow ideas | MIT, LICENSE:1-3 at 08252af | converge and analyze; prose hooks |
| [Agent OS](https://github.com/buildermethods/agent-os) | | borrow ideas | MIT, LICENSE:1-3 at e892e61 | standards interview |
| [ouroboros](https://github.com/Q00/ouroboros) | | borrow ideas | MIT, LICENSE:1 at 592c667 | numeric readiness score; the LLM rates itself |
| [haft](https://github.com/m0n0x41d/haft) | | borrow ideas | MIT, LICENSE:1 at e0c63f4 | decision evidence that expires |
| [Rigour](https://github.com/rigour-labs/rigour) | | borrow ideas | MIT, LICENSE:1 at 7e0ef7f | per-check precision; dismissals read from the merge base |
| [IIKit](https://github.com/intent-integrity-chain/kit) | | borrow ideas | MIT, LICENSE:1 at 805efaa | the agent can re-lock its hashed assertions; installs only through Tessl |
| [cc-spex](https://github.com/rhuss/cc-sdd) | | borrow ideas | Apache-2.0, LICENSE:1-3 at 8be8b8c | superseded/retired markers; manifests say MIT |
| [adamsreview](https://github.com/adamjgmiller/adamsreview) | | borrow ideas | MIT, LICENSE:1 at b5b8ef4 | seven lenses; no stopping rule |
| [foreman](https://github.com/michalzan/foreman) | | borrow ideas | MIT, LICENSE:1-3 at 13c771b | fail-closed merge guard; other gates fail open |
| [stull](https://github.com/justinstimatze/stull) | | borrow ideas | MIT, LICENSE:1-3 at 81538d7 | fuel-bounded hook state machines; fails open |
| [tdd-guard](https://github.com/nizos/tdd-guard) | | borrow ideas | MIT, LICENSE:1 at ffb7026 | superseded by Probity |
| [aidoc-flow](https://github.com/vladm3105/aidoc-flow-framework) | | borrow ideas | MIT, LICENSE:1-3 at 747b38c | IDs change when wording changes |
| [multi-agent-review](https://github.com/riekelt/multi-agent-review) | | borrow ideas (no license text) | none; MIT in plugin.json:12 only, at 6db8b1f | tiered spec-review panel |
| [humanize](https://github.com/PolyArch/humanize) | | borrow ideas (no license text) | none; MIT in plugin.json:10 only, at 4eeb392 | breaker after stalled rounds |
| [NTCoding team plugin](https://github.com/NTCoding/autonomous-claude-agent-team) | | borrow ideas (no license) | none (listing at 24ab0ce) | event-sourced phases |
| [promptwheel](https://github.com/promptwheel-ai/promptwheel) | checking that green was earned | borrow ideas | Apache-2.0 (license file at 3558f77) | re-run from the base commit, with the base commit's gate; a commit trailer lets the agent clear a verdict unless disabled; its example Stop hook fails open |
| [tamperward](https://github.com/hamsasoftware/tamperward) | research method for keeping tests honest | borrow ideas | license file at 1832f5b (not recorded) | hooks fail closed; states what it can't block; its pre-registered prevention effect didn't replicate (b=5, c=3, p=0.727) |
| [qikly](https://github.com/gal-a/qikly) | | borrow ideas | Apache-2.0, LICENSE:1-2 at f1b72fd | withholds criteria from the coder, enforced in code and failing closed; claimed results have no committed data; its own pipeline, outside Claude Code |
| [sawbuck](https://github.com/sawbuck-ai/sawbuck) | | borrow ideas | Apache-2.0 (license file at aed58ec) | Stop wall on protected paths; state the agent can edit; fails open; A/B not reproducible |
| [falsegreen](https://github.com/vinicq/falsegreen) | | borrow ideas | MIT (license file at 1e4229a) | AST scanner for Python tests that can never fail; pre-commit hook fails open; no precision data |
| [catching-jit-tests-vitest](https://github.com/hbmartin/catching-jit-tests-vitest) | | borrow ideas | MIT (license file at f0155e2) | harvests generated tests that fail on the PR; TypeScript only; calibration has no data |
| [letspecify](https://www.npmjs.com/package/letspecify) | checking spec quality | borrow ideas | MIT, package/LICENSE:1 in npm 0.34.0 (tarball matches the registry's sha512). Vendored tree-sitter grammars and runtime are MIT (`package/vendor/tree-sitter/LICENSES/`). The package's declared repository returns 404. The author's public [kaerumotoharu-sudo/letspecify](https://github.com/kaerumotoharu-sudo/letspecify) is an older snapshot (0.6.0, last pushed 2026-08-15), so the npm package is the only public copy of the current source | deterministic EARS lint and a verdict gate; its own spec repo and ID scheme; its rules only warn, and report NOT EVALUATED without a vocabulary |
| [Habit Hooks](https://github.com/habit-hooks/habit-hooks) | turning lint findings into fix guidance | borrow ideas | MIT (license file at 54e2569) | deterministic; an incomplete run never counts as a pass; ships only CLAUDE.md prose, so it needs wiring as a hook |
| [Showboat](https://github.com/simonw/showboat) | proving a slice's behavior for human review | borrow ideas | Apache-2.0 (license file at d531261) | `verify` re-runs recorded commands and fails on any difference; effect unmeasured |
| [brooks-lint](https://github.com/hyhmrright/brooks-lint) | | borrow ideas | MIT, LICENSE:1 at 019c9cf | Symptom-Source-Consequence-Remedy finding format; evals check structure, not correctness; its SessionStart hook writes to `~/.claude/commands` |
| [stop-that-shit](https://github.com/lennney/stop-that-shit) | | borrow ideas | MIT, LICENSE:1 at 32fff44 | a task-authority contract set only by the user's prompt; its guard against re-reviewing unchanged code is prose; hook fails open |
| [conductor](https://github.com/gemini-cli-extensions/conductor) | | reject | Apache-2.0, LICENSE:1-3 at 6e8f9a8 | prose only; no IDs |
| [cocogitto](https://github.com/cocogitto/cocogitto) | | reject | MIT at 8cfddce (file line not recorded) | Conventional Commits only; can't require a body |

### Matrix of the shortlist

Values: `native`, `partial`, `extensible`, `unsupported`, `unverified`; `n/a` where a criterion doesn't apply. The source of each cell is in parentheses, or is the candidate's row in "Limitations checked in source".

| Candidate | H1 | H2 | H3 | H4 | Depth of design | Code over agents | Evidence | Commit autonomy configurable | Maintained (HEAD) |
|---|---|---|---|---|---|---|---|---|---|
| LID | native (LICENSE:1) | native (APM) | native (no git writes) | native | native (decision templates, evals) | partial (`lidc`; gates are prose) | partial (practitioner use) | n/a | 2026-11-09 |
| craftsman | native | partial (hooks fail open) | native (no commits) | n/a | native (protocol doc, 8 releases with evals) | native | partial (seeded suite) | n/a | 2026-11 |
| musthold | native | partial (go install; XDG state) | native | n/a | native (17 ADRs) | native | partial (first loop inconclusive) | n/a | 2026-11 |
| Probity | native | partial (unpinned `npx`) | native | n/a | partial | native | unverified (none published) | n/a | 2026-11-03 |
| BMAD | native | partial (uv, Python) | partial (always commits locally) | unsupported (spec layer weaker; lenses usable) | native (changelog A/B results) | partial | partial | unsupported (no switch) | 2026-11-07 |
| Compound Engineering | native | partial (vendored skills) | partial (commits and pushes) | unsupported (spec layer weaker) | native (~150 plan and eval docs) | partial | partial | unsupported | 2026-11-09 |
| superpowers | native | partial (vendored skills) | partial (agents commit per task) | unsupported (spec layer weaker) | native (dated specs, 57 releases) | partial | partial (evals docs only) | partial (CLAUDE.md override) | 2026-11-03 |
| DAW | native | native | partial (merge gate misses `gh api` merge) | unsupported (PRD with AC IDs; no design tree) | native (RATIONALE.md, 16 scenarios) | native | partial | native (assisted and minimal modes) | 2026-11-07 |
| spec-flow-plugin | native | partial (Node projects) | partial (commits and pushes per milestone) | partial (own IDs, runner proof) | native (53 ADRs) | native | partial (engine tested; model evals have no results) | unsupported | 2026-11 |
| a2dlc | native | partial (Go binary, Docker) | native | n/a | native (10 RFCs, protocol) | native | partial (pre-registered; small sets; raw logs not committed) | n/a | 2026-11 |
| cairn | native | native | native | n/a | partial (calibration history in comments) | native | partial (fixtures only) | n/a | 2026-11 |
| disensor | native | partial (cross-family reviewer needs its own login) | native | n/a | native (method paper, schemas) | native | partial (measures the record) | n/a | 2026-11 |
| agentops | native | native | native | n/a | native (ADRs, eval reports) | partial (guidance more than code) | partial (small n) | n/a | 2026-11 |
| layered-code-review | native | partial (state outside the repo) | native | n/a | partial | partial | unverified (no results) | n/a | 2026-10-18 |
| dev-process-toolkit | native | partial (Bun) | native | unverified | partial | native | partial (tests over phrasings) | partial (merge ratchet; commits fixed) | 2026-11-10 |

### Native features (docs only)

| Feature | Need | Support | Source |
|---|---|---|---|
| Hooks: a PreToolUse `deny`, or exit 2, blocks; exit 1 doesn't; hooks fail open by default. `onFailure: "block"` fails closed on command and http handlers (v2.1.295+). A secondary source says it's ignored on Stop and SubagentStop | N1 | extensible | [Claude Code hooks](https://code.claude.com/docs/en/hooks.md); [onFailure on Stop hooks](https://startdebugging.net/2026/10/how-to-make-a-claude-code-hook-fail-closed-with-onfailure-block/) (secondary) |
| Sandboxed Bash: an OS-level profile restricting what shell commands and their children can write and reach on the network | N1 | partial | [Claude Code sandboxing](https://code.claude.com/docs/en/sandboxing), [sandbox environments](https://code.claude.com/docs/en/sandbox-environments). <ul><li>**Coverage:** Bash only. Read, Edit and Write follow permission rules instead, and hooks and MCP servers run outside the sandbox. So protecting a gate's state takes a sandbox `denyWrite` *and* permission deny rules.</li><li>**Platforms:** macOS (Seatbelt) or Linux with bubblewrap and socat installed. It's off by default, and runs unsandboxed when unavailable unless `failIfUnavailable` is set.</li><li>**Built-in protection:** `.claude/hooks`, `.claude/settings*` and `.git/hooks` are always protected.</li><li>**Escapes:** the model can ask to run a command unsandboxed unless `allowUnsandboxedCommands: false` is set.</li><li>**Cloud sessions:** not documented.</li><li>**Unconfirmed:** whether `denyWrite` beats the working directory's default write grant.</li><li>**Evidence it holds where hooks don't:** only the SSRN report's 11-attack test, on macOS.</li></ul> |
| Stop blocks are overridden after 8 consecutive continuations | N1 | partial | [Claude Code environment variables](https://code.claude.com/docs/en/env-vars) |
| Committed `.claude/settings.json` hooks run in cloud sessions; plugins in `enabledPlugins` aren't installed there | H2 | partial | [Claude Code cloud environments](https://code.claude.com/docs/en/cloud-environments.md#what-carries-over-from-your-setup) |
| Path-scoped rules | N6 | native | [Claude Code memory](https://code.claude.com/docs/en/memory.md#path-specific-rules) |
| Dynamic workflows (loops in plain JavaScript); `/code-review`; ultrareview | N2 | extensible | [Claude Code workflows](https://code.claude.com/docs/en/workflows.md); [Claude Code local code review](https://code.claude.com/docs/en/code-review-local.md) |

### Blends considered

1. **The chosen blend:** LID as the spine, native features, and small pieces of this repo's own that reimplement verified mechanisms. Every part passes H1-H4, and most of the heavy design work is borrowed.
2. **A big framework as the host, with LID inside it** (BMAD, superpowers, Compound Engineering or GSD). Rejected: each has a weaker spec layer and prose gates, and practitioner reports put BMAD and GSD at the highest cost.
3. **DAW as the whole process.** Rejected: its pipeline replaces LID's phase flow. Its enforcement core is borrowed instead.
4. **craftsman unmodified as the review wave.** Kept as the leading base to build on: its plugin hooks fail open, and its triage is weaker than BMAD's and Compound Engineering's. Decide after a trial.

### Scenario walk

1. **A fresh cloud session.**
   - Plugins in `enabledPlugins` aren't installed there, so enforcement must come from hooks committed in `.claude/settings.json`, calling tools pinned through mise.
   - Every gate's state must be outside the agent's write reach, or fingerprinted and checked again (ringi-gate, a2dlc).
   - Hooks fail closed where the platform allows, which excludes Stop hooks, so no Stop hook is the only check.
2. **Tests first, attempted with a Bash heredoc.**
   - Probity's file-edit rule misses the heredoc, so a shell-write rule is added.
   - The check of new tests takes their list from the diff and requires each to fail on the base tree (red-first-gate, a2dlc), refusing an agent-written list.
3. **Late changes after a review wave converged.**
   - Coverage credited by hunk digest (craftsman) re-reviews only the changed hunks.
   - An integration witness (disensor) requires that some review saw the final tree.
   - The Claude Code team's rules apply: cap at 3 rounds, never repeat a finding, tag findings on old code "pre-existing". Under them, mean reviews to pass fell from 2.08 to 1.32.
4. **Agents start opening PRs.**
   - The merge policy can only tighten during a run, and "auto" needs the operator's config (dev-process-toolkit).
   - Every spelling of a merge prompts the developer (foreman).
   - The default branch stays human-merged, backed by forge branch protection.

## Practitioner evidence

These are first-party or vendor reports, unverified:
- **[Solving code review at Anthropic](https://claude.dev/blog/solving-code-review-at-anthropic/)** (Claude Code team):
  - About 59% of repeat flags were on code that predated the reviewer's first pass.
  - Their fixes: a 3-round cap, diff-only re-review, fixing every instance of a bug class, never repeating a finding, Important/Nit/Pre-existing tags, verifiers voting, every incident becoming an eval case.
  - Reported results: one-round pass rate from 65% to 78%; mean reviews to pass from 2.08 to 1.32.
- **[Harness design for long-running apps](https://anthropic.com/engineering/harness-design-long-running-apps)** (Anthropic): a skeptical separate evaluator, and contracts with hard thresholds for each criterion. Out of the box, Claude acting as QA talked itself into approving.
- **[Meta RADAR](https://arxiv.org/abs/2605.30208):** the abstract reports an automated review funnel tiered by risk, over 331k landed diffs, at a third of the revert rate.
- **[Spec-driven development benchmark](https://uvik.net/blog/spec-driven-development-benchmark/)** (Uvik; vendor-run, one team, one model):
  - Cost: BMAD was highest ($4.23 per merged ticket).
  - Drift: OpenSpec was lowest (2.4%), Spec Kit highest (12.5%).
  - Where specs paid off: only for features, data pipelines and tickets touching three or more files.
- **[Exploring spec-driven development tools](https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html)** (Böckeler): Spec Kit produced too much markdown, and the agent duplicated existing classes.
- **[GSD vs superpowers vs Claude Code](https://chaseai.io/blog/gsd-vs-superpowers-vs-claude-code)** (a single run): GSD took about 5 times the time and 6 times the tokens, with no better output.
- **[sawbuck](https://github.com/sawbuck-ai/sawbuck)'s README A/B:** one CLAUDE.md line reportedly took test edits from 85 in 100 to 0 in 100. Neither sawbuck's repo nor promptwheel's contains the harness, data or transcripts, so it can't be reproduced and is given no weight here.
- **[agentops](https://github.com/boshu2/agentops)' practice ledger:**
  - Mandatory review "never converged".
  - Test-first ordering isn't supported as a rule. This one rests on a practitioner blog post that wasn't read here.
  - A code gate halved false completion claims, where prose removed none.
- **Writing on agent harnesses:**
  - [My AI adoption journey](https://mitchellh.com/writing/my-ai-adoption-journey) (Hashimoto) and [Agent harness engineering](https://addyosmani.com/blog/agent-harness-engineering/) (Osmani): every rule in an agent file traces to a past failure.
  - [Backpressure in coding agent harnesses](https://dasith.me/2026/06/14/backpressure-in-coding-agent-harnesses/) (Dasith): gates that rely on a model's judgment should start out advisory.
  - [Skill issue: harness engineering](https://www.humanlayer.dev/blog/skill-issue-harness-engineering-for-coding-agents) (HumanLayer): subagents split by role failed for them.
- **[Thoughtworks Technology Radar, Vol. 35](https://www.thoughtworks.com/radar/techniques):** mutation testing is in Adopt; risk-tiered oversight is in Trial; human-in-the-loop theater and stacked PRs are in Caution.

## Limitations checked in source

Each "verified in source" item is at the commit given in the verified-candidates table.

Verified:
- **LID:** its plugins ship no hooks. The only script is an optional reference `coherence-check.mjs` that always exits 0. *Verified in source (listing at 727ed80).*
- **`lidc`** ([lid-tooling](https://github.com/EtaCassiopeia/lid-tooling) at 1f5627d; MIT OR Apache-2.0, `Cargo.toml:9`):
  - It registers 13 checks (`checks/mod.rs:46-62`); this repo runs 3.
  - It has no staleness check: `audited_sha` is parsed but never read.
  - It decides whether a citation is a test from the absolute file path (`parse/source.rs:126-169`). So citations in `.sh` and `.yaml` files count as neither code nor test, and a checkout under a directory named `test` or `tests` makes coverage pass vacuously.
  - A spec ID with no digit aborts the run, and a lowercase one is silently ignored (`parse/markdown.rs:38-41`).
  - Comma lists in `@spec` work (`parse/source.rs:94-112`).

  *Verified in source.*
- **[Shallnot](https://github.com/RachidChabane/shallnot)** at 1434e8a (Apache-2.0):
  - It binds tests to requirements only from JUnit results, with `ID~REV` tags.
  - Its default ID pattern rejects multi-segment IDs like LID's.
  - Its Stop hook blocks on test failures, but lets the turn end when the hook itself errors, and gives up after 3 blocks.

  *Verified in source.* So a musthold shim must run real Shallnot on a generated spec, or stand in for its CLI. It isn't a file conversion.
- **Fail-open hooks:**
  - tdd-guard: *verified in source (`src/cli/tdd-guard.ts:39-49`)*;
  - judicata: *verified in source (`gate.py:124`)*;
  - foreman: *verified in source (`hooks/stop_gate.py:369-381`)*;
  - humanize: *verified in source (`write-validator:191-193`, `bash-validator:214-217`)*;
  - claimcheck: *verified in source (`claimcheck.mjs:136-144`)*.
- **Fail-closed hooks:**
  - Probity: *verified in source (`src/config.ts:110-131`)*;
  - spec-flow-plugin's Stop gate, on its own crash: *verified in source (`internal/hooks/gate.go:149-478`)*.
- **Agent-writable state defeats the gate:**
  - tdd-guard: *verified in source (`src/guard/GuardManager.ts:17-38`)*;
  - preflight: *verified in source (`stamp-lib.sh:32-40`)*;
  - spec-flow-plugin: *verified in source (`phaseguard.go:45-59`)*;
  - red-first-gate: *verified in source (`red_first_gate.py:249-266`)*;
  - Rivet: *verified in source (`guard-protect.mjs:86-115`)*.
- **Defenses that hold:**
  - a2dlc reads the base commit's config: *verified in source (`internal/app/app.go:217-275`)*;
  - ringi-gate fingerprints its state and checks it again: *verified in source (`agent-review-loop-lib.mjs:2855-2950`)*.
- **"Gates" that are prose:**
  - Spec Kit's extension hooks: *verified in source (`src/specify_cli/extensions/__init__.py:6177-6178`)*;
  - IIKit's red-before-green: *verified in source (`iikit-07-implement/SKILL.md:96-98`)*.
- **Gates that match only some tools:** IIKit's hook matches Bash only. *Verified in source (`check-hook-bypass.sh:1-44`).*
- **Mechanisms that hold in code:**
  - craftsman's wave plan and cap: *verified in source (`huntplan.py:186-241,590-603`)*;
  - BMAD's triage routing: *verified in source (`skills/bmad-build/step-04-review.md:51-103`)*;
  - Compound Engineering's fingerprint dedupe and independence rule: *verified in source (`findings-mechanics.py:67-131,222-229`)*;
  - Alibaba's delete-only filter: *verified in source (`agent.go:1565-1615`)*;
  - OpenSpec's delta merge: *verified in source (`src/core/specs-apply.ts:168-420`)*;
  - disensor's G6 and G7 gates: *verified in source (`gate.py:639-711`)*.
- **Merges into the default branch:**
  - preflight pushes HEAD to main by default: *verified in source (`run.sh:710`)*;
  - GSD's default branching merges executor worktrees into the checked-out branch: *verified in source (`execute-phase.md:784`)*.
- **Licenses:** as in the verified-candidates table. Two candidates have no license text, only a manifest field: multi-agent-review and humanize. NTCoding's team plugin has no license.

Could not verify (docs only, snippet depth, or not cloned):
- musthold's checks of mutant validity and staleness. *Docs only (ADRs 0008 and 0017).*
- [Rigour](https://github.com/rigour-labs/rigour) reads dismissals from the merge base (`trusted-state.ts`; no line recorded).
- [dev-process-toolkit](https://github.com/nesquikm/dev-process-toolkit)'s merge ratchet (`merge_policy_ratchet.ts`; no line recorded).
- [RQML](https://www.npmjs.com/package/@rqml/cli): its approval is a status flip the agent can run. Read from the `@rqml/cli` 0.11.0 tarball; no repository was cloned.
- Claims recorded without a line citation:
  - craftsman's launcher exits 0 when Python is missing;
  - cc-spex's gate covers Skill calls only;
  - cairn's hooks run after the fact on Edit, Write and MultiEdit;
  - Probity's TDD rule lets Bash writes through;
  - BMAD's, superpowers' and Compound Engineering's phase order are prose;
  - deep-review-loop's stopping rule is prose;
  - DAW's merge gate misses `gh api .../merge`.
- Everything outside the verified table: snippet or docs depth.
- Native Claude Code features: docs only, as the product is closed source.
- [superpowers](https://github.com/obra/superpowers)' evals, which are in a separate repo.
- Round-5 candidates, read at README or package depth only:
  - [torve](https://pypi.org/project/torve/), [no-mistakes](https://github.com/kunchenguid/no-mistakes);
  - [Hypothesis's Claude Code command](https://hypothesis.works/articles/claude-code-plugin/), [ast-grep](https://www.thoughtworks.com/radar/tools/ast-grep).
- [Habit Hooks](https://github.com/habit-hooks/habit-hooks)' cited pre-registered study (83.3% genuine fixes with coaching against 5.6-28.9% with a bare metric) was seen only in its README.
- The practitioner experiment agentops cites for "test-first ordering not supported" ([Agentic workflows: do agents work?](https://bryanfinster.substack.com/p/agentic-workflows-do-agents-work)). It's a blog post that wasn't read; its claims here are secondhand, through agentops' `docs/practice-ledger.md:71`.
- **Codeberg:** unavailable. HTTP 429 in rounds 1, 3 and 4; not retried in rounds 2 and 5.
- **Semantic Scholar:** unavailable. HTTP 429 with the key set, on three attempts. Its substitute, OpenAlex, was searched, and no Semantic Scholar data was used.

## Papers

| Paper | Read state | Evidence strength | Review status | Class | Claim (tag) |
|---|---|---|---|---|---|
| [A Gated Spec-Driven Workflow](https://arxiv.org/abs/2611.05094) | read in part (3, 5.2-5.3, 7, 8) | observational study | preprint | borrow ideas | Reports that re-reviews didn't converge, and recommends moving controls into tooling (paper-reported) |
| [Humanize](https://arxiv.org/abs/2610.08900) | read in part (3.2, 3.3, 4, 6, 8) | observational study | preprint | borrow ideas | Reports uncapped review tails, and argues termination must be designed (paper-reported) |
| [Introducing Consort](https://arxiv.org/abs/2609.09671) | read in part (II-B, II-C, IV-D, V) | untested proposal | preprint | borrow ideas | Proposes classing enforcement as persuasion, structure, or controls the agent can't edit (paper-reported) |
| [A Deterministic Control Plane for LLM Coding Agents](https://arxiv.org/abs/2606.26924) | read in part (4.5, 10, App. C) | weak experiment | preprint | borrow ideas | Reports a phase lifecycle as a labelled transition system with invariants (paper-reported) |
| [Bounded Loops](https://arxiv.org/abs/2609.27871) | read in part (2.4, 8.1) | experiment | preprint | borrow ideas | Reports completion decided by a gate the worker can't write (paper-reported) |
| [More Rounds, More Noise](https://arxiv.org/abs/2603.16244) | read in part (2.2, 6.4, 6.5) | experiment | preprint | borrow ideas | Reports later rounds raising false positives, and a 2-of-3 parallel ensemble beating iteration (paper-reported) |
| [Cross-Context Review](https://arxiv.org/abs/2603.12123) | read in part (7.2, 8) | weak experiment | preprint | borrow ideas | Reports a second review in a fresh session beating one in the same session, but not robustly beating a single review (paper-reported) |
| [Rethinking Verification in Agent Harnesses](https://arxiv.org/abs/2610.34577) | read in part (5, 6, B.4, E.5) | experiment | preprint | borrow ideas | Reports more parallel critics costing less than more rounds (paper-reported) |
| [Adversarial Review](https://arxiv.org/abs/2608.18167) | read in part (3.3-3.4, 4.5, 5.2, 7, 8) | weak experiment | preprint | borrow ideas | Reports a critic auditing the review before the author edits helping most (more than a meta-reviewer over three reviewers); a second independent reviewer didn't beat one beyond noise (paper-reported) |
| [OpenCodeReview](https://arxiv.org/abs/2608.09290) | read in part (3.2.3, 3.4.2-3, 4.2, 6) | weak experiment | preprint | borrow ideas | Reports a falsifying reflector filtering comments (paper-reported; the filter is verified in the artifact) |
| [Guardrails Beat Guidance](https://arxiv.org/abs/2604.11088) | read in part (7, 8) | experiment | preprint | borrow ideas | Reports a rule file's presence mattering more than its content (paper-reported) |
| [Spec-Driven Development as Prescribed and as Practiced](https://arxiv.org/abs/2608.25202) | read in part (IV-B, V-C, VII) | observational study | preprint | borrow ideas | Reports that no tool checks spec-code agreement after implementation (paper-reported) |
| [Citation Discipline in SDD](https://arxiv.org/abs/2606.30689) | read in part (8, 9) | experiment | preprint | borrow ideas | Reports requirement-ID citations in code letting tools detect 86-88% of hallucinations, which supports `@spec` (paper-reported) |
| [On the risk of coding before testing](https://arxiv.org/abs/2607.05139) | read in full | experiment | preprint | borrow ideas | Reports, over 5 models on HumanEval+, MBPP and BigCodeBench: <ul><li>Showing the code to the test writer cut the faults its tests caught by 13.2% on average.</li><li>Tests written in a fresh context from the spec alone caught 11.7% more faults.</li><li>Prompting tricks didn't close the gap.</li></ul>What it varied was the test writer's context, not the order (paper-reported) |
| [Spec Kit Agents](https://arxiv.org/abs/2604.05278) | read in part (abstract, 5) | weak experiment | preprint | borrow ideas | Reports phase hooks adding +0.15 to judged quality (paper-reported) |
| [Meta RADAR](https://arxiv.org/abs/2605.30208) | abstract only | observational study | preprint | borrow ideas | The abstract reports a risk-tiered review funnel at a third of the revert rate (paper-reported) |
| [Evaluating AGENTS.md](https://arxiv.org/abs/2602.11988) | abstract only | experiment | preprint | borrow ideas | The abstract reports context files adding over 20% cost without raising success (paper-reported) |
| [Refute-or-Promote](https://arxiv.org/abs/2604.19049) | abstract only | observational study | preprint | borrow ideas | The abstract reports adversarial gates removing about 80% of candidate findings (paper-reported) |
| [Is Agentic Code Review Helpful?](https://arxiv.org/abs/2607.03316) | abstract only | observational study | preprint | borrow ideas | The abstract reports 56% of CodeRabbit comments rejected (paper-reported) |
| [Quantifying Overclaiming Propensity](https://arxiv.org/abs/2609.20812) | abstract only | experiment | preprint | borrow ideas | The abstract reports agents claiming work they didn't do (paper-reported) |
| [ActPlane](https://arxiv.org/abs/2606.25189) | abstract only | untested proposal | preprint | borrow ideas | The abstract argues tool-call guardrails miss actions that bypass the tool layer (paper-reported) |
| [The EPIC Framework for SDD](https://arxiv.org/abs/2610.07534) | abstract only | observational study | preprint | borrow ideas | The abstract reports 40 spec-quality practices from ISO/IEC/IEEE 29148 (paper-reported) |
| [Negative Effect of LLMs on Requirements Inspection](https://arxiv.org/abs/2608.21298) | read in full | experiment | preprint | borrow ideas | Reports a crossover experiment: 34 students inspected simplified requirement documents with and without ChatGPT. <ul><li>Defect-detection F1 was about 8% lower with the LLM, but the credible intervals overlap.</li><li>The LLM had no effect on judging severity or on time.</li><li>Students who started with the LLM improved about half as much between sessions.</li><li>The authors advise using an LLM only after a manual pass.</li></ul>It doesn't measure an autonomous reviewer's recall (paper-reported) |
| [TDD-Agent](https://arxiv.org/abs/2608.16742) | read in full | experiment | peer-reviewed (EMNLP 2026) | borrow ideas | Reports tests written first adding only 0.6-2.9 points; most of the gain came from iterating on execution feedback while both tests and code could change (up to +17.1 points). It has no arm that writes code first and then iterates (paper-reported) |
| [Enforcing a Software Lifecycle Around an AI Coding Agent](https://doi.org/10.2139/ssrn.7675938) | read in full | weak experiment | unreviewed report | borrow ideas | Reports, for a proprietary Claude Code lifecycle plugin with n of 1-3 per cell: <ul><li>A text-level hook guard alone let 8 of the 8 attacks that ran breach. Claude Code's OS sandbox profile held all 11, with or without the guard. Every obfuscation class tried got past the text filter.</li><li>A crashing hook fails open, so any exception inside a guard should deny.</li><li>Review loops didn't converge on their own; a round cap bounds them without ending the churn, and review was 40-50% of a run's cost.</li><li>A second-vendor reviewer caught a defect two same-vendor reviewers passed.</li><li>Orchestration cost 4-8 times more on large tasks, with no gain on small or medium ones.</li></ul>(paper-reported; no artifact released) |

About 50 more papers on secondary topics were read as abstracts and classed **borrow ideas** or **reject**. None changed a class or the verdict, and they aren't listed here.

## Worth retrieving manually

None.

## Coverage ledger

Five snowball rounds; per route, all rounds combined:

| Route | State | Queries or reason |
|---|---|---|
| The stack itself | searched | LID 1.4.0 skill; `lidc` 0.3.0 binary strings; `.claude/settings.json`; `apm.yml`; Claude Code docs |
| Earlier notes and decisions | searched | No `docs/decisions/`; [2026-11-05 leads from source calibration](2026-11-05-leads-from-source-calibration.md); [2026-11-06 federated knowledge and work items](2026-11-06-federated-knowledge-and-work-items.md); `docs/process-lessons.md:18` |
| GitHub repository search | searched | About 200 queries, e.g. "spec driven development", "tdd hooks claude", "write gate", "review convergence"; star-sorted mechanism queries in round 5 |
| GitHub topics | searched | About 45 queries, e.g. `topic:spec-driven-development topic:claude-code`, `topic:claude-code-hooks gate` |
| GitHub code search | searched | About 35 queries, e.g. `"tdd" filename:marketplace.json path:.claude-plugin`, `PreToolUse phase filename:hooks.json`; not used in round 5, whose seeds were followed by links |
| GitLab | searched | "spec-driven development", "claude code hooks", "requirements traceability" |
| Codeberg | unavailable | HTTP 429 after one retry in rounds 1, 3 and 4; not retried in rounds 2 and 5 |
| npm | searched | About 150 queries, e.g. "spec driven claude code", "definition of done agent", "stop hook claude" |
| PyPI | searched | Site searches, e.g. "spec-driven development claude code", "claude code stop hook evidence gate", "conventional commits linter pre-commit"; JSON lookups for known names |
| crates.io | searched | About 60 queries, e.g. "spec-driven", "conventional commits", "commit lint" |
| Language registries (Go, NuGet) | searched | pkg.go.dev: "spec driven development", "requirements traceability", "claude code hooks"; NuGet lookups in round 4 |
| libraries.io | searched | About 40 queries, e.g. "spec-driven-development", "evidence gate", "spec drift"; its dependents endpoint was disabled ("Disabled for performance reasons") |
| Homebrew formulae | searched | Local `jq` over formula.json for "spec-driven", "traceab", "tdd", "code review", "commitlint" and similar |
| nixpkgs | excluded | Condition unmet: no brotli decompressor installed |
| LibHunt | searched | Alternatives pages for spec-kit, OpenSpec, tdd-guard and two more |
| AUR | searched | "spec-kit", "openspec", "claude-code" and 5 more |
| ecosyste.ms | searched | Keywords spec-driven-development, claude-code-hooks, tdd-guard |
| Cross-language equivalents | searched | "superpowers alternative claude code plugin", "alternatives to Kiro IDE spec workflow for Claude Code" |
| Awesome lists | searched | About 35 lists, including hesreallyhim/awesome-claude-code, Engineering4AI/awesome-spec-driven-development, walkinglabs/awesome-harness-engineering, and the Spec Kit community catalog (194 extensions) |
| alternativeto.net | searched (via web search) | "alternatives to GitHub Spec Kit", "alternatives to BMAD method", "alternatives to Taskmaster"; the site wasn't fetched (Cloudflare) |
| General web search | searched | About 120 queries, e.g. "spec-kit vs openspec vs kiro", "AI code review agent loop stopping rule diminishing returns", practitioner write-ups of each framework |
| Hosted services | searched | Kiro, Tessl, Copilot, Cursor, CodeRabbit, Codex and others; Claude Code features |
| Skill directories | searched | skills.sh, e.g. "spec-driven", "ears requirements", "definition of done", "review converge"; other directories via web search |
| Claude Code plugin marketplaces | searched | Anthropic's marketplace file (317 plugins), filtered for spec, tdd, review, workflow, commit, hook and guard |
| MCP Registry | searched | One-word queries: "spec", "traceability", "tdd", "drift", "review-loop" |
| PulseMCP | excluded | Its robots.txt disallows ClaudeBot |
| Anthropic's skills repo | searched | Contents listing; nothing on the need |
| aitoolnet.com | searched | Sitemap slug grep for spec, kiro, tessl, code-review, tdd, workflow, bmad; 12 tool pages |
| arXiv | searched | `abs:"spec-driven development"`; `abs:specification AND abs:"coding agent" AND abs:requirements`; `abs:EARS AND abs:requirements AND abs:LLM` |
| OpenAlex | searched | "spec-driven development LLM coding agents", "requirements traceability large language model code generation tests", "multi-agent LLM code review false positives"; snowballed through citations in both directions |
| OpenAIRE | searched | `"spec-driven development" agents`, `"coding agent" guardrails lifecycle`, `"code review" "multi-agent" LLM` |
| papers.cool | searched | "spec-driven development", "agentic code review false positives", "coding agent test-driven development enforce" |
| Hugging Face papers | searched | "spec-driven development coding agents", "multi-agent code review", "test-driven development coding agent" |
| Crossref | searched | "spec-driven development AI coding agents", "enforcing software lifecycle AI coding agent guardrails", "multi-agent LLM code review" |
| Semantic Scholar | unavailable | HTTP 429 with the key set, on three attempts; substitute OpenAlex searched |
| Zenodo | excluded | Its robots.txt disallows `/api` |
| Europe PMC | excluded | The need has no science-domain aspect |
| Venue program pages | excluded | The venue papers found were already indexed with abstracts |

## Snowball rounds

| Round | Seeds | New serious | With a novel mechanism | Examples that reached the candidates table |
|---|---|---|---|---|
| 1 | need and seeds | ~160 | not tagged | Probity, judicata, DAW, review-convergence, Spec Kit, BMAD |
| 2 | round 1's serious candidates | ~100 | not tagged | srs-dd, Spec Engine, foreman |
| 3 | round 2's serious candidates | 111 | 43 | claimcheck, red-first-gate, ringi-gate, Habeas Codicem, git-sumi |
| 4 | round 3's serious candidates | 139 | 24 | craftsman, musthold, a2dlc, cairn, disensor, agentops |
| 5 | the serious, novel candidates of rounds 3 and 4 | 16 | 16 | none read in source (qikly, letspecify and sawbuck at README depth) |

In all, 963 unique candidates, 520 of them serious, and 71 read in source.

**The search stopped at round 5 without meeting the skill's stopping rule.** Every round, round 5 included, added serious candidates, and the round-10 cap wasn't reached. The field is saturated with small, recent Claude Code plugins.

With the developer's approval, round 5 used a narrower rule. Its seeds were only the round 3 and 4 candidates with a new mechanism, and a candidate counted only if its mechanism was new **and** it showed diamond signals: rationale, evals, measurement or adoption. Under that rule, a follow-up pass on each route, searching from the round's own new candidates, added none. The narrower rule is proposed for [#159](https://github.com/jmbowman/agentic_development/issues/159).

Open leads, unread:
- about 135 filtered GitHub hits and 553 zero-star hits from round 4;
- the long tail of test-tampering detectors;
- pr-shepherd (no link found; 344k downloads a month; close to a known mechanism);
- Thoughtworks Radar blips not opened;
- PBT-Bench (arXiv 2605.15229) and SlopCodeBench (arXiv 2603.24755), read from summaries only.

### Out of scope: leads for [#167](https://github.com/jmbowman/agentic_development/issues/167) (task files and work queues)

These were noted and not chased:
- [kanban-md](https://github.com/antopolskiy/kanban-md): task `.md` files with YAML frontmatter and an atomic `pick --claim`;
- [Backlog.md](https://github.com/MrLesk/Backlog.md);
- [sako](https://github.com/Thakay/sako);
- [Spec Kitty lanes](https://priivacy-ai.github.io/spec-kitty/explanation/kanban-workflow.html);
- [rtmx](https://github.com/rtmx-ai/rtmx);
- [railwarden](https://github.com/advaith-1212/railwarden);
- [beads](https://github.com/gastownhall/beads);
- [agent-task-queue](https://github.com/block/agent-task-queue);
- [claude-task-master](https://github.com/eyaltoledano/claude-task-master): Commons Clause per npm metadata;
- [sprint.md](https://github.com/jnun/sprint.md);
- [specweave](https://www.npmjs.com/package/specweave);
- [Building a C compiler with 16 agents](https://www.anthropic.com/engineering/building-c-compiler): claiming tasks with lock files;
- papers: [Claim Plane](https://arxiv.org/abs/2607.21909), [An Exploratory Study of Agent Plans](https://arxiv.org/abs/2608.04661), [LoopsBench](https://doi.org/10.48550/arxiv.2608.00267), [AgenticFlict](https://doi.org/10.1145/3805760.3814923).

## Refresh trigger

Search again for a component before its HLD or LLD update is finalized, if more than three months have passed (after 2027-02-09). Also search again when any of these happens:
- LID ships hooks or mechanical gates;
- `lidc` adds proof results or staleness per spec;
- craftsman's hooks fail closed;
- musthold's second loop reports;
- Claude Code changes how hooks fail, or starts installing repo-declared plugins in cloud sessions.
