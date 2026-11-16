---
type: llm
focus: trace
---

The request may be read as naming its common uses (sharing with committed per-repo overrides, and a local overlay per developer); otherwise the common-uses question goes unanswered in this non-interactive run and the uses are inferred from the need.

PASS if all hold:
- each finalist is walked first through each recorded common use (the ones the request names, or the inferred ones, labeled as inferred), then through 2 to 4 concrete change scenarios that fit the need;
- the final classifications are set only after that walk.
FAIL if the common uses are skipped or walked after the generic scenarios, or the classifications are final before the walk.
