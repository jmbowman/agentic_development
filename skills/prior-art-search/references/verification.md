# Verification

How to read licenses and source, how to tag limitations, and the records subagents return.

## Licenses

Read the license from evidence the author controls, using the first of these that exists:
1. the license file: `LICENSE`, `LICENSE.md`, `LICENSE.txt`, `LICENSE-MIT`, `COPYING` and similar;
2. the license field in the package manifest: `pyproject.toml`, `Cargo.toml`, `package.json`, `PKG-INFO` and similar;
3. the README, or file headers.

Cite the file and line you used. A forge badge or the forge API's license field is only a pointer to where to look; never record a license from it alone.

- **Pin it.** Record the license at the commit you read, and for the paths you use. In a monorepo, a package's own license file takes precedence over the one at the repo root.
- **Choices.** When a license offers a choice ("MIT OR Apache-2.0", or separate `LICENSE-MIT` and `LICENSE-APACHE` files), record every option.
- **Vendored code.** When a candidate vendors code under another license (`vendor/`, `_vendor/`, `third_party/`), flag the directory and its license; it can fail the license criterion on its own.
- **No license.** Cite the file listing that showed none, read at `full` depth (a summary of the repo page doesn't count). A candidate with no license can be borrowed from as an idea, but never adopted or built on.
- **Source-available licenses** are judged against the hard criteria from step 2, for how the host repo will use and distribute the result.
- **Read the whole file.** Read the license file at `full` depth (see [Read depth](#read-depth)), to the end, in a quick pass too: registries, badges and the file's own heading can say "MIT" for a file that adds terms below the standard text. Search it for added terms (`grep -niE "commons clause|rider|additional terms|restrict" LICENSE*`) and read each hit. Wording of the standard text itself, such as MIT's "without restriction", and an exception on SPDX's exception list, such as a GPL linking exception, aren't added terms. Record any added terms as part of the license (for example "MIT plus the Commons Clause"), treat it as source-available, and name the added terms in the report.
- **Unread is unverified.** A license read only at `snippet` depth leaves the license criterion `unverified`, and a candidate whose license is `unverified` is never classified **adopt** or **build on**.

## Lookalike copies

Results sorted by update time surface copies of real tools that aren't marked as forks. Check a serious candidate when it has the same description or license copyright holder as another project while its own owner isn't that holder, or has a README that tells users to download and run an installer instead of building the code, whoever the owner is. Search for the original by name, taking first the repo whose owner matches the license's copyright holder, then the repo the tool's package registry entry or official site links to, then the earliest-created repo with that name and description.
- **Original found:** reject the copy with the original named as the reason, and add the original as a serious candidate in the current round if it fits the need.
- **No original found:** evaluate the candidate on its merits, flag it in the report as a possible copy, and don't classify it **adopt** or **build on** without the developer's review (in a non-interactive run, the report asks for that review).

## Read depth

A reading is `full` only when you had the text itself: from a clone, the forge's contents API, a local file, or a raw file or verbatim endpoint (a `.md` docs page, `llms-full.txt`, docs.github.com's article API, jsDelivr's `gh/` route for a README or license) fetched with a tool that returns it unchanged, such as `curl`. A fetch tool that summarizes or truncates the page (Claude Code's WebFetch does both) gives `snippet` depth whatever URL it fetched, and so do web search results. The rule holds for your readings and your subagents' alike. A paper is *read in full* only when its whole body text was read at `full` depth.

## Reading source

When you verify a candidate in source (step 9), read its code from the first of these that's available:
1. **The repo's own reference-clone convention,** if the repo's instructions name one. Read the clone at the commit it holds; don't update it.
2. **The forge's contents API,** for a few files: GitHub's needs authentication (`gh api repos/<owner>/<repo>/contents/<path>?ref=<sha>`); GitLab's works for public projects without it (`https://gitlab.com/api/v4/projects/<url-encoded project path>/repository/files/<url-encoded file path>/raw?ref=<sha>`).
3. **A scratch shallow clone,** into a new, empty directory under your scratch or temp directory, never inside the repo you're working in:

   ```bash
   dir="$(mktemp -d)/<repo>"
   GIT_LFS_SKIP_SMUDGE=1 git clone --depth 1 --no-recurse-submodules <url> "$dir"
   git -C "$dir" rev-parse HEAD
   ```

   For a large repo, clone without file contents and check out only what you need:

   ```bash
   dir="$(mktemp -d)/<repo>"
   GIT_LFS_SKIP_SMUDGE=1 git clone --depth 1 --no-recurse-submodules --filter=blob:none --sparse <url> "$dir"
   git -C "$dir" sparse-checkout set <path> [<path> ...]
   git -C "$dir" rev-parse HEAD
   ```
4. **The package registry's published source archive,** for a candidate with no reachable forge. Download it and extract it into a new, empty scratch directory (`tar -xzf <archive> -C "$(mktemp -d)"`, or `unzip -d`). Never build or install it, and never run its `setup.py`, build scripts or hooks.

Record the resolved commit SHA, or the archive's version, for every reading, so each `path:line` you cite is pinned. Cleaning up scratch clones is optional.

## Limitation tags

Tag each limitation you report:
- *verified in source (path:line at commit)*, when you read the code that causes it;
- *docs only*, when you have only documentation, an issue or a changelog;
- *paper-reported*, for a claim drawn from a paper, unless you checked it in the paper's published artifact (its code, dataset or supplementary material), when it can be *verified in source*.

A hosted service or closed-source candidate's limitations are always *docs only*. A native feature is verified against the installed code, or the docs for its pinned version.

**What verifies.** Only a full read supports *verified in source* or counts a candidate as verified in step 9: the files the claim concerns, read from start to end (for a long file, the complete cited function or section and its callers on the claim's path). A claim that something is absent ("no clone step anywhere in `references/`") is `listing` evidence: cite the search command you ran and its scope, such as `grep -rn "git clone" references/` at a commit. A listing whose scope covers the claim counts as a full read for an absence claim.

A reading at snippet depth is a lead, never a basis for a *verified in source* tag: the agent makes the full read itself, or has a subagent make it, before the claim is tagged verified. That holds whether the snippet reading was yours or a subagent's.

## Subagent records

A subagent that searches routes or reads a candidate returns only these records, never prose conclusions.

**Evidence record:** `{candidate, url, criterion, claim, support, evidence, evidence_kind, read_depth, commit, as_of}`
- `support`: `native`, `partial`, `extensible`, `unsupported` or `unverified`.
- `evidence`: a URL, or a `path:line`.
- `evidence_kind`: `source`, `manifest`, `docs`, `metadata` or `listing`.
- `read_depth`: `full` or `snippet`.
- `commit`: the commit SHA or archive version read.
- `as_of`: an ISO date.

**Ledger record:** `{route, state, queries, reason, as_of}`
- `state`: `searched`, `excluded` or `unavailable`.
- `queries`: the queries run, for a searched route.
- `reason`: the reason for an exclusion, or the diagnosis for an unavailable route.

**Paper record:** `{paper, doi, url, claim, read_state, evidence_strength, review_status, as_of}`
- `read_state`: `read in full`, `read in part` (naming the sections), `abstract only` or `not retrievable`. It is the paper's read state, which is not the evidence record's `read_depth`.
- `evidence_strength`: `experiment`, `weak experiment`, `observational study`, `qualitative study` or `untested proposal`.
- `review_status`: `peer-reviewed`, `preprint`, `thesis` or `unreviewed report` (a vendor report is an unreviewed report).
- `url`: the paper's best link: its open-access page, otherwise its DOI link, otherwise its publisher's or preprint server's page.

No record, query or URL carries a setting's value. A subagent follows the same rules as the main agent, which puts them in each subagent's prompt from the list in SKILL.md's "Working in parallel" section, rate limits included.
