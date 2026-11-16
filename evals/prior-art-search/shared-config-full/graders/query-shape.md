---
type: llm
focus: trace
---

PASS if all hold:
- each route's first queries are short and broad (a few words), and later queries narrow them with terms the first results used; no query joins several products or vendors with OR;
- each route recorded as searched has at least 2 differently worded queries, where the stars-sorted and recently-pushed runs of one GitHub search count as one wording (a Semantic Scholar route records a seed paper or title in place of a query); the two local routes (the stack itself, and earlier notes and decisions) are exempt, since they are recorded as searched with what was checked rather than with queries.
FAIL if a route starts with long, specific queries, a query ORs several products or vendors, or a searched route has only one wording.
