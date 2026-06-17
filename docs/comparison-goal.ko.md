# `/goal`과 Telltale의 차이

`/goal`은 Claude를 계속 움직이게 한다.

Telltale은 Claude가 수렴하는지 측정한다.

| 구분 | `/goal` | Telltale |
|---|---|---|
| 핵심 | 계속 반복 | 측정하며 수렴 |
| 목표 | 사용자가 completion condition 작성 | destination과 island map 구성 |
| 실행 단위 | active goal condition | current island |
| 증거 | transcript-visible evidence | event trace + verification + report |
| 실패 처리 | prompt에 직접 써야 함 | residual / re-chart / stop |
| 적합 | 명확한 조건 | 중간에 변수가 생기는 작업 |

핵심 문장:

```txt
/goal helps Claude continue.
Telltale helps Claude converge.
```
