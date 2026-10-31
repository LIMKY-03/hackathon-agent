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
- Codex 내장 멀티에이전트 실행과 순차 실행 대체 경로 지원
- 허용 모델 4종만 통과시키는 화이트리스트
- Computer Use와 브라우저 자동화 기능을 실행 명령에서 강제로 비활성화
- 외부 AI API 키 환경변수 감지 시 실행 중단
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

Astra와 그 밖의 모델은 코드에서 거부됩니다. 내장 멀티에이전트 모드에서는
한 실행의 서브에이전트들이 루트와 같은 모델을 사용합니다. 역할별 모델
라우팅이 필요할 때만 `--mode sequential`을 사용합니다.

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

## 라이선스

MIT

