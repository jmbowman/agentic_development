---
id: AD-325
title: >-
  Fold the 2026-11-17 search's route and harvester findings into sources.md and
  harvester.md
status: To Do
assignee: []
created_date: '2026-11-18T12:43:00Z'
labels: []
milestone: m-3
dependencies: []
references:
  - docs/prior-art/2026-11-17-in-repo-architecture-maps.md
  - AD-55
priority: low
type: feature
ordinal: 12000
performer: agent
agent_tier: moderate
effort: S
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The architecture-maps search (docs/prior-art/2026-11-17-in-repo-architecture-maps.md) found route and harvester behaviour the skill's references don't record. Fold it into skills/prior-art-search/references/sources.md and harvester.md, and decide whether the harvester's quoting should change:
- The harvester sends an unquoted multi-word arXiv query as an exact phrase, and it returns empty with no error. Quoted terms joined by AND work.
- Semantic Scholar recommendations from arXiv seeds were the most productive snowball. OpenAlex citations and references from broad seeds were mostly unrelated.
- npm search for "map" or "repo map" returns unrelated packages. libraries.io sorted by latest release found tools npm missed.
- GitHub's license API reports NOASSERTION both for standard MIT or Apache texts with a trailing note and for non-OSI licenses, and reports only one license of a dual license.
- LibHunt's `/r/<owner>/<repo>` pages often return 404, and owner-less URLs can land on a different project.
- ACM returned 403 to a scripted fetch of a PDF that OpenAlex lists as open access. The institution's repository copy and arXiv's HTML worked.
- Shallow clones carry no tags. `git ls-remote --tags` lists releases without spending GitHub API calls.

Related: AD-55. Done when the references record these and checks pass.

**Why it matters:** The next search avoids the same silent empties and misleading license labels.

**Why an agent:** the findings are stated; it's a references edit, with a harvester fix if one is chosen
<!-- SECTION:DESCRIPTION:END -->
