# Review log

The yield and cost of each review wave, so that the point of diminishing returns can be judged from data. The agent that runs a wave adds its row when it has triaged the findings. Rows are in the order the waves ran.

*Found* counts findings after removing duplicates. *Applied* counts those acted on. *Forks* counts those put to the developer as a choice between readings. *Wrong* counts findings that failed verification against the text or its sources. Tokens and time are the reviewing subagents' totals; parallel reviewers' times are not added. For eval rows, the cost column is the runner's reported dollars instead of tokens.

| Date | Component | Phase | Wave | Lenses | Found | Applied | Forks | Wrong | Tokens | Time |
|---|---|---|---|---|---|---|---|---|---|---|
| 2026-10-29 | session-wrap-up | LLD | 1 | gap probe; fact-check, cold read, fit, audience, edge firing, human review | 25 | 23 | 2 | 0 | 155k | 1.6 min |
| 2026-10-29 | session-wrap-up | LLD | 2 | re-check: contradictions, edge firing, two readings, support, audience | 12 | 12 | 0 | 0 | 72k | 1.0 min |
| 2026-10-30 | session-wrap-up | EARS | 1 | coverage, rung mismatch, contradiction, implicit scope, context-free reading, EARS form, testability | 20 | 17 | 3 | 0 | 66k | 1.8 min |
| 2026-10-30 | session-wrap-up | Edge audit | 1 | two blind divergence probes (spec text only); compositional audit | 32 | 18 | 14 | 0 | 173k | 2.1 min |
| 2026-10-30 | session-wrap-up | Slice 1 code | 1 | tests and graders (spec fit, discrimination, fact-check); skill text (spec fit, cold read, edge firing, portability, placement); audience, human review, fact-check, fit, logic placement | 30 | 30 | 0 | 0 | 251k | 2.2 min |
| 2026-10-30 | session-wrap-up | Slice 1 code | 2 | re-check: spec fit, grader discrimination, cold read, human review, audience | 5 | 5 | 0 | 0 | 87k | 2.3 min |
| 2026-10-30 | session-wrap-up | Slice 1 code | 3 | narrow re-check of the changed graders and prompts | 5 | 5 | 0 | 0 | 59k | 1.6 min |
| 2026-10-30 | session-wrap-up | Slice 1 evals | 1 | `claude plugin eval` runs (Haiku 5.5 smoke runs; Sonnet 5.5 agent and judge, with and without the plugin); 8 skill-text misses, 9 grader or prompt faults | 17 | 17 | 0 | 0 | $6.60 | 72 min |
