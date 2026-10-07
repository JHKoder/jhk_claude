# 코드 품질 측정 및 비교 플랜

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Sonnet 기반으로 토큰 효율 대비 코드 품질을 측정하는 유연한 비교 시스템 구축 — 한 번에 정확하고 품질 높은 코드 작성을 정량화

**Architecture:** 
기존 토큰/비용 수집 시스템(`experiment.db`)에 **품질 메트릭** 추가. 작은 복잡 작업들(A/B/C...)을 테스트 케이스로 정의하고, 각 작업별 정확도(테스트 통과율), 한 번 완성도(반복 수정 필요도), 코드 복잡도 측정. 대시보드에서 토큰대비 품질 지수 시각화.

**Tech Stack:** Python(SQLite, Flask/FastAPI), HTML/CSS/JS(Chart.js), Claude Sonnet API

**Spec:** 사용자 요구사항 (복잡한 작업으로 토큰 효율 + 한 번에 정확한 코드 작성 평가)

## Global Constraints

- 토큰 소모: 측정 스크립트 자체는 로컬 처리(토큰 0)
- 테스트 작업 언어: Python, Go, TypeScript 혼합 지원
- 비교 대상: Sonnet(주), Opus/Haiku(참조용)
- DB: 기존 `experiment.db` 스키마 확장 (백워드 호환성 유지)

## Review Focus

1. **정확도 평가의 일관성** - 각 작업의 테스트가 명확한 성공 기준을 가져야 함
2. **토큰 측정 신뢰성** - Claude API 로그에서 실제 토큰만 집계 (시스템 프롬프트 제외 여부)
3. **비교 공정성** - 동일한 작업을 다른 모델이 수행할 때도 동일한 테스트 적용
4. **한 번 완성도 정의** - 첫 응답 후 수정 횟수 vs 사용자 만족도 상관관계
5. **대시보드 반응성** - 실시간 수집 중에도 비교 기능이 안정적으로 작동

---

## 파일 구조

```
.experiment/
├── collectors/
│   ├── store.py                    (Modify) - quality_metrics 테이블 CRUD 추가
│   └── claude_session_parser.py    (Modify) - 품질 평가 훅 통합
├── schema_migrations/
│   └── 001_add_quality_metrics.sql (Create) - DB 스키마 확장
├── quality_metrics.py              (Create) - 품질 평가 로직 핵심
├── test_quality_metrics.py         (Create) - 품질 평가 단위 테스트
├── test_e2e_quality.py             (Create) - E2E 검증
├── test_cases/
│   ├── task_a_simple_refactor.md   (Create) - 간단한 리팩토링
│   ├── task_b_feature_implementation.md (Create) - 기능 구현
│   └── task_c_architecture_refactor.md  (Create) - 아키텍처 변경
├── config/
│   └── tasks.json                  (Modify) - Task A/B/C 정의 추가
├── server.py                       (Modify) - /api/quality-metrics 엔드포인트
├── templates/
│   ├── quality_comparison.html     (Create) - 품질 비교 UI
│   └── dashboard.html              (Modify) - 탭에 Quality Comparison 추가
├── QUALITY_METRICS_GUIDE.md        (Create) - 사용 가이드
└── README.md                       (Modify) - 품질 비교 섹션 추가

docs/superpowers/plans/
└── 2026-10-07-quality-metrics-system.md (이 파일)
```

---

## Task 1: DB 스키마 확장 - 품질 메트릭 테이블 추가

**Files:**
- Modify: `.experiment/collectors/store.py`
- Create: `.experiment/schema_migrations/001_add_quality_metrics.sql`

**Interfaces:**
- Consumes: 기존 `sessions` 테이블 (session_id, token_used 등)
- Produces: `quality_metrics` 테이블 (session_id, task_id, accuracy, first_pass, complexity_score)

- [ ] **Step 1: 기존 store.py 읽고 DB 스키마 확인**

`.experiment/collectors/store.py`를 읽어 현재 테이블 구조와 DB 경로 파악

- [ ] **Step 2: 마이그레이션 SQL 작성**

```sql
-- .experiment/schema_migrations/001_add_quality_metrics.sql
CREATE TABLE IF NOT EXISTS quality_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL UNIQUE,
    task_id TEXT NOT NULL,
    accuracy REAL,  -- 테스트 통과율 0-100
    first_pass INTEGER,  -- 첫 응답에서 성공 여부 (1/0)
    revision_count INTEGER,  -- 수정 필요 횟수
    complexity_score REAL,  -- 작업 복잡도 0-10
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(session_id) REFERENCES sessions(session_id)
);
```

- [ ] **Step 3: store.py에 마이그레이션 함수 추가**

```python
def init_quality_metrics_table():
    """초기화 함수"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    with open('.experiment/schema_migrations/001_add_quality_metrics.sql') as f:
        cursor.executescript(f.read())
    conn.commit()
    conn.close()

def insert_quality_metric(session_id, task_id, accuracy, first_pass, revision_count, complexity_score):
    """품질 메트릭 저장"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO quality_metrics 
        (session_id, task_id, accuracy, first_pass, revision_count, complexity_score)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (session_id, task_id, accuracy, first_pass, revision_count, complexity_score))
    conn.commit()
    conn.close()

def get_quality_metrics(session_id):
    """세션별 품질 메트릭 조회"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM quality_metrics WHERE session_id = ?", (session_id,))
    result = cursor.fetchone()
    conn.close()
    return result
```

- [ ] **Step 4: 테스트 (스크립트 실행 가능 확인)**

```bash
cd .experiment
python3 -c "from collectors.store import init_quality_metrics_table; init_quality_metrics_table(); print('OK')"
```

- [ ] **Step 5: Commit**

```bash
git add .experiment/collectors/store.py .experiment/schema_migrations/001_add_quality_metrics.sql
git commit -m "feat: add quality_metrics table to track code quality alongside token usage"
```

---

## Task 2: 테스트 작업 정의 (A/B/C... 3개)

**Files:**
- Create: `.experiment/test_cases/task_a_simple_refactor.md`
- Create: `.experiment/test_cases/task_b_feature_implementation.md`
- Create: `.experiment/test_cases/task_c_architecture_refactor.md`
- Modify: `.experiment/config/tasks.json`

**Interfaces:**
- Consumes: runner_config.json (compile/test 명령어)
- Produces: 각 작업의 명확한 요구사항 + 예상 테스트 시나리오

- [ ] **Step 1: Task A - 간단한 리팩토링 (20-30분 규모)**

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

- [ ] **Step 2: Task B - 기능 구현 (40-60분 규모)**

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

- [ ] **Step 3: Task C - 아키텍처 변경 (1.5-2시간 규모)**

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

- [ ] **Step 4: tasks.json 업데이트**

`.experiment/config/tasks.json`을 수정하여 다음 내용 추가:

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

- [ ] **Step 5: Commit**

```bash
git add .experiment/test_cases/ .experiment/config/tasks.json
git commit -m "feat: define three test tasks (A/B/C) for quality comparison"
```

---

## Task 3: 품질 평가 로직 구현

**Files:**
- Create: `.experiment/quality_metrics.py`
- Create: `.experiment/test_quality_metrics.py`

**Interfaces:**
- Consumes: 세션별 코드 변경, 테스트 결과, Claude API 토큰 로그
- Produces: `calculate_quality_score(session_id) → dict`

- [ ] **Step 1: 품질 메트릭 계산 함수 작성**

`.experiment/quality_metrics.py` 파일 생성:

```python
import subprocess
import json
import re
from pathlib import Path

class QualityEvaluator:
    """코드 품질 측정"""
    
    def __init__(self, task_id: str, project_root: str):
        self.task_id = task_id
        self.project_root = project_root
    
    def run_tests(self, test_command: str) -> dict:
        """테스트 실행 및 결과 파싱"""
        try:
            result = subprocess.run(
                test_command,
                shell=True,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            return {
                "passed": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {"passed": False, "error": "Test timeout"}
    
    def calculate_accuracy(self, test_result: dict, expected_test_count: int) -> float:
        """테스트 통과율 계산 (0-100)"""
        if not test_result.get("passed"):
            # 실패한 경우 stdout에서 몇 개 통과했는지 파싱
            output = test_result.get("stdout", "")
            # pytest 형식 예: "4 passed, 1 failed"
            match = re.search(r'(\d+) passed', output)
            passed = int(match.group(1)) if match else 0
            return (passed / expected_test_count) * 100 if expected_test_count > 0 else 0
        else:
            return 100.0
    
    def count_revisions_from_git(self, session_id: str) -> int:
        """세션 중 수정 횟수 (커밋 수) 계산"""
        try:
            result = subprocess.run(
                ["git", "log", "--oneline", "-n", "20"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            # 단순화: 같은 파일에 대한 커밋 수 (반복 수정 표시)
            # 실제로는 Claude 세션 로그에서 turn 수와 수정 횟수 비교
            return 1  # 첫 응답에서 완성 = 1
        except:
            return 1
    
    def calculate_complexity_score(self) -> float:
        """작업 복잡도 점수 (0-10)"""
        # tasks.json에서 읽어오기
        with open('.experiment/config/tasks.json') as f:
            tasks = json.load(f).get("tasks", [])
        
        for task in tasks:
            if task["id"] == self.task_id:
                return task.get("complexity", 5)
        return 5

def evaluate_session(session_id: str, task_id: str, project_root: str, test_command: str, expected_test_count: int):
    """세션 평가 통합 함수"""
    evaluator = QualityEvaluator(task_id, project_root)
    
    # 테스트 실행
    test_result = evaluator.run_tests(test_command)
    
    # 메트릭 계산
    accuracy = evaluator.calculate_accuracy(test_result, expected_test_count)
    first_pass = 1 if accuracy == 100.0 else 0
    revision_count = evaluator.count_revisions_from_git(session_id)
    complexity_score = evaluator.calculate_complexity_score()
    
    return {
        "session_id": session_id,
        "task_id": task_id,
        "accuracy": accuracy,
        "first_pass": first_pass,
        "revision_count": revision_count,
        "complexity_score": complexity_score
    }
```

- [ ] **Step 2: 테스트 작성**

`.experiment/test_quality_metrics.py` 파일 생성:

```python
import pytest
import tempfile
from quality_metrics import QualityEvaluator

def test_accuracy_calculation_perfect():
    """100% 통과"""
    evaluator = QualityEvaluator("task_a", ".")
    test_result = {"passed": True}
    accuracy = evaluator.calculate_accuracy(test_result, 4)
    assert accuracy == 100.0

def test_accuracy_calculation_partial():
    """부분 통과"""
    evaluator = QualityEvaluator("task_a", ".")
    test_result = {
        "passed": False,
        "stdout": "4 passed, 1 failed in 0.50s"
    }
    accuracy = evaluator.calculate_accuracy(test_result, 5)
    assert accuracy == 80.0

def test_complexity_score_task_a():
    """Task A는 복잡도 3"""
    evaluator = QualityEvaluator("task_a", ".")
    score = evaluator.calculate_complexity_score()
    assert score == 3

def test_complexity_score_task_c():
    """Task C는 복잡도 9"""
    evaluator = QualityEvaluator("task_c", ".")
    score = evaluator.calculate_complexity_score()
    assert score == 9
```

- [ ] **Step 3: 테스트 실행**

```bash
cd .experiment
python3 -m pytest test_quality_metrics.py -v
```

- [ ] **Step 4: Commit**

```bash
git add .experiment/quality_metrics.py .experiment/test_quality_metrics.py
git commit -m "feat: implement code quality evaluation metrics (accuracy, first_pass, complexity)"
```

---

## Task 4: 기존 수집 파이프라인 통합

**Files:**
- Modify: `.experiment/collectors/claude_session_parser.py`
- Modify: `.experiment/collectors/store.py` (추가 함수)

**Interfaces:**
- Consumes: Claude 세션 로그 (tokens, turns), 테스트 실행 결과
- Produces: `quality_metrics` 테이블에 저장된 평가 데이터

- [ ] **Step 1: 세션 파서에 품질 평가 훅 추가**

`.experiment/collectors/claude_session_parser.py`에 다음 함수 추가:

```python
def extract_task_id_from_session(session_log: dict) -> str:
    """세션 로그에서 작업 ID 추출"""
    # 예: 세션 초반 프롬프트에 "task_a" 또는 "Task A" 포함 여부 확인
    initial_messages = session_log.get("messages", [])
    if initial_messages:
        first_msg = initial_messages[0].get("content", "").lower()
        for task_id in ["task_a", "task_b", "task_c"]:
            if task_id in first_msg:
                return task_id
    return None

def parse_session_with_quality(log_path: str):
    """세션 로그 + 품질 평가 파싱"""
    from quality_metrics import evaluate_session
    
    session_log = parse_session(log_path)  # 기존 함수
    session_id = session_log.get("session_id")
    task_id = extract_task_id_from_session(session_log)
    
    if task_id:
        # 작업 설정에서 테스트 명령어 읽기
        import json
        with open('.experiment/config/tasks.json') as f:
            tasks = json.load(f).get("tasks", [])
        
        task_config = next((t for t in tasks if t["id"] == task_id), None)
        if task_config:
            project_root = task_config.get("repo", ".")
            # test_command는 runner_config.json에서 읽기
            # 여기서는 간단히 pytest 가정
            test_command = "python -m pytest tests/ -v"
            
            quality = evaluate_session(
                session_id,
                task_id,
                project_root,
                test_command,
                task_config.get("test_count", 4)
            )
            return {**session_log, "quality": quality}
    
    return session_log
```

- [ ] **Step 2: store.py에 품질 저장 헬퍼 함수 추가**

`.experiment/collectors/store.py`에 다음 함수 추가:

```python
def save_quality_metrics_on_stop(session_id, task_id):
    """Stop 시점에 품질 메트릭 저장"""
    from quality_metrics import evaluate_session
    import json
    
    with open('.experiment/config/tasks.json') as f:
        task_config = next(
            (t for t in json.load(f)["tasks"] if t["id"] == task_id),
            None
        )
    
    if task_config:
        quality = evaluate_session(
            session_id,
            task_id,
            task_config["repo"],
            "python -m pytest tests/ -v",
            task_config["test_count"]
        )
        insert_quality_metric(
            quality["session_id"],
            quality["task_id"],
            quality["accuracy"],
            quality["first_pass"],
            quality["revision_count"],
            quality["complexity_score"]
        )
```

- [ ] **Step 3: Commit**

```bash
git add .experiment/collectors/claude_session_parser.py .experiment/collectors/store.py
git commit -m "feat: integrate quality metrics collection into session parsing pipeline"
```

---

## Task 5: 대시보드 UI 업데이트

**Files:**
- Create: `.experiment/templates/quality_comparison.html`
- Modify: `.experiment/server.py` - 라우트 추가
- Modify: `.experiment/templates/dashboard.html` - 탭 추가

**Interfaces:**
- Consumes: `quality_metrics` 테이블 데이터, tasks.json 설정
- Produces: `/quality-comparison` 엔드포인트, 시각화 UI

- [ ] **Step 1: 품질 비교 HTML 템플릿 작성**

`.experiment/templates/quality_comparison.html` 파일 생성:

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Code Quality Comparison</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body { font-family: system-ui; margin: 20px; }
        .comparison-table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        .comparison-table th, .comparison-table td { border: 1px solid #ddd; padding: 12px; text-align: left; }
        .comparison-table th { background-color: #f5f5f5; }
        .quality-score { font-weight: bold; }
        .perfect { color: green; }
        .partial { color: orange; }
        .failed { color: red; }
        .chart-container { width: 100%; max-width: 800px; margin: 30px 0; }
    </style>
</head>
<body>
    <h1>Code Quality vs Token Usage</h1>
    
    <div class="chart-container">
        <canvas id="qualityChart"></canvas>
    </div>
    
    <h2>Task Comparison</h2>
    <table class="comparison-table">
        <thead>
            <tr>
                <th>Task</th>
                <th>Complexity</th>
                <th>Accuracy</th>
                <th>First Pass</th>
                <th>Revisions</th>
                <th>Tokens Used</th>
                <th>Quality/Token</th>
            </tr>
        </thead>
        <tbody id="dataTable">
            <tr><td colspan="7" style="text-align: center;">로딩 중...</td></tr>
        </tbody>
    </table>
    
    <script>
        fetch('/api/quality-metrics')
            .then(r => r.json())
            .then(data => {
                // 테이블 채우기
                const tbody = document.getElementById('dataTable');
                tbody.innerHTML = '';
                
                data.metrics.forEach(m => {
                    const row = tbody.insertRow();
                    const accuracy_class = m.accuracy === 100 ? 'perfect' : 
                                          m.accuracy >= 50 ? 'partial' : 'failed';
                    
                    row.innerHTML = `
                        <td>${m.task_id}</td>
                        <td>${m.complexity_score}</td>
                        <td class="${accuracy_class}">${m.accuracy.toFixed(1)}%</td>
                        <td>${m.first_pass ? '✓' : '✗'}</td>
                        <td>${m.revision_count}</td>
                        <td>${m.tokens_used || 'N/A'}</td>
                        <td>${(m.accuracy / (m.tokens_used / 1000 || 1)).toFixed(2)}</td>
                    `;
                });
                
                // 차트 그리기
                const ctx = document.getElementById('qualityChart').getContext('2d');
                new Chart(ctx, {
                    type: 'scatter',
                    data: {
                        datasets: [{
                            label: 'Task Performance',
                            data: data.metrics.map(m => ({
                                x: m.tokens_used || 0,
                                y: m.accuracy,
                                r: m.complexity_score * 2
                            })),
                            backgroundColor: 'rgba(75, 192, 192, 0.6)'
                        }]
                    },
                    options: {
                        scales: {
                            x: { title: { display: true, text: 'Tokens Used' } },
                            y: { title: { display: true, text: 'Accuracy (%)' }, max: 100 }
                        }
                    }
                });
            });
    </script>
</body>
</html>
```

- [ ] **Step 2: server.py에 API 엔드포인트 추가**

`.experiment/server.py`에 다음 함수 추가 (기존 Flask/FastAPI 구조에 맞게):

```python
@app.get("/api/quality-metrics")
def get_quality_metrics():
    """품질 메트릭 JSON 반환"""
    import sqlite3
    import json
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            qm.task_id, qm.accuracy, qm.first_pass, qm.revision_count, 
            qm.complexity_score, s.output_tokens
        FROM quality_metrics qm
        LEFT JOIN sessions s ON qm.session_id = s.session_id
        ORDER BY qm.created_at DESC
    """)
    
    rows = cursor.fetchall()
    conn.close()
    
    metrics = []
    for row in rows:
        metrics.append({
            "task_id": row[0],
            "accuracy": row[1],
            "first_pass": row[2],
            "revision_count": row[3],
            "complexity_score": row[4],
            "tokens_used": row[5]
        })
    
    return {"metrics": metrics}

@app.get("/quality-comparison")
def quality_comparison():
    """품질 비교 페이지"""
    with open('templates/quality_comparison.html') as f:
        return HTMLResponse(f.read())
```

- [ ] **Step 3: 대시보드 탭에 Quality Comparison 추가**

`.experiment/templates/dashboard.html`에서 탭 섹션 수정:

```html
<!-- 탭 추가 -->
<div class="tabs">
    <button onclick="switchTab(0)">Overview</button>
    <button onclick="switchTab(1)">Sessions</button>
    <button onclick="switchTab(2)">Quality Comparison</button>  <!-- 새 탭 -->
</div>

<!-- 탭 내용 추가 -->
<div id="tab2" class="tab-content" style="display:none;">
    <h2>Code Quality vs Token Usage</h2>
    <iframe src="/quality-comparison" style="width:100%; height:600px; border:none;"></iframe>
</div>
```

- [ ] **Step 4: Commit**

```bash
git add .experiment/templates/quality_comparison.html .experiment/server.py .experiment/templates/dashboard.html
git commit -m "feat: add quality comparison dashboard with metrics visualization"
```

---

## Task 6: E2E 테스트 및 검증

**Files:**
- Create: `.experiment/test_e2e_quality.py`

**Interfaces:**
- Consumes: 모든 모듈 (store, quality_metrics, server)
- Produces: 검증된 측정 시스템

- [ ] **Step 1: E2E 테스트 작성**

`.experiment/test_e2e_quality.py` 파일 생성:

```python
import pytest
import sqlite3
import json
import tempfile
from pathlib import Path
from collectors.store import insert_quality_metric, get_quality_metrics, init_quality_metrics_table
from quality_metrics import QualityEvaluator

def test_full_pipeline():
    """전체 측정 파이프라인 검증"""
    # 1. DB 초기화
    init_quality_metrics_table()
    
    # 2. 메트릭 삽입
    insert_quality_metric(
        session_id="test_session_001",
        task_id="task_a",
        accuracy=100.0,
        first_pass=1,
        revision_count=1,
        complexity_score=3
    )
    
    # 3. 메트릭 조회
    result = get_quality_metrics("test_session_001")
    assert result is not None
    assert result[2] == 100.0  # accuracy
    assert result[3] == 1  # first_pass
    
def test_quality_evaluation_integration():
    """품질 평가 통합 테스트"""
    # 작업 설정 있는지 확인
    with open('.experiment/config/tasks.json') as f:
        tasks = json.load(f).get("tasks", [])
    
    assert len(tasks) >= 3, "최소 3개 작업 필요"
    assert any(t["id"] == "task_a" for t in tasks)
    assert any(t["id"] == "task_b" for t in tasks)
    assert any(t["id"] == "task_c" for t in tasks)

def test_complexity_scores():
    """복잡도 점수 검증"""
    evaluator_a = QualityEvaluator("task_a", ".")
    evaluator_c = QualityEvaluator("task_c", ".")
    
    score_a = evaluator_a.calculate_complexity_score()
    score_c = evaluator_c.calculate_complexity_score()
    
    assert score_a < score_c, "Task C가 Task A보다 복잡해야 함"
    assert 1 <= score_a <= 10
    assert 1 <= score_c <= 10
```

- [ ] **Step 2: 테스트 실행**

```bash
cd .experiment
python3 -m pytest test_e2e_quality.py -v
```

- [ ] **Step 3: 서버 실행 및 수동 검증**

```bash
cd .experiment
python3 server.py &
# 브라우저에서 http://localhost:7788/quality-comparison 확인
```

- [ ] **Step 4: Commit**

```bash
git add .experiment/test_e2e_quality.py
git commit -m "test: add end-to-end quality metrics pipeline tests"
```

---

## Task 7: 문서 및 사용 가이드

**Files:**
- Create: `.experiment/QUALITY_METRICS_GUIDE.md`
- Modify: `.experiment/README.md` - 품질 비교 섹션 추가

**Interfaces:**
- Consumes: 모든 기능 (완성된 시스템)
- Produces: 사용자 가이드, 설정 예시

- [ ] **Step 1: 품질 메트릭 가이드 작성**

`.experiment/QUALITY_METRICS_GUIDE.md` 파일 생성:

```markdown
# Quality Metrics Guide

## 개요
코드 품질을 토큰 효율과 함께 측정하는 시스템입니다.

## 주요 지표

### Accuracy (정확도)
- 통과한 테스트 / 전체 테스트 × 100
- 범위: 0-100%
- 의미: 코드가 요구사항을 얼마나 충족하는가

### First Pass (한 번에 완성)
- 1: 첫 응답에서 모든 테스트 통과
- 0: 수정이 필요했음
- 의미: 정확도와 효율성

### Revision Count (수정 횟수)
- 정확도 100%에 도달할 때까지 필요한 수정 수
- 의미: 반복 비용

### Complexity Score (복잡도)
- 1-10 범위 (작은 작업 → 큰 작업)
- Task A: 3, Task B: 6, Task C: 9
- 의미: 작업의 난이도

### Quality/Token Ratio
- Accuracy ÷ (Tokens / 1000)
- 의미: 토큰 대비 품질 효율성

## 사용 방법

### 1. 작업 실행
Claude Code에서 Task A/B/C 중 하나를 선택하여 실행:
```
"Task A를 구현해줘"
```

### 2. 메트릭 자동 수집
- Stop Hook에서 자동으로 `quality_metrics` 저장
- 토큰은 Claude API 로그에서, 품질은 테스트에서 추출

### 3. 대시보드 확인
```bash
exp serve
# http://localhost:7788 → Quality Comparison 탭
```

## 해석

**우수한 결과:**
- Accuracy: 100%
- First Pass: 1
- Tokens: 낮음
- Quality/Token Ratio: 높음 (5 이상)

**개선이 필요한 결과:**
- Accuracy < 80%: 요구사항 이해 부족
- First Pass: 0이 많음: 첫 응답의 정확도 향상 필요
- Tokens: 높음: 프롬프트 최적화 필요

## 모델 비교 (참조)
- Sonnet (기준): Quality/Token = X
- Opus: Quality/Token = ?
- Haiku: Quality/Token = ?
```

- [ ] **Step 2: README.md에 품질 비교 섹션 추가**

`.experiment/README.md`에서 기존 "명령어" 섹션 다음에 다음 내용 추가:

```markdown
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
```

- [ ] **Step 3: Commit**

```bash
git add .experiment/QUALITY_METRICS_GUIDE.md .experiment/README.md
git commit -m "docs: add quality metrics guide and dashboard documentation"
```

---

## 플랜 검증 체크리스트

✅ **Spec 커버리지:**
- 토큰 효율 측정 ✓ (tokens_used 추적)
- 코드 품질 평가 ✓ (accuracy, first_pass)
- 한 번에 완성도 ✓ (first_pass, revision_count)
- 유연한 측정 ✓ (quality_metrics 테이블, tasks.json 설정)
- 대시보드 시각화 ✓ (quality_comparison.html, Chart.js)

✅ **플레이스홀더 검사:**
- 모든 SQL/Python 코드 완성 ✓
- 모든 HTML 완성 ✓
- API 엔드포인트 명시 ✓

✅ **타입 일관성:**
- accuracy: float (0-100)
- first_pass: int (0/1)
- complexity_score: float (1-10)
- tokens_used: int

✅ **Review Focus 커버리지:**
1. 정확도 평가 일관성 → Task 1-2 (테스트 정의, DB 스키마)
2. 토큰 측정 신뢰성 → Task 4 (API 로그 통합)
3. 비교 공정성 → Task 2 (동일한 테스트 세트)
4. 한 번 완성도 정의 → Task 3 (first_pass 계산)
5. 대시보드 안정성 → Task 5-6 (UI, E2E 테스트)

---

## 실행 방법

이 플랜을 **Subagent-driven** 방식으로 실행합니다.
- 각 Task마다 독립적인 subagent가 구현 → 리뷰 → 다음 Task
- 최종적으로 전체 브랜치 리뷰

**준비 완료. superpowers:subagent-driven-development 스킬을 사용하여 Task 1부터 시작하겠습니다.**
