---
type: tool_used
tool: Bash
input_match: '"command"\s*:\s*"(?:[^"\\]|\\.)*?(?:(?:^|"|;|&&|\|\||\||\\n)\s*(?:cp|mv|rm|touch|mkdir|truncate|ln)\s|\btee\b|\bsed\s+-i|\s>>?\s*(?:[./~$][\w./-]*|[\w-]+\.[a-z]+)|\bopen\([^),]*,\s*(?:mode\s*=\s*)?\\?[\x27"][wax])'
min: 0
max: 0
---
