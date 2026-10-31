# Process lessons

Lessons about this repo's development process, drawn from building its skills, for the process components the HLD plans (review-wave orchestration, the spec-review loop). The numbers behind them are in [the review log](review-log.md).

## Slices and specs

- **Specs grow in review.** A slice estimated before the EARS coverage review can double: coverage gaps and edge-audit forks add specs. Count a slice's specs after that review, and re-cut it if it passes about 40.
- **Spikes before EARS pay off.** Running the platform behaviors a design depends on (memory paths, session listing, the eval runner) removes wrong assumptions before any spec is written. Record the results as facts in the LLD.

## Review and evals

- **Evals find what review waves don't.** After six review waves on session-wrap-up's first slice, eval runs still found 8 skill-text misses and 9 grader or prompt faults. Run a skill's evals before its slice is committed.
- **Know when to stop reviewing.** Yield fell from 40 to 12 to 5 to 5 findings across one slice's code-review waves. Two narrow re-checks after the main wave were the useful stopping point.

## Approval steps

- **Put the text inside the question.** A question dialog can hide the conversation above it, so an approval step that asks through a question tool puts the exact text in the question itself (for example, in each option's preview).
- **Keep each preview short enough to show whole.** A long preview is cropped ("8 lines hidden"), hiding exactly the text being approved. Give each item its own question (a question tool can ask several at once), so each preview holds one item's text.
- **Every option shows the text it would apply.** An option that applies only part of a change ("only item 4") previews that part. One with no preview leaves the developer approving text they can't see.

These apply to session-wrap-up's approval gate in its third slice.
