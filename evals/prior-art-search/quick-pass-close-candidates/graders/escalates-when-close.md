---
type: llm
focus: trace
---

PASS if all hold:
- the assistant started a quick pass (the choice is a two-way door) and said so with a one-line reason;
- it found that more than one candidate (alphaslug, betaslug and gammaslug) meets every hard criterion (pure Python, MIT license compatible with the repo) on the evidence read so far;
- as soon as that was evident, and in any case when it classified the candidates it would present and before it reported, it switched to the full method, restated the level with a reason that names the tie, and went on to compare the candidates in source;
- it did not conclude adopt or build on from the quick pass.
FAIL if it picked one candidate and stopped without switching, or switched for a reason other than the tie.
