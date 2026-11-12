# delta

[delta](https://github.com/dandavison/delta), the git diff pager that this repo's [change-presentation note](../prior-art/2026-10-30-change-presentation.md) recommends extending rather than replacing. Items are from delta 0.20.1 (source at 3c2269c). delta's contributing guide sets no rule on AI-assisted contributions. A person writes the PR text and replies, as for the other upstreams.

## Show each changed line once, with removed and added words inline

- **Where:** the unified view's painter, `paint_minus_and_plus_lines` (`src/paint.rs:621`). Its unified branch paints every minus line, then every plus line (`src/paint.rs:671-700`).
- **What:** a reviewer reading an edited prose paragraph or a small code change sees the whole line twice and has to find the difference between them. A merged mode would show each paired line once, with removed words struck through and added words underlined, the way git's `--word-diff` does.
- **Evidence:**
  - delta already pairs minus and plus lines to compute its within-line highlights (`src/edits.rs:24`, `infer_edits`; `annotate` at `src/edits.rs:174`), and side-by-side mode uses the same pairing. So the change is in painting, not in the diff.
  - The request is [delta#152](https://github.com/dandavison/delta/issues/152), open since 2020. Its maintainer discussed a design there in 2021, asking whether marked lines should keep syntax highlighting and whether the mode would be an option or detected from git's arguments. That work stopped.
  - The workaround, git's own `--word-diff` piped through delta, is unreliable: see the next item.
- **Suggested fix:** an option such as `--inline-word-diff` that walks the existing line alignment and, for each paired minus and plus line, paints one row from the merged edit sequence:
  - unpaired lines stay as they are;
  - removed and added runs use `minus-emph-style` and `plus-emph-style`, so users' existing styles, strike and underline included, apply;
  - a fallback to separate lines when a pair alternates too often between changed and unchanged runs, like jj's `diff.color-words.max-inline-alternation`.

  Open design questions for the issue:
  - which line number a merged row shows;
  - how a merged row is described in OSC 1717 metadata, since one row covers two source lines. The spec describes a one-row modification as a `d` record followed by an `a` record.
- **Raised upstream:** partly. #152 exists; a design comment proposing this has not been posted.

## `--word-diff` output piped through delta loses its styling for code

- **Where:** word-diff detection (`src/handlers/hunk.rs:29-37`), which inspects the calling git command line, and the raw passthrough that follows (`src/handlers/hunk.rs:143-170`).
- **What:** with `git diff --word-diff=color | delta`, lines from a C++ file were re-highlighted as code and lost git's change styling, so `return x + 1` changed to `2` showed as `return x + 12`. Markdown lines usually kept their styling.
- **Evidence:** on 2026-10-30 with delta 0.20.1 and git 2.53, a scratch repo with one changed C++ line and one changed Markdown paragraph, colours set with `git -c color.diff.old=... -c color.diff.new=...`:
  - C++ alone lost its styling in 9 of 9 runs, both piped and through the real pager;
  - Markdown alone kept it in 5 of 6 runs;
  - in mixed diffs, only the Markdown line kept it.

  delta 0.17.0 behaved the same way. This matches [delta#1957](https://github.com/dandavison/delta/issues/1957).
- **Suggested fix:** decide passthrough per line from the input itself (git's word-diff colour codes, or `[-`/`{+` markers in `plain` mode) rather than from the parent process's arguments, and never apply syntax highlighting to a line that carries word-diff markup.
- **Raised upstream:** #1957 exists; these reproduction details have not been added.

## Hunk headers show one level of scope

- **Where:** hunk header handling (`src/handlers/hunk_header.rs`), which shows git's `code_fragment`.
- **What:** delta shows the single line git's function-name pattern found. A reviewer can't see the full path to a change: the heading chain in Markdown (H1 › H2 › H3), the class and method in Python or C++, or the table in TOML. Git's built-in `cpp` pattern also skips indented definitions, so a method defined inside a class body shows the class name instead.
- **Evidence:** git's patterns give one level and have no TOML or YAML driver (`userdiff.c` at v2.53.0). jj 0.46 added nearby source symbols to its hunk headers, and the same gap shows there.
- **Suggested fix:** an optional scope provider for hunk headers, using tree-sitter grammars or an external command that receives the file and line and returns a scope path. It falls back to git's fragment when the provider has nothing.
- **Raised upstream:** no. Best proposed after the merged-line work, so that one design discussion doesn't carry both.
