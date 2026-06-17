# Island Close

Orchestrator decides whether an Island can close.

Close requires:
- Inspector close recommendation;
- passing verification or an explicit recorded exception;
- no accepted residual that invalidates close criteria.

On close, append `island_reached` and `verified_route_recorded`. Route segments include facts, decisions, constraints, passed checks, deferred signals, and rejected signals.
