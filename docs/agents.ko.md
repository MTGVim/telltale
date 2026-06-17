# 에이전트 구성

Telltale M1은 실제 subagent 기반으로 간다.

역할 분리는 환각 방지의 핵심이다.

```txt
Sailor may be cheap.
Inspector must be skeptical.
Advisor is expensive and rare.
```

## Orchestrator

- 전체 루프 제어
- loop authority claim/release
- Cartographer/Sailor/Inspector/Advisor 호출
- event trace append
- island 선택
- close/re-chart/stop 결정
- report 작성

Orchestrator는 제품 코드를 직접 수정하지 않는다.

## Cartographer

- destination 추출
- island map 작성
- scorecard 작성
- 모든 점수에 basis 제공

근거가 부족하면 unknown_surface를 올린다.

## Sailor

- current island만 실행
- island map 수정 금지
- destination success 선언 금지
- scope 밖 작업 발견 시 signal로 보고

Sailor는 싼 모델을 쓸 수 있는 후보이다.

## Inspector

- Sailor output 검증
- diff, verification output, close criteria를 본다
- Sailor 자기평가를 primary evidence로 믿지 않는다
- signal classification 제안

Inspector는 제품 코드 수정 권한이 없어야 한다.

## Advisor

- 모호성/발산/재항로/abort/block 판단
- 추천만 한다
- Orchestrator가 결정한다

Advisor는 비싸고 드물게 호출한다.
