# Task A: 간단한 리팩토링

## 요구사항
Python 프로젝트에서 중복된 유틸리티 함수 3개를 하나로 통합

### 현재 코드 (before)
```python
# utils.py
def parse_csv(path):
    import csv
    with open(path) as f:
        return list(csv.DictReader(f))

def parse_json(path):
    import json
    with open(path) as f:
        return json.load(f)

def parse_yaml(path):
    import yaml
    with open(path) as f:
        return yaml.safe_load(f)
```

### 요구사항
- 통합 함수 `parse_file(path)` 구현 — 확장자로 자동 포맷 감지
- 기존 함수들은 유지 (backward compat)
- 지원 포맷: csv, json, yaml
- 에러: 미지원 확장자는 ValueError 발생
- 테스트 케이스:
  - `test_parse_file_csv()` - CSV 파일 파싱 성공
  - `test_parse_file_json()` - JSON 파일 파싱 성공
  - `test_parse_file_yaml()` - YAML 파일 파싱 성공
  - `test_parse_file_unsupported()` - .txt 파일은 ValueError 발생

## 성공 기준
- 모든 테스트 통과
- 첫 응답에서 통과하면 first_pass=1, 수정 후 통과하면 first_pass=0
- accuracy = (통과 테스트 수 / 전체 테스트 수) × 100
- complexity_score = 3 (간단한 작업)
