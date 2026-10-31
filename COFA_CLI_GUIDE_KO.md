# 사진 속 CofA CLI에서 사용하는 순서

이 문서는 공개 범용 프레임워크를 대회 환경으로 **가져오는 절차**만 설명합니다.
실제 문제나 결과물을 GitHub로 보내지 않습니다.

## 1. 터미널 열기

사진 속 웹 IDE 아래쪽의 `TERMINAL` 탭을 선택합니다. 이미 Codex 대화 입력창에
있다면 셸 터미널로 전환합니다.

## 2. 현재 위치와 파일 확인

```bash
pwd
ls -la
```

과제의 `README.md`가 있는 위치를 기억합니다. 아래에서는 그 위치를 `~`로
가정합니다.

## 3. 공개 저장소 복제

```bash
cd ~
git clone https://github.com/LIMKY-03/cofa-hackathon-agent-orchestrator.git
cd cofa-hackathon-agent-orchestrator
```

공개 저장소이므로 개인 GitHub 토큰이나 로그인이 필요하지 않습니다. `git
push`는 실행하지 않습니다.

## 4. 프레임워크 자체 점검

```bash
python -m unittest discover -s tests -v
python -m cofa_orchestrator --help
```

## 5. 과제 명세 입력

과제 파일이 상위 폴더 `~`에 있다면 `--workspace ..`를 사용합니다.

```bash
python -m cofa_orchestrator init --workspace ..
```

화면 질문에 주제, 가장 중요한 필수 조건, 최종 제출물을 입력한 뒤 에디터에서
`~/TASK.json`을 열어 나머지 `requirements`, `constraints`, `outputs`,
`acceptance_criteria`를 추가합니다.

## 6. 실행 전 검사

```bash
python -m cofa_orchestrator validate --workspace ..
python -m cofa_orchestrator plan --workspace .. --profile balanced
python -m cofa_orchestrator run --workspace .. --mode multi-agent \
  --model gpt-6.1-sol --dry-run
```

오류가 없으면 실제 실행합니다.

```bash
python -m cofa_orchestrator run --workspace .. --mode multi-agent \
  --model gpt-6.1-sol
```

## 7. 화면에서 Codex 모델을 직접 고를 때

Codex 화면의 `/status`로 현재 모델과 작업 디렉터리를 확인하고 `/model`에서
허용된 모델만 선택합니다. 기본 권장은 Sol 6.1입니다. Astra는 선택하지
않습니다.

## 8. 결과 확인과 제출 후 잠금

```bash
ls -la ../.cofa/handoffs
python -m cofa_orchestrator status --workspace ..
```

최종 제출을 확정한 직후:

```bash
python -m cofa_orchestrator lock --workspace ..
```

그 뒤의 서술형 문제에는 AI를 사용하지 않습니다. 실제 문제, 코드, 결과물,
로그를 외부로 전송하거나 `git push`하지 않습니다.

