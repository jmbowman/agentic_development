# Interactive scenarios specs

Design: [interactive-evals-design.md](interactive-evals-design.md). The terms below are used as follows:
- **The plugin:** the pytest plugin pytest-claude-code-evals.
- **A skill:** a directory in this repo's `skills/` that contains a `SKILL.md`; `<skill>` is its directory name, and `<module>` is that name with each `-` replaced by `_`.
- **A scenario directory:** `evals/<skill>/interactive/` for a skill.
- **A scenario module:** a file named `test_*.py` in a scenario directory.
- **A scenario:** a module-level function in a scenario module whose name starts with `test` (methods of test classes aren't scenarios).
- **An `@spec` annotation:** a Python comment line of the form `# @spec ID[, ID...]`.
- **A segment's specs file:** a file `docs/intent/<segment>/<segment>-specs.md` in this repo.
- **A spec's marker:** the italic parenthetical that ends its line in a segment's specs file, such as *(eval)*.
- **An eval case:** a directory under `evals/<skill>/` that holds a `case.yaml`; it cites a spec when its `case.yaml` has a `# @spec` comment line naming the spec's ID.
- **A manual script:** a `##` section of a skill's `evals/<skill>/manual.md` whose heading names at least one spec ID; it names the spec IDs in its heading.
- **The check task:** the `check` task in this repo's `mise.toml`, with the tasks it depends on.

What the scenarios need the plugin to provide is listed in the design for the plugin's own design to cover; it isn't specified here. How runs are recorded in the review log is a working rule in this repo's `AGENTS.md`.

## Layout

- [x] **IEVAL-LAY-001**: Each scenario module shall be named `test_<module>.py` or `test_<module>_<suffix>.py`, where `<module>` is derived from the skill whose scenario directory holds it.
- [x] **IEVAL-LAY-002**: A `conftest.py` in a scenario directory shall contain no `@spec` annotation.
- [x] **IEVAL-LAY-003**: Each scenario whose `@spec` annotation cites a spec ID starting `NOTES-` shall be in `evals/session-wrap-up/interactive/`.
- [x] **IEVAL-LAY-004**: For each skill, `git check-ignore` shall match the path `evals/<skill>/interactive/results/`.

## Dependency

- [ ] **IEVAL-DEP-001**: This repo's `pyproject.toml` shall list the plugin in its `[dependency-groups]` table under exactly one group, `interactive`, with a version specifier that names one exact release or one git commit, and shall not list it under `[project]`.
- [ ] **IEVAL-DEP-002**: The check task's dependency install shall include the `interactive` dependency group.
- [x] **IEVAL-DEP-003**: This repo's pytest `testpaths` setting shall be set, and shall name no path under `evals/`.

## Checks without a model

- [x] **IEVAL-CHK-001**: The check task shall collect every scenario module with pytest without running any scenario, shall fail when collecting a scenario module fails, and shall pass when no scenario module exists.
- [x] **IEVAL-CHK-002**: Every `.py` file in a scenario directory shall pass the check task's type checker.

## Sessions

- [ ] **IEVAL-RUN-001**: Each scenario shall start its Claude Code sessions with `--plugin-dir` set to the absolute path of this repo's working tree.
- [ ] **IEVAL-RUN-002**: Each scenario shall give its Claude Code sessions a working directory, a home directory and a config directory that it seeds outside this repo's working tree.
- [ ] **IEVAL-RUN-003**: The scenario that checks NOTES-LIVE-003 (hooks registered both by the plugin and in project settings) shall seed its scratch repo's `.claude/settings.json` with the subagent notes hook entries of this repo's `.claude/settings.json`, read when the scenario runs, for the same events and matchers, with each command's script path replaced by the script's absolute path in this repo's working tree.

## Markers

- [x] **IEVAL-MARK-001**: A spec shall be marked *(interactive)* only when a scenario's `@spec` annotation cites it, no eval case cites it, and no manual script names it.
- [x] **IEVAL-MARK-002**: A spec shall be marked *(eval, interactive)* only when an eval case and a scenario's `@spec` annotation both cite it and no manual script names it.
- [x] **IEVAL-MARK-003**: A spec that a scenario's `@spec` annotation cites and no manual script names shall be marked exactly *(interactive)* or *(eval, interactive)*, or carry no marker.
- [x] **IEVAL-MARK-004**: No `##` heading in a skill's `manual.md` shall equal, after its leading `## ` and trailing whitespace are removed, the argument of a `replaces` marker on a scenario in that skill's scenario directory.
- [x] **IEVAL-MARK-005**: A `replaces` marker shall be applied to a scenario function and shall take exactly one positional string argument: the heading text, without its leading `## ` and trailing whitespace, of the manual script the scenario replaces. At most one scenario in a scenario directory shall carry a given argument.
- [ ] **IEVAL-MARK-006**: A scenario shall carry a `replaces` marker only when it checks every step and pass condition of that manual script; a scenario that checks only some of them shall not carry the marker until the script has been split so that one of its parts holds exactly what the scenario checks.
- [x] **IEVAL-MARK-007**: This repo's pytest configuration shall register the `replaces` marker.
- [x] **IEVAL-MARK-008**: When a file `evals/<name>/manual.md` holds no manual script, it shall not exist, whatever other text it holds and whether or not `<name>` is a skill.
- [x] **IEVAL-MARK-009**: The test module `tests/test_interactive_scenarios.py` shall check IEVAL-LAY-001 to IEVAL-LAY-003, IEVAL-MARK-001 to IEVAL-MARK-005, IEVAL-MARK-008, IEVAL-STAT-001 and IEVAL-STAT-002 across every segment's specs file, every `evals/*/manual.md` and every scenario directory, reading `@spec` annotations as text lines and `replaces` markers from each scenario module's syntax tree, without importing the plugin.

## Latest results

A **triaged run** of an eval case or scenario is the run that a row of `docs/review-log.md` reports; its **row** is that review-log row, identified by the row's Date, Component, Phase and Wave columns. A run **counts** unless triage traced its failure to the grader or the case rather than the skill.

- [x] **IEVAL-STAT-001**: For each skill that has an eval case or a scenario, `evals/<skill>/latest-results.md` shall hold one Markdown table, with a header row and exactly one body row for each of the skill's eval cases and scenario functions, and no other body rows.
- [x] **IEVAL-STAT-002**: Each body row of a latest-results table shall hold, in order: the eval case's directory name or the scenario's `<module file>::<function>`; and, for its latest triaged run, the run's date, the Claude Code version, the model under test (not the judge), the number of its runs in that triaged run that count, the number of those that failed, and the review-log row's Date, Component, Phase and Wave; dates shall be written `YYYY-MM-DD`, and the two counts as whole numbers with the failures no more than the runs. A case or scenario with no triaged run shall hold `never run` in each of those cells.
