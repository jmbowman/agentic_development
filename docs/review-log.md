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
| 2026-10-30 | session-wrap-up | Slice 2 EARS and edge audit | 1 | spec review (coverage, rung, contradiction, scope, EARS form, testability); two blind divergence probes; compositional audit | 22 | 11 | 11 | 0 | 216k | 3.8 min |
| 2026-10-31 | session-wrap-up | Slice 2 EARS and edge audit | 2 | re-check of the revised specs: rung, contradiction, two readings, cold read, eval verifiability | 8 | 3 | 5 | 0 | 76k | 3.0 min |
| 2026-10-31 | session-wrap-up | Slice 2 EARS and edge audit | 3 | narrow re-check: contradictions, two readings, design behavior with no spec | 5 | 3 | 2 | 0 | 66k | 1.9 min |
| 2026-10-31 | session-wrap-up | Slice 2 code | 1 | skill text (spec fit, cold read, edge firing, portability, placement); tests and graders (discrimination, fact-check); human review, audience | 32 | 29 | 3 | 0 | 310k | 4.5 min |
| 2026-10-31 | session-wrap-up | Slice 2 code | 2 | narrow re-check of the fork fixes: spec fit, grader discrimination, slice 1 regressions | 3 | 2 | 1 | 0 | 104k | 2.4 min |
| 2026-11-01 | session-wrap-up | Slice 2 evals | 1 | `claude plugin eval` runs (Sonnet 5.5 agent and judge, one run each, no baseline arm); 7 skill-text misses, 2 grader or prompt faults | 9 | 9 | 0 | 0 | $1.87 | 8 min |
| 2026-11-01 | session-wrap-up | Slice 2 evals | 2 | `claude plugin eval` re-runs of the fixed cases and the rest of slice 1; privacy three times; 1 skill-text miss, 2 grader or prompt faults | 3 | 3 | 0 | 0 | $1.24 | 11 min |
| 2026-11-01 | session-wrap-up | Slice 2 evals | 3 | `claude plugin eval` re-runs of the two remaining cases, twice each; 1 grader fault | 1 | 1 | 0 | 0 | $0.46 | 2 min |
| 2026-11-01 | session-wrap-up | Slice 3 edge audit | 1 | two blind divergence probes (spec text only); compositional audit | 24 | 11 | 13 | 0 | 154k | 2.5 min |
| 2026-11-01 | session-wrap-up | Slice 3 EARS | 1 | spec review of the revised design and specs: coverage, contradiction, implicit scope, cold read, testability, tenets, terms | 16 | 12 | 4 | 0 | 80k | 2.9 min |
| 2026-11-01 | session-wrap-up | Slice 3 EARS | 2 | narrow re-check after the slice split: contradictions, uncovered design, two readings | 6 | 6 | 0 | 0 | 68k | 1.4 min |
| 2026-11-01 | session-wrap-up | Slice 3a code | 1 | spec fit, grader discrimination, slice 1 and 2 regressions, human review, public audience | 12 | 11 | 1 | 0 | 112k | 2.7 min |
| 2026-11-01 | session-wrap-up | Slice 3a evals | 1 | `claude plugin eval` trial of the two riskiest cases (Sonnet 5.5 agent and judge, one run each, no baseline arm); 2 skill-text misses, 1 grader or prompt fault | 3 | 3 | 0 | 0 | $0.28 | 1 min |
| 2026-11-01 | session-wrap-up | Slice 3a evals | 2 | `claude plugin eval` runs of 11 cases, new and most exposed; 5 skill-text misses, 2 grader or prompt faults, 1 failure diagnosed in the next wave | 8 | 7 | 0 | 0 | $1.16 | 6 min |
| 2026-11-01 | session-wrap-up | Slice 3a evals | 3 | `claude plugin eval` re-runs of the six failed cases; 1 skill-text miss, 2 case faults (one spec moved to a manual run: an eval can't run outside git) | 3 | 3 | 0 | 0 | $0.73 | 3 min |
| 2026-11-02 | session-wrap-up | Slice 3a evals | 4 | `claude plugin eval` full suite, one run per case; 3 skill-text misses, 1 case fault, 3 single failures in behavior this slice didn't change | 7 | 4 | 0 | 0 | $2.75 | 12 min |
| 2026-11-02 | session-wrap-up | Slice 3a evals | 5 | `claude plugin eval` re-runs of the seven failed cases, the three unexplained ones twice each; two passed both runs, and one was a real trigger gap | 1 | 1 | 0 | 0 | $1.15 | 5 min |
| 2026-11-02 | session-wrap-up | Slice 3a evals | 6 | `claude plugin eval` re-runs after the trigger fix; the skill fired three times of three; 1 skill-text miss (a required status line left out) | 1 | 1 | 0 | 0 | $0.36 | 1 min |
| 2026-11-02 | session-wrap-up | Slice 3b code | 1 | safety, spec fit, regressions, portability, human review of the skill and the manual scripts, public audience | 14 | 9 | 5 | 0 | 99k | 3.2 min |
| 2026-11-02 | session-wrap-up | Slice 3b evals | 1 | `claude plugin eval` full suite, one run per case; no safety regression; 4 skill-text misses, 1 grader fault, 3 single failures sent to re-runs | 8 | 5 | 0 | 0 | $2.97 | 13 min |
| 2026-11-02 | session-wrap-up | Slice 3b evals | 2 | `claude plugin eval` re-runs of seven cases, twice each; 2 skill-text misses (open items moved to the loose ends), 1 noisy grader split | 3 | 3 | 0 | 0 | $1.95 | 7 min |
| 2026-11-02 | session-wrap-up | Slice 3b evals | 3 | `claude plugin eval` re-runs of the three remaining cases; the split grader passed; 1 skill-text miss from the last fix, 1 fork on what a next-session prompt may say | 2 | 1 | 1 | 0 | $1.33 | 4 min |
| 2026-11-03 | session-wrap-up | Slice 3b evals | 4 | `claude plugin eval` re-runs after the fork's fix; three rules each slipped once in three runs, moved into the report template | 3 | 3 | 0 | 0 | $1.33 | 4 min |
| 2026-11-03 | session-wrap-up | Slice 3b evals | 5 | `claude plugin eval` final wording round, three runs each; the compaction rule held 3 of 3; an earlier dropped lesson returned 1 of 3 (`repeat-run`), and a dropped guess became a loose end 1 of 3 (`routes-by-house-rules`), both left at that rate | 2 | 0 | 0 | 0 | $1.52 | 5 min |
| 2026-11-05 | prior-art-search | Edge audit (papers, settings, links) | 1 | two blind divergence probes (spec text only); compositional audit | 25 | 25 | 11 | 0 | 144k | 1.1 min |
| 2026-11-05 | prior-art-search | Tests (papers, settings, links) | 1 | coverage and false passes; grader and fixture mechanics; ease of human review, scope and public-repo rules | 30 | 21 | 7 | 0 | 258k | 3.4 min |
| 2026-11-05 | prior-art-search | Skill text (papers, settings, links) | 1 | spec fit; cold read and edge firing; facts and public-repo hygiene | 26 | 21 | 4 | 1 | 196k | 2.1 min |
| 2026-11-05 | prior-art-search | Skill text (papers, settings, links) | 2 | re-check after forks, rate limits and user agent: spec fit, cold read, drift between files | 11 | 10 | 1 | 0 | 93k | 1.8 min |
| 2026-11-06 | prior-art note (federated knowledge and work items) | Note | 1 | fact-check against the search and verification records; skill and repo-rule conformance; cold read and reasoning | 55 | 50 | 5 | 0 | 359k | 5.0 min |
| 2026-11-06 | prior-art note (federated knowledge and work items) | Note | 2 | re-check after the forks and rewrite: consistency of the decisions, new errors against the records, link, license and matrix-source rules, cold read | 33 | 33 | 0 | 0 | 156k | 5.1 min |
| 2026-11-06 | prior-art note (decision records and LID) | Note | 1 | fact-check against the round-6 and verification records; skill and repo-rule conformance; cold read and reasoning, including tension with LID's template | 64 | 64 | 0 | 0 | 324k | 3.9 min |
| 2026-11-06 | prior-art note (agent reference clones) | Note | 1 | fact-check against the search and verification records; skill and repo-rule conformance; cold read and reasoning | 69 | 64 | 5 | 0 | 393k | 4.0 min |
| 2026-11-06 | prior-art note (agent reference clones) | Note | 2 | re-check after the forks and rounds 4-5: consistency of the decisions and cold read; new errors against the records, matrix sources, link and tag rules | 61 | 60 | 0 | 1 | 262k | 5.0 min |
