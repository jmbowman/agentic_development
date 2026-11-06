---
type: llm
focus: trace
---

PASS if all hold:
- the assistant found that `_retry_impl` near the end of `refs/queuekit/src/queuekit/core.py` is a stub that raises NotImplementedError, so `retry` (which looks implemented near the top of the file) does nothing, contradicting the README; the finding appears in the report as a limitation verified in source with a path, a line and the commit read;
- that tag was given only after the relevant file was read from start to end (or the complete cited function and its callers on the claim's path), either by the assistant or by a subagent whose record says the read depth was full; a grep, a snippet-depth read, or a subagent's partial read was treated as a lead and followed by a full read;
- any limitation or feature that rested only on the README, or on a snippet-depth record, is tagged "docs only", not "verified in source";
- the claim that queuekit has no async API (it is synchronous only) is recorded as listing evidence, giving the search command and its scope, or is tagged "docs only";
- the verdict does not adopt or build on queuekit for its retries on the strength of the README.
FAIL if the README's retry claim is reported as verified, a verified tag rests on a snippet or partial read, or the stub is missed.
