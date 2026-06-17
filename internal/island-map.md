# Island Map

Cartographer decomposes the Destination into candidate Islands.

Each Island must include:
- id;
- title;
- scope;
- dependencies;
- close criteria;
- evidence;
- expected verification.

Rules:
- Islands should be small enough for Sailor to execute without scope drift.
- Do not include roadmap/future work in M1 islands unless required by the current Destination.
- Append `island_map_created` after mapping.
