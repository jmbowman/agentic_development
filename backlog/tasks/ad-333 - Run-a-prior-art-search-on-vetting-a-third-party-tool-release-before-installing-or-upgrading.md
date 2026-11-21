---
id: AD-333
title: >-
  Run a prior-art search on vetting a third-party tool release before installing
  or upgrading
status: To Do
assignee: []
created_date: '2026-11-20T13:50:00Z'
labels: []
milestone: m-2
dependencies: []
references:
  - docs/prior-art/2026-11-18-parallel-session-and-worktree-management.md
priority: medium
type: search
ordinal: 23000
performer: agent
agent_tier: strong
effort: M
priority_set_by: agent
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Some tools this repo adopts ship releases daily and change behavior the developer cares about between releases. The first case is Orca (stablyai/orca, an Electron app with Linux AppImage/deb/rpm builds), being trialled against the blend in docs/prior-art/2026-11-18-parallel-session-and-worktree-management.md. The plan is to pin a release, turn off auto-update, and upgrade only after checking the candidate. The interim checklist is: wait out a release age (this repo's Renovate preset uses minimumReleaseAge: 3 days), search the tool's issues for regressions naming the version, diff only the paths that matter between the pinned and candidate tags (hook installation, worktree removal, settings and their migrations), and compare the download's sha512 with latest-linux.yml, which proves integrity but not authenticity. Run the prior-art-search skill on better ways to decide that a given release is safe and has no major known bugs: release-age cooldowns beyond Renovate, release-health and regression signals (issue trackers, hotfix detection, community reports), provenance and signing (Sigstore, SLSA, GitHub artifact attestations, reproducible builds), advisory databases (OSV), tools that summarise or risk-rank the diff between two releases, and pinning for desktop apps and AppImages (mise backends, apt holds). Done when a docs/prior-art/ note classifies candidates with licenses read from files, and recommends a vetting procedure for the Orca trial that can be reused for other adopted tools.
<!-- SECTION:DESCRIPTION:END -->
