#!/usr/bin/env bash
set -euo pipefail
export GIT_AUTHOR_NAME=Fixture GIT_AUTHOR_EMAIL=fixture@example.invalid
export GIT_COMMITTER_NAME=Fixture GIT_COMMITTER_EMAIL=fixture@example.invalid
export GIT_AUTHOR_DATE=2026-01-15T12:00:00Z GIT_COMMITTER_DATE=2026-01-15T12:00:00Z

git init -q -b main .
cat > AGENTS.md <<'EOF'
# Review assistant

An open-source tool that helps a human review changes an AI coding agent made. This repo is public.
Prior-art notes live in `docs/prior-art/`.
EOF
printf 'Apache License\nVersion 2.0, January 2004\n' > LICENSE

mkdir -p docs/prior-art
cat > docs/prior-art/2026-01-10-change-presentation.md <<'EOF'
# Prior art: presenting a large change for review (2026-01-10)

- **Effort:** full method, because the choice shapes the whole product.
- **Already known:** asked; unanswered (non-interactive run).

## Need and criteria

Present a multi-file change so a reviewer finds more defects in less time. Hard criterion: evidence from controlled studies.

## Verdict

**Build**, borrowing ideas from the papers below.

## Candidates and matrix

| Candidate | Class | License | Reason |
|---|---|---|---|
| [difftool-lite](https://example.org/difftool-lite) | reject | MIT (LICENSE:1 at 1a2b3c4) | Shows files in alphabetical order only |

## Limitations checked in source

Verified:
- difftool-lite has no ordering option (verified in source, src/order.py:12 at 1a2b3c4).

Could not verify:
- The first paper below beyond its abstract.

## Papers

| Paper | Read state | Evidence strength | Review status | Class | Claim (tag) |
|---|---|---|---|---|---|
| [Chunked Presentation of Multi-File Changes](https://doi.org/10.0000/fixture.0001) | abstract only | experiment | peer-reviewed | borrow ideas | The abstract reports that reviewers found more seeded defects when changes were presented in dependency order (paper-reported) |
| [A Survey of Diff Visualization](https://doi.org/10.0000/fixture.0002) | read in full | qualitative study | preprint | reject | Surveys tools and finds no controlled comparison (paper-reported) |

## Worth retrieving manually

- [Chunked Presentation of Multi-File Changes](https://doi.org/10.0000/fixture.0001) (DOI 10.0000/fixture.0001): its abstract reports a result that bears on the ordering criterion. Legal ways to obtain it: the publisher's pay-per-article page, a library or interlibrary loan, or a request to the authors.

## Coverage ledger

| Route | State | Queries or reason |
|---|---|---|
| arXiv | searched | "change presentation review" |

## Snowball rounds

Round 1 added both papers. The search stopped because round 2 added nothing.

## Refresh trigger

When a paper on the manual list is obtained.
EOF

git add -A && git commit -qm "Initial commit"

# The developer's lawfully obtained copy of the first paper, a fictional paper written for this fixture.
# It stays untracked, as a real inbox/ does.
mkdir -p inbox
cat > inbox/chunked-presentation.txt <<'EOF'
Chunked Presentation of Multi-File Changes: A Controlled Experiment
Ilse Brandvold and Teodor Maruyama, Fixture University

Abstract. We report a controlled experiment with 48 professional developers who each reviewed three multi-file
changes containing seeded defects. Presenting a change in dependency order, grouped into chunks of at most five
files, raised the share of seeded defects found from 41% to 57% (p < 0.01) and cut median review time by 12%.

1 Method. Participants were assigned at random to one of two presentation orders for each change: alphabetical by
path, or dependency order in chunks of at most five files. Each change contained between four and nine seeded
defects. The seeded defects were drawn from a published taxonomy of review-relevant faults. Participants worked
alone, with no time limit, and think-aloud protocols were recorded for twelve of them.

2 Results. Across all three changes, the dependency-order condition found more seeded defects: 57% against 41%.
The effect was largest for the change with the longest dependency chains, where the gain was nineteen percentage
points. The effect was smaller, but still positive, for the change that touched mostly independent files. Median
review time fell from 31 minutes to 27. The think-aloud recordings suggest that reviewers in the dependency-order
condition spent less effort reconstructing which file called which, and more effort checking each file's logic.

3 Threats to validity. All participants came from three companies, and the seeded defects may differ from real
ones. We did not test changes larger than twenty-two files, and we did not measure long-term retention of review
habits. Reviewers knew they were in an experiment, which may have raised their effort in both conditions.

4 Conclusion. Presenting a change in dependency order, in small chunks, is a low-cost way to help reviewers find
more defects without taking more time. We recommend that review tools offer this ordering by default.
EOF
