---
type: llm
---

PASS if all hold:
- the verdict is build or blend;
- the report records that hosted Renovate can't run `mise lock` as a post-upgrade task;
- it finds aquaproj's update-checksum-workflow (or the update-checksum action) as a pattern to borrow;
- the criteria list hard criteria first, including license compatibility with the repo's MIT license;
- native features of the stack (Renovate's own managers, mise) appear as candidates;
- the report has a ranked shortlist with reasons, a matrix whose cells use only native, partial, extensible, unsupported or unverified, "Verified" and "Could not verify" lists, and a coverage ledger with each route's state and queries;
- each reported limitation is tagged "verified in source" with path:line at a commit SHA, or "docs only", and a hosted service's limitations are docs only;
- any native feature it reports on is checked against the installed code or the docs for its pinned version;
- every `unsupported` matrix cell cites evidence of the absence (a search command and its scope), and unconfirmed cells are `unverified`;
- the "Verified" list includes at least the top two ranked candidates;
- the ledger includes the routes the need triggers (at least GitHub, npm, awesome lists and general web search), and later rounds were seeded from serious candidates (their topics, alternatives pages, awesome lists, other-language equivalents or dependents).
FAIL if any is missing.
