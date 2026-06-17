# 멘탈모델: Island Hopping Convergence

Telltale은 큰 작업을 한 번에 완전 자율 실행하지 않는다.

큰 목표를 닫을 수 있는 island로 나누고, 가장 싸게 확인할 수 있는 유용한 island부터 시도한다.

## 가장 안전한 island가 아니다

Telltale은 가장 안전한 island를 고르지 않는다.

안전한지는 가봐야 알기 때문이다.

대신 가장 싼 유용한 island를 고른다.

```txt
성공하면 목적지에 가까워진다.
실패해도 다음 항해를 좁히는 증거가 남는다.
```

## Greedy하지만 기억상실은 아니다

Telltale은 greedy하다.

하지만 매 island마다 새 출발하지 않는다.

닫힌 island는 verified route를 남긴다.

다음 island는 빈 prompt가 아니라, verified route 위에서 시작한다.

## 핵심 문장

```txt
Win small, or learn cheap.
```

```txt
Telltale is greedy, but not forgetful.
```
