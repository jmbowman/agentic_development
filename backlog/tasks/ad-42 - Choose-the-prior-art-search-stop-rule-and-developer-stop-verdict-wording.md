---
id: AD-42
title: Choose the prior-art-search stop rule and developer-stop verdict wording
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
  - issue
milestone: m-3
dependencies: []
references:
  - https://github.com/jmbowman/agentic_development/issues/260
  - https://github.com/jmbowman/agentic_development/issues/159
  - skills/prior-art-search/SKILL.md:84
  - skills/prior-art-search/SKILL.md:172
priority: high
type: decision
performer: human
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
SKILL.md step 6 stops when a round adds no new serious candidate, which never fires in crowded fields (issues #159, #260). Proposals on the table: (a) #260: stop when no find in two consecutive rounds changes the verdict or shortlist, reported separately from the cap with open leads listed; (b) #159: tag each find (could change verdict, could change shortlist, improves a custom piece, borrow ideas, variant) and apply the rule per route kind, software vs literature; (c) the #98 evidence: a find counts only if it has a new mechanism plus evidence of depth, and an untagged find must not end the search until the candidates it would displace were read in source; (d) allow seeding from novel candidates of any earlier round. Also decide how the verdict reads when the developer stops after convergence (keep the converged verdict, state the stop and open leads) versus before convergence (inconclusive). Done means the developer picks one reading of each so the build item can proceed.

**Why it matters:** Unblocks cheaper prior-art searches: the cross-repo search spent about 5.3M subagent tokens past convergence.

**Why the developer:** chooses between competing readings of the stop rule and verdict semantics
<!-- SECTION:DESCRIPTION:END -->
