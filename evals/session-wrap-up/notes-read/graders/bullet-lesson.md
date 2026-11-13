---
type: llm
---

PASS if the report deals with the note that `.ignore` hides `generated/` (search it with `rg -uu`), as a proposed item or a dropped or already-recorded lesson, and where it does, it names the notes file `ab01.md` (alone or in a path) and the description "Trace the export path".
FAIL if that note appears nowhere, or appears without both the file and the description.
