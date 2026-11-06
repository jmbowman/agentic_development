---
type: llm
focus: trace
---

PASS if all hold:
- the assistant started a quick pass (the choice is a two-way door) and said so with a one-line reason;
- it noticed that the best candidate (mdlinks) leaves a core requirement unmet (it doesn't run on Windows, and the requirement allows no exceptions) and that no other candidate covers it (anchorcheck runs everywhere but doesn't check external links);
- as soon as that was evident, and in any case when it classified the candidates it would present and before it reported, it switched to the full method and restated the level with a reason that names the gap;
- it did not give the verdict adopt or build on from the quick pass;
- after the switch it searched, or gave a reason tied to the need for, each route it had excluded only for the reason "quick pass" (with the network down, a route may end unavailable).
FAIL if it concluded adopt or build on mdlinks without switching, or called the Windows gap a small extension.
