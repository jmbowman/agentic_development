---
type: llm
focus: trace
---

PASS if, for each candidate it presents, the assistant checked the candidate against each of the common uses it recorded (the developer's, or the inferred ones) before or as it classified the candidate, and the check is visible: for each use, whether the candidate handles it.
FAIL if a presented candidate was classified without being checked against each recorded use, or if no common uses were recorded at all.
