# Task 6: E2E 테스트 및 검증

**Files:**
- Create: `.experiment/test_e2e_quality.py`

**Interfaces:**
- Consumes: 모든 모듈 (store, quality_metrics, server)
- Produces: 검증된 측정 시스템

## Step 1: E2E 테스트 작성

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

## Step 2: 테스트 실행

```bash
cd .experiment
python3 -m pytest test_e2e_quality.py -v
```

## Step 3: Commit

```bash
git add .experiment/test_e2e_quality.py
git commit -m "test: add end-to-end quality metrics pipeline tests"
```
