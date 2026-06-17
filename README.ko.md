# Telltale 한글 설명판

**싼 반복. 측정 가능한 수렴.**

Telltale은 Claude Code 작업을 위한 cost-aware convergence orchestrator다.

Agentic coding은 목표가 모호해서만 실패하지 않는다. 작업 중에 표류하기 때문에 실패한다. 테스트가 깨지고, scope가 커지고, 기존 가정이 틀리고, 구현 후에야 새로운 gap이 드러난다.

Telltale은 Claude에게 “될 때까지 계속해”라고 시키지 않는다.

큰 작업을 닫을 수 있는 island로 나누고, 가장 싸게 확인할 수 있는 유용한 island부터 시도한다. 성공하면 검증된 항로가 생기고, 실패해도 다음 항해를 좁히는 증거가 남는다.

```txt
cheap probe
→ verification
→ residual analysis
→ correction or next island
→ convergence report
```

## 핵심 감각

```txt
Win small, or learn cheap.
```

한글로 풀면:

> 작게 이기거나, 싸게 배운다.

Telltale은 가장 안전한 island를 고르지 않는다. 안전한지는 가봐야 알기 때문이다.

대신 가장 싼 유용한 island를 고른다.

- 성공하면 검증된 항로가 생긴다.
- 실패하면 다음 항해를 좁히는 증거가 남는다.

## Greedy하지만 기억상실은 아니다

Telltale은 greedy하다. 하지만 매 island마다 새로 시작하지 않는다.

도달한 island는 검증된 항로를 남긴다.

검증된 항로에는 다음이 포함된다.

- 확인된 사실
- 유지해야 할 제약
- 이미 내린 결정
- 통과한 검증
- 보류/거절된 신호

다음 island는 빈 prompt에서 시작하지 않는다. 이전 island가 남긴 검증된 항로 위에서 시작한다.

## `/goal`과의 차이

`/goal`은 Claude를 계속 움직이게 한다.

Telltale은 Claude가 수렴하는지 측정한다.

| 구분 | `/goal` | Telltale |
|---|---|---|
| 핵심 | 계속 반복 | 측정하며 수렴 |
| 목표 | 사용자가 조건 작성 | 목적지와 island map 구성 |
| 실행 단위 | active condition | current island |
| 실패 처리 | 조건에 직접 써야 함 | residual / re-chart / stop |
| 증거 | transcript 중심 | event trace + convergence report |
| 적합 | 명확한 목표 | 중간에 변수가 생기는 작업 |

## 에이전트 구성

M1은 실제 subagent 기반으로 간다.

| 역할 | 책임 |
|---|---|
| Orchestrator | 전체 루프 제어, island 선택, event trace 기록 |
| Cartographer | destination을 island map으로 나눔 |
| Sailor | current island만 실행 |
| Inspector | diff/검증 결과를 보고 residual 분석 |
| Advisor | 모호성, 발산, 재항로 설정 시 조언 |

핵심 규칙:

```txt
Sailor may be cheap.
Inspector must be skeptical.
Advisor is expensive and rare.
```

Telltale은 변경을 만든 agent의 자기평가를 믿지 않는다.

## M1 범위

포함:

- `/telltale:sail`
- destination extraction
- island map
- island scorecard
- cheapest useful island selection
- subagents: Cartographer / Sailor / Inspector / Advisor
- current island execution
- verification
- residual analysis
- signal classification
- island close
- verified route carry-forward
- re-chart on drift
- event trace
- convergence report

제외:

- meta-feedback
- loop-memory
- doctor
- worktree isolation
- automatic rule promotion
