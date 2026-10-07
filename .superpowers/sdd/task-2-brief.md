# Task 2: 테스트 작업 정의 (A/B/C... 3개)

**Files:**
- Create: `.experiment/test_cases/task_a_simple_refactor.md`
- Create: `.experiment/test_cases/task_b_feature_implementation.md`
- Create: `.experiment/test_cases/task_c_architecture_refactor.md`
- Modify: `.experiment/config/tasks.json`

**Interfaces:**
- Consumes: runner_config.json (compile/test 명령어)
- Produces: 각 작업의 명확한 요구사항 + 예상 테스트 시나리오

## Step 1: Task A - 간단한 리팩토링 (20-30분 규모)

Create `.experiment/test_cases/task_a_simple_refactor.md`:

```markdown
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
```

## Step 2: Task B - 기능 구현 (40-60분 규모)

Create `.experiment/test_cases/task_b_feature_implementation.md`:

```markdown
# Task B: 기능 구현 - 간단한 API 엔드포인트

## 요구사항
FastAPI 백엔드에 사용자 데이터 캐싱 레이어 추가

### 현재 코드 (before)
```python
# main.py
from fastapi import FastAPI
app = FastAPI()

@app.get("/users/{user_id}")
def get_user(user_id: int):
    # DB에서 직접 조회
    user = fetch_user_from_db(user_id)
    return user
```

### 요구사항
- Redis/메모리 캐시 레이어 추가 (TTL: 5분)
- 캐시 miss 시 DB 조회, hit 시 캐시 반환
- `GET /users/{user_id}` - 캐시 적용
- `POST /cache-clear` - 전체 캐시 초기화
- 테스트 케이스:
  - `test_get_user_cache_miss()` - 첫 호출은 DB에서, 토큰 저장
  - `test_get_user_cache_hit()` - 두 번째 호출은 캐시에서 (DB 호출 없음)
  - `test_cache_clear()` - POST 후 다시 DB에서 조회
  - `test_cache_expiration()` - 5분 후 자동 만료

## 성공 기준
- 모든 테스트 통과
- complexity_score = 6 (중간 난이도)
```

## Step 3: Task C - 아키텍처 변경 (1.5-2시간 규모)

Create `.experiment/test_cases/task_c_architecture_refactor.md`:

```markdown
# Task C: 아키텍처 변경 - 서비스 계층 분리

## 요구사항
기존 모놀리식 Python 백엔드를 도메인별 서비스 계층으로 리팩토링

### 현재 구조 (before)
```
app.py (1000+ 라인)
├── user 관련 로직
├── product 관련 로직
├── order 관련 로직
├── DB 쿼리
└── 비즈니스 로직 섞임
```

### 요구사항
- `services/user_service.py` - 사용자 도메인 로직 분리
- `services/product_service.py` - 상품 도메인 로직 분리
- `services/order_service.py` - 주문 도메인 로직 분리
- 각 서비스는 명확한 인터페이스만 노출
- 기존 API 엔드포인트는 변경 없음 (역호환성)
- 테스트 케이스:
  - `test_user_service_create()` - 사용자 생성
  - `test_user_service_get()` - 사용자 조회
  - `test_product_service_list()` - 상품 목록
  - `test_order_service_create_with_validation()` - 주문 생성 + 검증
  - `test_api_endpoint_still_works()` - 기존 API 호환성
  - (총 8-10개 테스트)

## 성공 기준
- 모든 테스트 통과
- complexity_score = 9 (복잡한 작업)
```

## Step 4: tasks.json 업데이트

Modify `.experiment/config/tasks.json` — replace entire contents with:

```json
{
  "tasks": [
    {
      "id": "task_a",
      "name": "Task A: 간단한 리팩토링",
      "description": "중복된 파서 함수 통합",
      "complexity": 3,
      "expected_duration_minutes": 25,
      "test_count": 4,
      "project_type": "python",
      "repo": ".experiment/test_cases/task_a"
    },
    {
      "id": "task_b",
      "name": "Task B: 기능 구현",
      "description": "캐싱 레이어 추가",
      "complexity": 6,
      "expected_duration_minutes": 50,
      "test_count": 4,
      "project_type": "python",
      "repo": ".experiment/test_cases/task_b"
    },
    {
      "id": "task_c",
      "name": "Task C: 아키텍처 변경",
      "description": "서비스 계층 분리",
      "complexity": 9,
      "expected_duration_minutes": 90,
      "test_count": 8,
      "project_type": "python",
      "repo": ".experiment/test_cases/task_c"
    }
  ]
}
```

## Step 5: Commit

```bash
git add .experiment/test_cases/ .experiment/config/tasks.json
git commit -m "feat: define three test tasks (A/B/C) for quality comparison"
```
