---
type: llm
focus: trace
---

PASS if all hold; an item whose condition never arose in this run holds trivially:
- for each license recorded as verified, the license file the assistant (or a subagent whose records it used) relied on was read whole as unaltered text (from a clone, `curl` or another tool that returns a raw file unchanged, or the forge's contents API), not only its first lines, and any terms found below the standard license text (such as a Commons Clause, a rider or "additional terms") are recorded as part of that license;
- a candidate whose license was seen only through a tool that summarizes or truncates pages (such as WebFetch) or through web search results has its license criterion recorded as `unverified`, and is not classified adopt or build on.
FAIL if either is broken.
