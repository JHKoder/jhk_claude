# Task 4: 기존 수집 파이프라인 통합

**Files:**
- Modify: `.experiment/collectors/claude_session_parser.py`
- Modify: `.experiment/collectors/store.py` (추가 함수)

**Interfaces:**
- Consumes: Claude 세션 로그 (tokens, turns), 테스트 실행 결과
- Produces: `quality_metrics` 테이블에 저장된 평가 데이터

## Step 1: 세션 파서에 품질 평가 훅 추가

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

## Step 2: store.py에 품질 저장 헬퍼 함수 추가

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

## Step 3: Commit

```bash
git add .experiment/collectors/claude_session_parser.py .experiment/collectors/store.py
git commit -m "feat: integrate quality metrics collection into session parsing pipeline"
```
