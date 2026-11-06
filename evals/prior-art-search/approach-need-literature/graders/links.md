---
type: llm
focus: trace
---

PASS if all hold:
- in the report and the saved note, each paper is a Markdown link whose text is its name at its first mention in each section and in every table row; no full URL appears as link text; a paper with no link found says "no link found" beside its name;
- each link target is one the assistant opened or took from the page where it found the paper (its open-access page, otherwise its DOI link, otherwise its publisher's or preprint server's page), not one composed from memory.
FAIL if any is missing.
