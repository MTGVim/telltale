# Telltale 결정사항 요약

## 1. 제품명 / 네임스페이스

- 제품명: **Telltale**
- 핵심 명령: **`/telltale:sail`**
- 기존 `/tk:*` namespace는 사용하지 않는다.
- 생성 상태는 `.claude/telltale/` 아래에 둔다.

## 2. 메인 컨셉

초기 `converge` 중심에서, island-hopping convergence loop로 재정의했다.

핵심 문장:

> Telltale은 가장 안전한 섬을 예언하지 않는다. 가장 싸게 확인할 수 있는 유용한 섬을 먼저 시도한다.

> 성공하면 검증된 항로가 생기고, 실패해도 다음 항해를 좁히는 증거가 남는다.

## 3. 명령명

`/telltale:converge` 대신 `/telltale:sail`을 선택했다.

이유:

- 사용자 입력 기준으로 더 자연스럽다.
- 출항/항해 멘탈모델과 잘 맞는다.
- 내부 기술 개념은 여전히 convergence loop로 설명한다.

## 4. M1 범위

M1은 core convergence loop만 구현한다.

포함:

- destination extraction
- island map
- island scorecard
- cost-aware greedy island selection
- subagent split
- event trace
- convergence report

제외:

- meta-feedback
- loop-memory
- doctor
- evidence anchor hash
- model routing UI
- worktree isolation

## 5. Subagent 구성

M1부터 실제 subagent 기반으로 간다.

- Cartographer: island map 작성
- Sailor: current island 실행
- Inspector: 검증/잔차 분석
- Advisor: 모호성/발산/중요 판단
- Orchestrator: command 본체, 최종 결정 및 trace 기록

핵심 원칙:

```txt
Sailor may be cheap.
Inspector must be skeptical.
Advisor is expensive and rare.
```

## 6. 정량화

LLM이 감으로 섬을 고르지 않도록 island scorecard를 둔다.

필드:

- value_to_destination
- cost_to_try
- verification_distance
- dependency_readiness
- information_gain_if_fail
- unknown_surface
- coordination_cost
- reversibility

선택 공식:

```txt
usefulness = value_to_destination + information_gain_if_fail + dependency_readiness + reversibility
cost = cost_to_try + verification_distance + unknown_surface + coordination_cost
priority = usefulness - cost
```

근거 없는 점수는 금지한다. 근거가 부족하면 unknown_surface를 올린다.

## 7. Verified route carry-forward

Greedy지만 기억상실은 아니다.

닫힌 island는 다음을 남긴다.

- facts
- decisions
- constraints
- passed checks
- deferred signals
- rejected signals

다음 island는 이 verified route를 바탕으로 시작한다.

## 8. 구현 흡수 대상

- TigerKit: branch-local generated state / command source 분리
- Ouroboros: spec/seed + ledger + replayable event + eval gate
- OMC: single loop authority / agent-model split
- oh-my-opencode-slim: orchestrator discipline / smallest useful improvement
- Ponytail: unnecessary work ladder / minimum needed implementation
- Claude Code subagents: isolated context, tool access, model control
