---
id: AD-325
title: >-
  Fold the 2026-11-17 search's route and harvester findings into sources.md and
  harvester.md
status: To Do
assignee: []
created_date: '2026-11-18T12:43:00Z'
updated_date: '2026-11-23T00:03:00Z'
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

The parallel-sessions search (docs/prior-art/2026-11-18-parallel-session-and-worktree-management.md) hit the same exact-phrase behaviour again: 11 of its 23 arXiv phrase queries, all of four or more words, came back empty with no warning, and it was found only by reading a raw feed. That makes a harvester fix (or at least a warning on an empty multi-word arXiv query) more pressing than a references note alone. The same run also found that the harvester prints `harvest.log` as an output path but never wrote that file in the run directory.

Related: AD-55. Done when the references record these and checks pass.

**Why it matters:** The next search avoids the same silent empties and misleading license labels.

**Why an agent:** the findings are stated; it's a references edit, with a harvester fix if one is chosen
<!-- SECTION:DESCRIPTION:END -->

## Comments

<!-- COMMENTS:BEGIN -->
author: d7b6ac42-ae0a-43d4-910b-471bd3b28ac7
created: 2026-11-22T00:15:00Z

---

The 2026-11-18 parallel-session search (docs/prior-art/2026-11-18-parallel-session-and-worktree-management.md) found more route behaviour for sources.md:
- the agent's web search tool ignored `site:`, so `site:codeberg.org` and `site:pypi.org` queries returned nothing from those sites;
- GitHub topic lookups for broad terms (claude-code, jujutsu) returned mostly spam topics, while lookups by a candidate's name (herdr, orca) found its plugin topics;
- jsDelivr's `resolved?specifier=main` returned `version: null` for GitHub repos, and the first tag it lists can lag the latest release;
- proxy.golang.org resolves a Go module's bare path to its v1 line, so a module now at `/v3` looks stale;
- libraries.io can list npm packages that have no published versions;
- npm searches on generic words (concurrency limit, monitor, dashboard) return unrelated SDKs, while naming the agent or Claude works;
- Hugging Face paper search results carry a `githubRepo` field, the quickest source of a paper's code link.

---

author: a83d57b3-ccde-4032-8a68-b0d049aa9a66
created: 2026-11-23T00:03:00Z

---

Route findings from the generated-views search (docs/prior-art/2026-11-19-generated-views-over-markdown.md): GitHub answered HTTP 403 "secondary rate limit" after about 15 repository searches sent 3 s apart, with primary quota still left; 6 s spacing with a back-off on "rate limit" ran clean for about 100 more. `gh search code` queries with several terms returned no hits even where the terms appear together; single names worked. libraries.io's `licenses` field holds whole license texts, so trim it with jq before reading the output.

---
<!-- COMMENTS:END -->
