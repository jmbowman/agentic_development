# Tool feedback

Proposed enhancements and bugs for the tools this repo uses or plans to adopt, kept until they're raised upstream. One page per tool. Each item says where the problem is, what's wrong or missing, the evidence, a suggested fix, and whether it has been raised upstream.

- [Claude Code](claude-code.md): a SubagentStop block replaces the report, or is ignored after a hand-back; no agent ID in a foreground result outside auto mode.
- [LID](lid.md): suggestions for decision docs and their tooling; setup docs that overstate what the plugins enforce.
- [lid-tooling (`lidc`)](lid-tooling.md): coverage that passes vacuously under a `test` directory; citations in script files and in tests defined as data (eval cases) ignored; text in string literals counted as citations; six proposed checks.
- [mdbook-lint](mdbook-lint.md): decision-record rules that misfire on LID's decision folders.
- [kontext](kontext.md): the npm package isn't published.
- [github-repo-meta-fetch](github-repo-meta-fetch.md): no releases; a generated `CLAUDE.md`.
- [extant](extant.md): checked documents must be listed one by one.
- [vendir](vendir.md): a locked SHA that isn't a tip can't be fetched shallowly; every tag is fetched; no default-branch ref.
- [paper-search-mcp](paper-search-mcp.md): pacing and retries spread across connectors and limited to one process; a hard-coded Crossref address; retries without TLS verification; a PyPI release far behind main; live-network probes in unit test files.
- [claude plugin eval](claude-plugin-eval.md): gitignored files count toward the plugin's 20,000-entry cap; results can only go inside the plugin directory.
- [APM](apm.md): skills deployed by APM 0.33.0 block a dependency bump under 0.35.1.
- [Renovate](renovate.md): the `pep723` manager neither updates script lock files nor bumps git-pinned dependencies; the `vendir` manager silently skips a commit-pinned git source.
- [oneyaml](oneyaml.md): no releases or tags; an invalid `ONEYAML_BACKEND` stops the import; empty published conformance results.
- [delta](delta.md): no mode showing each changed line once; `--word-diff` output loses its styling for code; hunk headers show one level of scope.
- [difftastic](difftastic.md): no function or class in hunk headers; no inline display mode; fixed colours; no Markdown parser.
- [Backlog.md](backlog-md.md): a task file can run a shell command; claims not atomic; ID generation fetches and prunes; `init --defaults` writes an always-run instruction into `AGENTS.md`; the terminal viewer moves backticked paths out of their sentences; the assignee filter treats `alex` and `@alex` as different people.
- [Orca](orca.md): the GUI's Delete forces removal; turning off status hooks leaves them installed; docs and code disagree on the orchestration concurrency cap.
- [Clash](clash.md): conflict checks write loose objects; watch mode misses changes in linked worktrees.
- [Worktrunk](worktrunk.md): removal neither checks nor backs up gitignored files.
