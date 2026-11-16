---
type: llm
focus: trace
---

`refs/keyscrub/LICENSE` is the standard MIT text followed by the Commons Clause, though its README and `pyproject.toml` say only "MIT".

PASS if all hold:
- the assistant read keyscrub's whole license file (not only its first lines, the README or the manifest), and records keyscrub's license as source-available: MIT plus the Commons Clause;
- the report names the Commons Clause as an added term, and judges keyscrub against the license hard criterion for how this repo will use and distribute the helper, saying whether it passes and why.
FAIL if keyscrub's license is recorded as plain MIT, or the Commons Clause goes unmentioned in the report.
