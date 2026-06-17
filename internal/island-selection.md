# Island Selection

Select the cheapest useful ready Island.

Formula:

```text
usefulness = value_to_destination + information_gain_if_fail + dependency_readiness + reversibility
cost = cost_to_try + verification_distance + unknown_surface + coordination_cost
priority = usefulness - cost
```

Selection rules:
1. Remove islands with `value_to_destination <= 0`.
2. Defer islands with `dependency_readiness == 0`.
3. Split islands with `verification_distance >= 4`.
4. Split islands with `unknown_surface >= 4` unless `information_gain_if_fail` is high.
5. Select the ready island with highest priority.
6. On ties, choose lower cost.
7. If all priorities are low, re-chart or ask Advisor/user.
