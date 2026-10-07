# Task 4 Report: 기존 수집 파이프라인 통합

## 완료 항목

### 1. `claude_session_parser.py`에 두 함수 추가

**`extract_task_id_from_session(log_path: str) -> str | None`**
- JSONL 파일을 직접 읽어 첫 `user` 메시지 content에서 `task_a/b/c` 키워드 탐색
- content가 list 형식(tool_result 등)인 경우도 처리

**`parse_session_with_quality(session_id, project_root, transcript_path) -> dict`**
- 기존 `parse_session()` 호출 후 task_id 감지 시 `quality_metrics.evaluate_session()` 실행
- `quality_metrics.py`가 `collectors/` 외부(`.experiment/` 루트)에 있어 `importlib.util`로 동적 임포트
- 반환값: `{**token_totals, "quality": {...}}`

### 2. `store.py`에 `save_quality_metrics_on_stop` 추가

- `quality_metrics.evaluate_session()` 호출 후 `insert_quality_metric()`으로 DB 저장
- `task_config`가 없으면 `None` 반환

## 주요 설계 결정

| 항목 | 결정 |
|------|------|
| `quality_metrics` 임포트 | `importlib.util`로 동적 로드 — `sys.path` 오염 없음 |
| `parse_session_with_quality` 시그니처 | brief의 `log_path` 대신 기존 `parse_session`과 일치하는 `(session_id, project_root, transcript_path)` |
| task_id 탐색 범위 | 첫 user 메시지만 확인 (성능) |

## 변경 파일

- `.experiment/collectors/claude_session_parser.py`
- `.experiment/collectors/store.py`
