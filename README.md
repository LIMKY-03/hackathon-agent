# Hackathon Agent

대회 플랫폼이 제공하는 **Codex CLI만** 사용하여 과제 명세를 분석하고,
`planner → implementer → tester → reviewer → packager` 역할로 작업을 분배하는
범용 멀티에이전트 프레임워크입니다. OpenRouter나 외부 모델 API를 호출하지
않으며 Python 표준 라이브러리 외의 런타임 의존성이 없습니다.

이 공개 저장소에는 사전에 작성된 범용 코드와 예시만 있습니다. 실제 대회
문제, 파일, 풀이, 결과물 또는 후속 서술형 답변은 포함하지 않습니다.

## 핵심 기능

- 주제, 요구사항, 제약, 최종 제출물, 평가 기준을 `TASK.json`으로 입력
- 요구사항 ID와 추적표를 만들고 5개 역할에 동적으로 배분
- Planner가 원본 데이터를 읽기 전용으로 분석하고 edge case를 정리한 뒤 MVP 설계
- 모든 역할에 Fast 서비스 속도를 기본 요청 (`--speed fast`)
- Codex 내장 멀티에이전트 실행과 순차 실행 대체 경로 지원
- 허용 모델 4종만 통과시키는 화이트리스트
- Computer Use와 브라우저 자동화 기능을 실행 명령에서 강제로 비활성화
- 키 관련 환경변수가 있어도 실행을 계속하며, 값·변수명을 출력하지 않는 일반 안내만 표시
- 제출 후 AI 사용을 차단하는 로컬 잠금 명령
- 실제 명령을 실행하지 않고 준비 상태를 점검하는 `--dry-run`
- 표준 라이브러리 `unittest` 테스트 제공

## 허용 모델

| 화면 표시 | CLI 모델 ID | 권장 역할 |
|---|---|---|
| Sol 6.1 | `gpt-6.1-sol` | 기본 총괄, 계획, 최종 검토 |
| Terra 5.6 | `gpt-5.6-terra` | 구현 |
| Luna 6 | `gpt-6-luna` | 빠른 검사, 패키징 |
| Sol 6.0 | `gpt-6-sol` | 테스트, 대체 총괄 |

Astra와 그 밖의 모델은 실행 모델 화이트리스트에서 거부됩니다. 현재 기본
멀티에이전트 프롬프트는 서브에이전트별 모델을 명시하지 않으므로 환경의
기본값을 따릅니다. 별도 설정이 없다면 부모 모델을 상속합니다. 최신 Codex는
서브에이전트별 모델 지정도 지원하지만 CofA 버전과 권한을 확인해야 합니다.
이 프레임워크의 `--mode sequential`은 프로필의 역할별 모델을 명시적으로
전달합니다. 두 모델의 독립 분석·교차 검토 절차는 [계획 안내](PLANNING_GUIDE_KO.md)를 참고하세요.

## 개발 전 데이터 분석

Planner는 먼저 제공 파일의 구조·타입·키·단위·날짜와 관계를 확인하고,
결측·중복·잘못된 형식·범위·참조 오류 등을 조사하도록 지시받습니다.
원본은 보존하며, 표본 분석은 전체 분석과 구분합니다. 데이터가 없는 과제는
그 사실을 기록합니다. 이 과정은 모델에 주는 작업 지침이며 별도의 자동 데이터
검사 엔진이나 보고서 내용의 강제 검증 기능은 아닙니다.

- `.cofa/data-audit.md`: 조사 근거, 관찰 결과, 가정, 미해결 질문
- `.cofa/edge-cases.md`: 예외 조건, 처리 규칙, 예상 화면/API 동작, 테스트 방법

Implementer는 두 문서를 읽고 구현하고 Tester는 예외 조건을 테스트합니다.

## Fast 속도 기본 적용

모든 `run` 실행에 `--enable fast_mode -c 'service_tier="fast"'`를 전달합니다.
작업 폴더가 저장소 밖이어도 적용되도록 CLI 인자로 지정하며, 저장소 내 대화형
Codex용 `.codex/config.toml`에도 같은 기본값을 넣었습니다. 서브에이전트의
서비스 속도는 부모 설정을 따릅니다. 모델이나 추론 강도는 변경하지 않습니다.

`--profile fast`는 역할별 **모델 배정**, `--speed fast`는 **서비스 속도**로
서로 다른 설정입니다. Fast 사용 가능 여부와 실제 속도는 플랫폼·모델에
따라 다르며 사용량 소모가 늘 수 있습니다. 지원하지 않으면 오류 내용을 확인하고
`--speed standard`로 실행하세요. 자동으로 다른 모델이나 서비스로 전환하지 않습니다.

```bash
python -m cofa_orchestrator run --workspace .. --mode multi-agent --speed fast
```

## 빠른 시작

### 1. 공개 저장소 복제

```bash
cd ~
git clone https://github.com/LIMKY-03/hackathon-agent.git
cd hackathon-agent
```

### 2. 자체 테스트

```bash
python -m unittest discover -s tests -v
```

### 3. 실제 과제 명세 작성

실제 내용은 대회 환경 안에서만 입력합니다. 아래 예시는 과제 작업 공간이
복제한 저장소의 상위 폴더(`..`)인 경우입니다.

```bash
python -m cofa_orchestrator init \
  --workspace .. \
  --topic "과제 주제" \
  --requirement "필수 조건 1" \
  --requirement "필수 조건 2" \
  --constraint "제약 조건" \
  --output "최종 제출물 1" \
  --acceptance "검증 기준"
```

명령줄 기록에 과제 내용을 남기고 싶지 않다면 인자 없이 실행한 뒤 질문에
직접 입력하고, 생성된 `../TASK.json`을 에디터에서 보완합니다.

```bash
python -m cofa_orchestrator init --workspace ..
```

### 4. 검증과 계획 생성

```bash
python -m cofa_orchestrator validate --workspace ..
python -m cofa_orchestrator plan --workspace .. --profile balanced
```

생성 파일은 `../.cofa/` 아래에만 저장됩니다.

### 5. 실행 전 명령 확인

```bash
python -m cofa_orchestrator run \
  --workspace .. \
  --mode multi-agent \
  --model gpt-6.1-sol \
  --dry-run
```

### 6. 멀티에이전트 실행

```bash
python -m cofa_orchestrator run \
  --workspace .. \
  --mode multi-agent \
  --model gpt-6.1-sol
```

서브에이전트 기능이 제공되지 않거나 안정적이지 않을 때만 순차 대체 경로를
사용합니다.

```bash
python -m cofa_orchestrator run \
  --workspace .. \
  --mode sequential \
  --profile balanced
```

## 제출 직전과 제출 후

제출 전에 `.cofa/handoffs/`의 테스트·검토 기록과 로컬 제출 매니페스트를
확인합니다. 실제 제출을 확정한 직후 다음 명령으로 AI 실행을 잠급니다.

```bash
python -m cofa_orchestrator lock --workspace ..
```

이후 후속 서술형 문제에서는 이 프레임워크, Codex, 외부 브라우저 또는 다른
AI를 사용하지 말고 본인이 직접 답변합니다.

## 안전 설계

환경변수 이름만으로는 플랫폼 제공 키·개인 키·비AI 서비스용 키를 구분할 수
없습니다. 따라서 키 관련 환경변수의 존재는 실행 중단 사유가 아닙니다.
`validate`, `run`은 이름의 존재만 확인해 일반 안내를 stderr에 표시하며,
`status`도 같은 안내만 반환합니다. 키 값은 조회·출력·기록하지 않고
환경변수도 삭제하거나 변경하지 않습니다. 이 안내는 실제 외부 API 사용 여부를
검사하는 기능이 아닙니다. 외부 AI·개인 키 사용 금지 지침은 계속 적용됩니다.

프레임워크는 다음 작업을 구현하지 않습니다.

- GitHub 저장소 생성, `git push`, 파일 업로드 또는 외부 전송
- 외부 AI 서비스/API 호출
- Computer Use, 브라우저 자동화, 원격 제어
- 감독·보안·업로드 제한 우회
- 제출 후 서술형 답변 생성

공개 저장소를 대회 환경으로 가져오는 `git clone`과, 대회 결과를 밖으로
내보내는 `git push`는 전혀 다른 작업입니다. 이 저장소는 전자만 안내합니다.

## 개발자 검증

```bash
python -m unittest discover -s tests -v
python -m cofa_orchestrator --help
python -m cofa_orchestrator run --help
```

Codex의 `AGENTS.md` 처리 방식과 멀티에이전트 동작은 공식 OpenAI 문서를
기준으로 설계했습니다.

- https://developers.openai.com/cookbook/examples/gpt-5/codex_prompting_guide
- https://developers.openai.com/api/docs/guides/responses-multi-agent
- https://learn.chatgpt.com/docs/agent-configuration/subagents
- https://learn.chatgpt.com/docs/agent-configuration/speed

## 라이선스

MIT

