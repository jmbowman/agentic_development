---
node: high-level-design
---

# Decision: When review waves stop

## Context

Every slice, spec change and prior-art note here clears a review wave before it is committed: parallel reviewers, each with a lens, followed by triage that verifies each finding and drops what isn't worth its cost. The question is what happens after a wave's fixes are applied: whether another wave runs, what it looks at, and what ends the loop.

Both ways of getting this wrong are costly. Stopping early ships defects that the next wave would have caught: in this repo, fresh reviewers of a fixed change regularly report several findings each on the *original* change, over half of them worth fixing [dev: the developer's observation from running review waves; not yet counted]. Stopping late wastes tokens and the developer's attention: one project found that a reviewer asked to find problems finds one every time (agentops, in the process synthesis's open questions), a same-reviewer second round cut F1 from 0.376 to 0.303 because it invented findings once the real errors ran out [P: arXiv 2603.16244], and an uncapped loop ran 87 rounds in one case [P: arXiv 2610.08900]. Neither way catches everything: after six waves on one skill, evals still found 8 skill-text misses ([process lessons](../process-lessons.md)). The evidence is gathered in the [process synthesis](../prior-art/2026-11-10-agentic-development-process-synthesis.md) (stages 9 and 10, and Decision 1 of its open questions).

## Decision Elements

- **Defects caught before commit** (major). A defect a later wave would have found costs more once committed: it reaches consumers, or is found by an eval or the developer instead.
- **Resistance to invented findings** (major). The loop must not reward a reviewer for reporting something, or it never ends and fills the log with noise.
- **Bounded cost and churn** (moderate). Each wave costs tokens and time, and a fix can introduce a regression that needs its own wave. The loop needs a way to notice when it isn't converging.
- **Developer attention** (moderate). The developer reads the result and rules on forks; they should see a loop only when it needs them.
- **Data to tune from** (minor). Whatever rule is chosen, its thresholds are untested, so each wave should leave the counts needed to revisit it.

## Options in the Domain

### Coded stop rule over a ledger

One wide wave per phase. A further pass runs only when a verified high-severity finding was fixed, or a fix rewrote a large share of the artifact; that pass reviews only the fix diff and what references it. At most three passes. Findings on untouched text are tagged pre-existing and don't trigger a pass. The rule is a function over a review ledger, so a gate can re-check it. This is the shape of craftsman's planner and BMAD's prose rule, and of a vendor report's three-round cap with diff-only re-review [X: Anthropic, "Solving code review"]. That report credits the cap, diff-only re-review and not repeating findings with raising first-round passes from 65% to 78%, the most direct outside evidence for this option; on one slice here, two narrow re-checks after the main wave were the useful stopping point ([process lessons](../process-lessons.md)).

- **Defects caught: weak.** Later passes never look at unchanged text, so the defects that fresh reviewers find in the original change after the obvious ones are fixed are never looked for, and a pass runs only after a high-severity fix or a large rewrite.
- **Invented findings: strong.** Nothing a reviewer reports can extend the loop beyond the computed rule.
- **Cost and churn: strong.** At most three passes, each narrow.
- **Developer attention: strong.** The loop runs without them.
- **Data: strong.** The ledger records everything the rule reads.

*Summary:* cheap and predictable, at the price of a known blind spot in the original change.

### The same reviewers iterate until a wave reports nothing

Reviewers re-check the revised artifact (resumed, or told what changed) until a wave reports no findings.

- **Defects caught: partial.** Reviewers who keep their earlier context keep their earlier blind spots.
- **Invented findings: weak.** Zero findings as the exit condition pressures reviewers to report something; BMAD removed such a halt for that reason, and the same-reviewer F1 drop above measured its mechanism, a second review by the same reviewer.
- **Cost and churn: weak.** No cap and no churn check.
- **Developer attention: partial.** Runs alone until it doesn't stop.
- **Data: weak.** Nothing to tell real findings from invented ones.

### Fresh full-scope waves until triage accepts nothing worth fixing

Each wave uses fresh reviewers on the whole change as it now stands, fixes included, not only the fix diff. Reviewers are told that reporting nothing is a good outcome, and not to report anything that costs more to fix than it's worth for the artifact's intended uses. They also get the findings earlier triage *rejected*, with the reason, and those it recorded as backlog tasks, with the task ID, so those aren't raised again; findings accepted for fixing aren't listed, so the reviewers aren't anchored on what was already fixed. After each wave a triage agent separate from the reviewers and from the agent that made the change, given the intended uses, sorts each finding as fix now, record as a backlog task, or not worth it in this project, and tags each accepted finding that the previous wave's fixes caused. Here a finding is *accepted* when triage sorts it fix now; one recorded as a backlog task is *deferred*. Its ruling is final, except that a finding which chooses between two readings of intent goes to the developer as a fork. When triage accepts any finding for fixing, the fixes are applied and another wave runs, since even a small fix can introduce a significant regression; triage keeps that bar meaningful by not accepting wording tweaks or trivial smells that aren't worth a wave. Findings triage rejects or defers are not applied in this loop; a deferred one is fixed through its task, so the tree the last wave reviewed is the one that ships. The loop stops at the first wave whose triage accepts nothing to fix now, once no fork is waiting on the developer; a fork the developer rules fix-now counts as an accepted finding, so another wave follows its fix.

The loop escalates to the developer instead of starting a sixth wave, or when at least two of a wave's accepted findings, and more than 30% of them, were caused by the previous wave's fixes: later waves are then mostly finding regressions the fixes introduced, a sign that patching isn't converging. A finding is fix-caused only when a fix introduced the defect; a ruling that wasn't carried into every file that restates it is an ordinary finding. On either trigger, the loop escalates with that wave's accepted findings unapplied, so the developer decides whether to patch, rework or stop. If the developer chooses to patch or rework, waves resume and the count restarts from that ruling: the escalation is itself the developer's review of where the loop stands, which is one purpose of the wave limit.

- **Defects caught: strong.** Each wave is an independent sample over the whole change, which is what finds the defects earlier waves missed; independent parallel reviews outperformed repeated review in the same study that measured the F1 drop. Within one review, though, two reviewers with findings pooled did not beat one beyond noise [P: arXiv 2608.18167], so width alone is not the gain. Neither study measured fresh waves after fixes: the case that later full-scope waves find defects earlier ones missed rests on the observation in Context.
- **Invented findings: partial.** A reviewer can still pad a report, but padding can't extend the loop: only triage's acceptance of a fix can, and the triage agent judges value, not volume. The list of rejected and deferred findings stops repeated ones.
- **Cost and churn: partial.** More waves than the coded rule on most changes, and wider review has reached similar accuracy to more rounds at lower cost [P: arXiv 2610.34577], which favours the coded rule's single wide wave. The escalation triggers bound a loop that isn't converging, but both thresholds are guesses.
- **Developer attention: strong.** The loop runs alone and reaches the developer only for forks and escalations.
- **Data: strong**, if each wave's review-log row records the wave number and the counts of findings raised, accepted, deferred to the backlog and rejected, and how many accepted findings the previous wave's fixes caused.

*Summary:* more waves for more caught defects, with triage rather than a formula deciding when value has run out.

## Selection

**Fresh full-scope waves until triage accepts nothing worth fixing.** It is the only option strong on defects caught, the major criterion where the other two fall short, and its weakness on invented findings is contained by making triage, not the reviewers, the only path to another wave. The costs it accepts over the coded rule: more waves per change, a stop that is a judgment rather than a computed value, escalation thresholds that start as guesses, and a choice against the vendor report's evidence for a capped, diff-only rule and a paper's finding that wider review matched more rounds at lower cost, resting on the developer's observation that full-scope later waves find defects in the original change.

Tenet 10 (compute what can be derived; store only facts and rulings) cuts both ways here: the stop is a triage *ruling*, which is stored rather than computed, while the escalation triggers are derivable from the recorded counts and can be computed once the review ledger exists.

What it forecloses: diff-only re-review as the general rule for review waves, and a fixed cap of three. A narrower check is still fine between waves, such as an implementer's re-check of its own fix before the next wave; it is not a wave, so it neither counts toward the five-wave escalation nor replaces a full-scope wave.

What it obligates:
- the review procedure and reviewer briefs say that reporting nothing is acceptable, carry the rejected and deferred findings, and run triage as a separate agent given the artifact's intended uses;
- the review log records the per-wave counts listed above, and the review ledger generates them once built;
- the escalation thresholds (five waves; at least two and over 30% fix-caused, where the 30% comes from deep-review-loop, unmeasured there too) are revisited once the log has enough waves to judge them;
- the HLD's "review waves until convergence" means this loop.
