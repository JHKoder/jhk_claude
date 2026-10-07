# Experiment Tool

Claude Code 세션의 토큰 사용량·비용·품질 지표를 자동 수집해 브라우저 대시보드로 비교하는 도구.

백엔드·프론트·인프라·네이티브·보안·디자인·PD 등 **어느 팀, 어느 언어에도 복붙으로 적용 가능**.

---

## 빠른 시작 (클론 후 2단계)

```bash
# 1. 설치 (최초 1회)
bash .experiment/install.sh

# 2. runner_config.json 에서 팀 빌드 명령 설정
#    (기본값: ./gradlew — 백엔드 이외 팀은 반드시 수정)
vi .experiment/runner_config.json

# 이후 Claude Code 세션이 끝날 때마다 자동 수집
# 대시보드 확인
exp serve
```

---

## 팀별 runner_config.json 예시

`compile` 또는 `test` 가 `null` 이면 해당 단계를 **SKIP** (대시보드에 회색 표시).

```jsonc
// 백엔드 (Gradle)
{ "compile": "./gradlew compileJava -q",
  "test":    "./gradlew test -q",
  "test_parser": "gradle" }

// 프론트엔드 (npm/Jest)
{ "compile": "npm run build --silent",
  "test":    "npm test -- --watchAll=false --passWithNoTests",
  "test_parser": "jest" }

// 프론트엔드 (pnpm)
{ "compile": "pnpm build",
  "test":    "pnpm test -- --watchAll=false --passWithNoTests",
  "test_parser": "jest" }

// Python / 인프라
{ "compile": null,
  "test":    "python -m pytest -q --tb=no",
  "test_parser": "pytest" }

// Terraform / 인프라 (테스트 없음)
{ "compile": "terraform validate -no-color",
  "test":    null,
  "test_parser": null }

// 디자인·PD (코드 변경 없는 팀 — 프롬프트 품질만 추적)
{ "compile": null, "test": null, "test_parser": null }
```

`_examples` 키에도 위 예시들이 모두 포함돼 있어 복사해서 사용할 수 있습니다.

---

## 자동 수집 기준

Stop Hook이 다음 **AND 조건**을 모두 만족할 때만 저장 (`runner_config.json` 에서 임계값 변경 가능):

| 기준 | 기본값 | 의도 |
|------|--------|------|
| turn 수 | ≥ 5 | 단순 질답 제외 |
| output 토큰 | ≥ 500 | 짧은 응답 제외 |
| 파일 변경 | 1개 이상 | 코드 작업 없는 세션 제외 |
| 중복 session_id | 없음 | 재시작 시 이중 저장 방지 |

---

## 명령어

```bash
exp serve              # 실시간 대시보드 (기본 포트 7788)
exp serve 8080         # 포트 지정
exp list               # 수집된 실험 목록
exp show <id>          # 단일 실험 상세
exp compare <a> <b>    # 터미널 A/B 비교
exp rate <id> <1-5>    # 수동 평점

# 태스크 기반 실험 실행 (config/tasks.json 필요)
exp run <name> <claude|opencode> [task-id]
```

---

## 품질 비교 (새로운 기능)

### 시작하기
```bash
# 1. 측정할 작업 선택 (Task A/B/C)
exp list  # 사용 가능한 작업 목록

# 2. Claude Code 세션에서 작업 실행
# "Task A를 구현해줘" 등

# 3. 대시보드에서 결과 확인
exp serve
# http://localhost:7788/quality-comparison
```

### 지표 설명
- **Accuracy**: 테스트 통과율 (%)
- **First Pass**: 첫 응답에서 완성 (1=yes, 0=no)
- **Complexity**: 작업 난이도 (1-10)
- **Quality/Token**: 토큰 대비 품질 효율

### 비교 전략
Task A (간단) → Task B (중간) → Task C (복잡) 순으로 실행하여 난이도별 효율 추적.

---

## 파일 구조

```
.experiment/
├── install.sh                  # 설치 스크립트 (최초 1회)
├── runner_config.json          # 팀별 빌드 명령 설정
├── exp                         # CLI 진입점
├── server.py                   # 실시간 대시보드 서버
├── test_templates.py           # 템플릿 구조 테스트 (표준 라이브러리)
├── compare.py                  # 터미널 비교
├── experiment.db               # SQLite (gitignore 처리됨)
├── templates/
│   ├── dashboard.html          # 메인 대시보드 UI
│   ├── harness.html            # Harness Explorer UI
│   └── snapshot_viewer.html   # .claude 스냅샷 뷰어 (플레이스홀더 치환)
├── collectors/
│   ├── store.py                # DB CRUD
│   ├── claude_session_parser.py  # Claude Code 로그 파싱 (경로 자동)
│   ├── config_snapshot.py      # .claude/ 규칙 스냅샷 (경로 자동)
│   └── analyzer.py             # AI 분석 (Haiku)
└── config/
    └── tasks.json              # 실험 태스크 정의
```

---

## 템플릿 테스트

서버 UI를 수정한 뒤 아래 명령으로 구조 회귀를 검증한다. 외부 의존성 없음.

```bash
python3 .experiment/test_templates.py
```

| 검증 항목 | 대상 파일 |
|---|---|
| `__PLACEHOLDER__` 미치환 여부 | `snapshot_viewer.html` |
| Python f-string 표현식 잔류 | `snapshot_viewer.html` |
| guide 탭 수 ↔ 섹션 수 일치 | `dashboard.html` |
| `switchGuideTab` 인덱스 순차성 | `dashboard.html` |
| 파일 내용 인라인 삽입 방지 (lazy-load) | `snapshot_viewer.html` |
| HTML 기본 구조 (`html/head/body` 쌍) | 3개 템플릿 전체 |
| 서버 라우트 HTTP 상태 | 서버 실행 중일 때만 |

서버가 실행 중이지 않으면 라우트 테스트는 자동 skip된다.

---

## 비용

| 단계 | 토큰 소모 |
|------|-----------|
| Stop Hook / collect | 0 (로컬 스크립트) |
| exp list / serve / compare | 0 (SQLite + Python) |
| **실험 실행 자체** | claude/opencode 세션 비용만 |
| exp analyze (AI 분석) | Haiku 소량 |
