# Telltale 한글 설명판

[![Validate](https://github.com/MTGVim/telltale/actions/workflows/validate.yml/badge.svg)](https://github.com/MTGVim/telltale/actions/workflows/validate.yml)

**싼 반복. 측정 가능한 수렴.**

Telltale은 Claude Code 작업을 위한 cost-aware convergence orchestrator다. 긴 agentic 작업을 작은 island로 나누고, 가장 싸게 확인할 수 있는 유용한 island부터 실행한 뒤, 검증된 항로만 다음 단계로 넘긴다.

현재 릴리즈: `0.0.5`.

```txt
Win small, or learn cheap.
```

한글로 풀면:

> 작게 이기거나, 싸게 배운다.

## 언제 쓰나

Telltale은 이런 상황에 적합하다.

- 작업이 길다.
- scope drift가 생기기 쉽다.
- 자기보고가 아니라 evidence 기반 검증이 필요하다.
- agent가 범위를 넓히기 전에 bounded island 하나를 끝내길 원한다.
- 실패하더라도 다음 항해를 좁히는 증거가 남아야 한다.

## 언제 쓰지 않나

Telltale은 이런 상황에는 과하다.

- 아주 작은 one-shot 수정이다.
- 이미 정확한 파일과 patch를 알고 있다.
- 탐색 비용이 직접 구현보다 크다.
- background daemon, cross-run learning, model-routing UI가 필요하다.

## `/goal`과의 차이

`/goal`은 done을 정의한다.

`/telltale:sail`은 route를 제어한다.

목적지 계약에는 `/goal`을 쓰고, 항로가 표류할 수 있으면 `/telltale:sail`을 쓴다.

```text
/goal 빈 장바구니 checkout bug는 안내 상태가 보이고 테스트가 통과하면 완료다.
/telltale:sail 현재 실패 로그에서 checkout 빈 장바구니 상태를 고치고 검증해.
```

## 명령어

Marketplace-safe 공개 Claude Code command는 하나다.

```text
/telltale:sail <task, SOT, bug report, failing log, or goal>
```

짧은 `/sail`은 local/installed skill/Hermes-friendly alias다.

| 환경 | 명령 |
|---|---|
| Claude Code marketplace plugin | `/telltale:sail <task>` |
| Claude Code installed skill / local checkout alias | `/sail <task>` |
| Hermes Agent skill command | `/sail <task>` |

공개 `/telltale:converge` 명령은 없다. convergence는 내부 개념이고, 사용자-facing command는 `sail`이다.

## 핵심 루프

1. destination 추출
2. candidate island map 작성
3. evidence 기반 island scorecard 작성
4. cheapest useful ready island 선택
5. Sailor가 current island만 실행
6. Inspector가 skeptical하게 검증
7. residual signal 분류
8. close / re-chart / block / abort / continue 결정
9. event trace, state, report 작성

생성 state는 `.claude/telltale/` 아래에 branch-local로 저장되며 gitignore 대상이다.

구체적인 첫 실행 예시는 [`docs/examples/fix-failing-test.md`](docs/examples/fix-failing-test.md)를 보면 된다.

## 설치 검증

```bash
python3 scripts/telltalectl.py doctor
```

정상 예시:

```text
Telltale doctor

OK   plugin manifest found
OK   marketplace manifest found
OK   public command found: /telltale:sail
OK   local alias found: /sail
OK   Hermes skill found: hermes/skills/sail
OK   generated state is gitignored
OK   versions match: 0.0.5

Result: healthy
```

전체 local validation:

```bash
npm run validate
python3 scripts/telltalectl.py doctor
```

`npm run validate`는 `claude plugin validate . --strict`, schema validation, smoke, doctor, unit test를 실행한다.

## Claude Code local development install

```bash
git clone https://github.com/MTGVim/telltale.git
cd telltale
claude --plugin-dir .
```

Claude Code 안에서:

```text
/telltale:sail <task>
/sail <task>
```

## Claude Code marketplace/public install

Claude Code 안에서:

```text
/plugin marketplace add MTGVim/telltale
/plugin install telltale@telltale
/reload-plugins
/telltale:sail <task>
```

로컬 CLI equivalent:

```bash
claude plugin marketplace add MTGVim/telltale
claude plugin install telltale@telltale
```

## Hermes Agent install

Telltale 0.0.5는 Hermes-native skill surface를 포함한다. Hermes는 installed skill을 slash command로 노출하므로 skill name `sail`은 다음처럼 사용할 수 있다.

```text
/sail <task, SOT, bug report, failing log, or goal>
```

로컬 개발에서는:

```bash
mkdir -p "${HERMES_HOME:-$HOME/.hermes}/skills"
ln -sfn "$(pwd)/hermes/skills/sail" "${HERMES_HOME:-$HOME/.hermes}/skills/sail"
hermes -s sail
```

## Troubleshooting

### `/plugin` command가 없다

Claude Code 버전이 낮거나 plugin support가 꺼져 있을 수 있다.

```bash
claude --version
claude update
```

### `/telltale:sail`이 안 보인다

```bash
claude plugin validate . --strict
python3 scripts/telltalectl.py doctor
claude --plugin-dir .
```

그 다음 Claude Code에서 `/reload-plugins` 후 slash completion을 다시 확인한다.

### `/sail` alias가 안 보인다

아래 surface 중 하나가 설치/로드됐는지 확인한다.

```text
skills/sail/
.claude/commands/sail.md
hermes/skills/sail/SKILL.md
```

### schema validation이 실패한다

```bash
python3 scripts/telltalectl.py validate-schemas
python3 scripts/telltalectl.py doctor
```

helper는 schema를 설치된 package/repository에서 읽고, state는 현재 프로젝트에 쓴다.

### 생성 state가 git에 보인다

`.claude/telltale/`은 generated branch-local state이므로 추적하면 안 된다. 이 repo의 `.gitignore`는 해당 경로를 포함하고, `doctor`가 이를 확인한다.

## M1 범위

포함:

- `/telltale:sail`
- `/sail` local / installed skill / Hermes alias
- destination extraction
- island map
- island scorecard
- cheapest useful island selection
- Cartographer / Sailor / Inspector / Advisor
- current island execution
- verification
- residual analysis
- signal classification
- island close
- verified route carry-forward
- re-chart on drift
- event trace
- convergence report
- doctor diagnostics
- CI validation

제외:

- meta-feedback
- loop-memory 또는 cross-run learning
- model-routing UI
- worktree isolation
- automatic rule promotion
- background daemon
- 새 공개 명령 `/telltale:converge`
