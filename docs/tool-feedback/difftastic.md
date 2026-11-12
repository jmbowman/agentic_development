# difftastic

[difftastic](https://github.com/Wilfred/difftastic), the structural differ that this repo's [change-presentation note](../prior-art/2026-10-30-change-presentation.md) recommends extending rather than replacing. Items are from difftastic 0.71.0 (source at 4618021). Its AI policy asks for AI use to be disclosed in commit messages or pull requests, and issue and PR comments must not be written with an LLM. So agents may help with the code, but a person writes the PR text and replies.

## No function or class in hunk headers

- **Where:** hunk headers are built by `style::header` (`src/display/style.rs:539-579`) from the path, the hunk number and the language. It's called per hunk from `src/display/inline.rs:76`.
- **What:** a reviewer can't see which function, class or heading a change belongs to, which git's hunk headers and delta show. This is the main reason to prefer delta even when difftastic's diff is clearer.
- **Evidence:**
  - The tree-sitter node kind is available while parsing (`list_from_cursor`, `src/parse/tree_sitter_parser.rs:1837`) but isn't kept on `Syntax::List` (`src/parse/syntax.rs:116-131`).
  - The request is [difftastic#304](https://github.com/Wilfred/difftastic/issues/304), open since 2022. Commenters ask for git's `-p`-style function context, and note that tree-sitter could get it right where regexes don't.
- **Suggested fix**, either of these:
  - keep the node kind and name on lists, add a per-language table of scope kinds, and pass the enclosing scope path to `header()` (medium);
  - a cheaper first step: look back through the source for the nearest definition line with a per-language pattern, as jj 0.46's `source_symbol.rs` does (small).
- **Raised upstream:** #304 exists; no implementation has been proposed.

## No inline display mode

- **Where:** the display modes, side-by-side and inline (`main.rs:963-976`). The inline view prints each side's changed lines separately.
- **What:** each changed line appears twice, once per side, even when only one token changed. For long lines this makes the change hard to find.
- **Evidence:** hunks carry matched line pairs (`src/display/hunks.rs:19-28`), and the novel spans per side are known, so a merged row is a display change.
- **Suggested fix:** a display mode that, for each matched line pair, prints one row interleaving the removed and added novel spans, with separate rows for unmatched lines.
- **Raised upstream:** not found in a search for "inline word". [difftastic#846](https://github.com/Wilfred/difftastic/issues/846) concerns the inline highlighting style, which is related.

## Colours are fixed

- **Where:** `novel_style` (`src/display/style.rs:308-319`) uses ANSI red and green, bright on dark backgrounds; the only option is `--background`.
- **What:** a user can't choose colours or add non-colour cues. Readers with red-green colour blindness depend on their terminal theme happening to make red and green distinguishable.
- **Evidence:** open issues [difftastic#675](https://github.com/Wilfred/difftastic/issues/675) (additions hard to see on some themes) and [difftastic#611](https://github.com/Wilfred/difftastic/issues/611) (bright green unreadable under Solarized).
- **Suggested fix:** configurable styles for novel tokens on each side, accepting attributes such as underline and strikethrough as well as colours. Keeping the ANSI palette colours as the default keeps today's behaviour.
- **Raised upstream:** the colour problems are; a styles option isn't proposed.

## No Markdown parser

- **Where:** language detection (`src/parse/guess_language.rs`). A search of it and of the vendored parsers finds no Markdown grammar.
- **What:** Markdown files fall back to a line-based text diff, so specs and docs get none of difftastic's benefits, and they're where reflowed paragraphs make line diffs hardest to read.
- **Evidence:** the tree-sitter-md grammar exists (MIT), with separate block and inline grammars.
- **Suggested fix:** add tree-sitter-md, treating headings, list items and paragraphs as lists and words as atoms, so a reflowed paragraph diffs by word.
- **Raised upstream:** not checked.
