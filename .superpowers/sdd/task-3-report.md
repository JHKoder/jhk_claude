# Task 3 Report: 품질 평가 로직 구현

## Status: DONE_WITH_CONCERNS

## 완료된 작업

- `.experiment/quality_metrics.py` 생성: `QualityEvaluator` 클래스 및 `evaluate_session()` 함수
- `.experiment/test_quality_metrics.py` 생성: 4개 테스트 케이스
- git commit: `5e9aa64`

## 수정 사항 (brief 대비)

`calculate_complexity_score()`의 tasks.json 경로를 상대경로(`'.experiment/config/tasks.json'`)에서 `Path(__file__).parent / 'config' / 'tasks.json'`으로 변경. `.experiment/` 디렉토리에서 실행 시 상대경로가 틀림.

## 우려사항

pytest 미설치로 테스트 실행 불가 (`No module named pytest`). pip install 권한도 없음. 로직은 정상이나 실행 검증 미완료.

테스트 실행을 위해 다음 중 하나 필요:
- `pip install pytest --break-system-packages` (수동)
- 프로젝트 venv 설정
