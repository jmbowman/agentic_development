---
title: Add diff-scoped mutation testing as a reviewer signal in copier-python
status: To Do
assignee: []
created_date: '2026-11-16'
labels:
- prior-art
references:
- docs/prior-art/2026-10-27-review-and-comprehension-burden.md#Verdict
- https://github.com/jmbowman/agentic_development/issues/90
priority: medium
type: feature
performer: agent
agent_tier: strong
effort: L
priority_set_by: agent
target: github.com/jmbowman/copier-python
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Mutate only the changed lines, cap mutants per line, and show only survivors (Google's pattern, Petrovic et al. 2021), using cosmic-ray because copier-python runs its code under test in subprocesses where mutmut cannot record which tests reach a mutant. Mull is the later choice for PortaBase (needs a Clang build). Done when a slice's review output lists surviving mutants on changed lines. Depends on #89's evaluation of musthold for the shared per-test kill data.

**Why it matters:** Strongest signal on whether new tests would catch a break.

**Why an agent:** Tool integration after evaluation

**Also waits on (not tracked as a task):** #89 musthold evaluation

**Filed by:** an agent session in agentic_development, 2026-11-16. The receiving repo sets its id and priority.
<!-- SECTION:DESCRIPTION:END -->
