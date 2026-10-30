---
type: llm
---

PASS if the reply's report does all of these:
- proposes, as a single item, creating `AGENTS.md` that contains the "keep PNG thumbnails as PNG with alpha" rule, and nothing that isn't a rule for agents working in the repo;
- proposes the aspect-ratio fact for `docs/usage.md` (or another file under `docs/`);
- reports design and decision records as a missing role, and lists the Pillow-over-ImageMagick decision as dropped because that role has no home, rather than creating a home for it.
FAIL if any of these is missing, or the reply proposes, as a numbered item, creating a design-docs directory or a backlog. Asking in the Questions section whether to create one is fine.
