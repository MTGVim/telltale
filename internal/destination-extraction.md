# Destination Extraction

Cartographer converts the user's task, SOT, bug report, or failing log into a concrete Destination.

Required output:
- destination id and concise statement;
- close criteria;
- source evidence;
- explicit exclusions;
- unresolved questions.

Rules:
- Do not infer hidden acceptance criteria.
- Missing source-of-truth evidence must be recorded as uncertainty.
- Append `destination_extracted` before island mapping.
