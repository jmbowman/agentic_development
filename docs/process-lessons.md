# Process lessons

Lessons about this repo's development process, drawn from building its skills, for the process components the HLD plans (review-wave orchestration, the spec-review loop). The numbers behind them are in [the review log](review-log.md).

## Slices and specs

- **Specs grow in review.** A slice estimated before the EARS coverage review can double or more (session-wrap-up's second slice went from 8 specs to 38): coverage gaps and edge-audit forks add specs. Count a slice's specs after that review, and re-cut it if it passes about 40.
- **Spikes before EARS pay off.** Running the platform behaviors a design depends on (memory paths, session listing, the eval runner) removes wrong assumptions before any spec is written. Record the results as facts in the LLD.

## Review and evals

- **Evals find what review waves don't.** After six review waves on session-wrap-up's first slice, eval runs still found 8 skill-text misses and 9 grader or prompt faults. Run a skill's evals before its slice is committed.
- **Trial the riskiest cases first.** Run a new suite's riskiest cases on the real model before the full set. For session-wrap-up's second slice, two cases cost $0.37 and found four faults.
- **Run the whole suite when a report gains a section.** Session-wrap-up's slice 3a passed its new cases, then the full suite failed seven more: the new state check exposed scaffolds that didn't match their records, and the new section gave the agent room to invent follow-ups.
- **Put an output rule in the output's template.** In session-wrap-up's slice 3b, rules stated in a step's text kept slipping, even after rewording. Moved into the report template's placeholder lines, which the agent copies as it writes, they mostly held.
- **Set a last round before starting it.** Once each remaining miss was down to one run in three, a final round was named in advance, and what still slipped was logged with its rate instead of starting another round.
- **Re-run a surprise before diagnosing it.** Two of three single failures passed twice on re-run. The third failed again, and was a real trigger gap.
- **Know when to stop reviewing.** Yield fell from 40 to 12 to 5 to 5 findings across one slice's code-review waves. Two narrow re-checks after the main wave were the useful stopping point.
- **State each value once.** A value written in two places drifts: a re-check found OpenAIRE's rate limit given as 7,000 in a route table and 7,200 in the same file's rate-limit section, a day after both were written. Keep it in one place and point to it.

## Approval steps

- **Put the text inside the question.** A question dialog can hide the conversation above it, so an approval step that asks through a question tool puts the exact text in the question itself (for example, in each option's preview).
- **Keep each preview short enough to show whole.** A long preview is cropped ("8 lines hidden"), hiding exactly the text being approved. Give each item its own question (a question tool can ask several at once), so each preview holds one item's text.
- **Every option shows the text it would apply.** An option that applies only part of a change ("only item 4") previews that part. One with no preview leaves the developer approving text they can't see.

These apply to session-wrap-up's approval gate in slice 3b.

## Research and sources

- **Check a source's terms and live behavior before recommending it.** Read the service's terms and robots.txt, and probe it, before a route goes into a skill. A first probe recommended Arch's package search, which its robots.txt disallows, and rated OpenAlex the primary paper route a day before its anonymous search was paused under load.
