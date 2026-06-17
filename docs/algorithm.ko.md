# 알고리즘: Cost-aware Greedy Island Selection

Telltale은 LLM의 감으로 island를 고르지 않는다.

각 island는 scorecard를 가진다.

## Scorecard fields

| Field | 의미 |
|---|---|
| value_to_destination | 성공 시 최종 목적지에 기여하는 정도 |
| cost_to_try | 실행 비용 |
| verification_distance | 검증까지의 거리 |
| dependency_readiness | 지금 바로 가능한 정도 |
| information_gain_if_fail | 실패해도 얻는 정보량 |
| unknown_surface | 아직 모르는 영역 |
| coordination_cost | user/advisor 판단 비용 |
| reversibility | 실패 후 되돌리기 쉬운 정도 |

모든 score에는 basis가 필요하다.

근거가 없으면 confidence를 올리지 않고 unknown_surface를 올린다.

## Priority formula

```txt
usefulness =
  value_to_destination
+ information_gain_if_fail
+ dependency_readiness
+ reversibility

cost =
  cost_to_try
+ verification_distance
+ unknown_surface
+ coordination_cost

priority = usefulness - cost
```

## Selection rules

1. value_to_destination <= 0인 island는 제거한다.
2. dependency_readiness == 0인 island는 보류한다.
3. verification_distance >= 4인 island는 쪼갠다.
4. unknown_surface가 높은 island는 information_gain_if_fail도 높지 않으면 쪼개거나 보류한다.
5. ready island 중 priority가 가장 높은 island를 선택한다.
6. 동률이면 cost가 낮은 island를 선택한다.
