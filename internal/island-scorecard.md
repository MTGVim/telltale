# Island Scorecard

Every Island must be scored on the fixed 0-5 M1 scale.

Fields:
- `value_to_destination`
- `cost_to_try`
- `verification_distance`
- `dependency_readiness`
- `information_gain_if_fail`
- `unknown_surface`
- `coordination_cost`
- `reversibility`

Every score must include non-empty `basis[]`. Unsupported confidence is forbidden. Missing evidence increases `unknown_surface`.
