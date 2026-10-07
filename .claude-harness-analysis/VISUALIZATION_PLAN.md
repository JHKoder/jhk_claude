# Claude Harness Engineering — Git I/O 시각화 계획

## 개요

Task 1-6 진행 중 생성되는 로그 및 분석 자료를 **Git I/O 대시보드에서 실시간으로 볼 수 있게** 구성.

---

## 1. 데이터 수집 & 저장 구조

### 1.1 로그 파일 생성 (Task 진행 중)

```
.claude-harness-analysis/
├── logs/
│   ├── task-1-baseline.log          # Task 1 실행 로그 (타임스탬프)
│   ├── task-2-variant-a.log         # Task 2 실행 로그
│   ├── task-3-variant-b.log         # Task 3 실행 로그
│   ├── task-4-variant-c.log         # Task 4 실행 로그
│   ├── task-5-consolidation.log     # Task 5 실행 로그
│   └── task-6-hooks.log             # Task 6 실행 로그
├── metrics/
│   ├── token-baseline.json          # 기준점 토큰 측정
│   ├── token-variant-a.json         # Variant A 토큰 측정
│   ├── token-variant-b.json         # Variant B 토큰 측정
│   ├── token-variant-c.json         # Variant C 토큰 측정
│   ├── token-master.json            # 최종 마스터 토큰 측정
│   └── clarity-scores.json          # 명확성 점수 (0-100)
└── reports/
    ├── task-1-report.md             # Task 1 완료 보고서
    ├── task-2-report.md             # Task 2 완료 보고서
    ├── task-3-report.md             # Task 3 완료 보고서
    ├── task-4-report.md             # Task 4 완료 보고서
    ├── task-5-report.md             # Task 5 완료 보고서
    └── task-6-report.md             # Task 6 완료 보고서
```

### 1.2 메트릭 JSON 형식 (각 Task 후 업데이트)

```json
{
  "task_id": "task-1",
  "task_name": "Baseline Analysis",
  "timestamp": "2026-10-07T10:30:00Z",
  "status": "completed",
  "metrics": {
    "token_cost": 3640,
    "clarity_score": 72,
    "lines_of_code": 26,
    "word_count": 385,
    "undefined_terms": 7,
    "overlapping_rules": 3
  },
  "duration_minutes": 28,
  "commits": ["abc1234"],
  "files_created": [
    ".claude-harness-analysis/baseline-metrics.json",
    ".claude-harness-analysis/semantic-audit.md"
  ]
}
```

---

## 2. Git I/O 대시보드 확장

### 2.1 새 탭: "Harness Engineering"

**위치**: `docs/index.html`에 새 섹션 추가

```html
<!-- docs/index.html에 추가 -->

<div class="content">
  <!-- 기존 섹션들... -->
  
  <!-- 새 섹션: Harness Engineering -->
  <div class="section">
    <h2>🔧 Harness Engineering Progress</h2>
    
    <!-- Progress Bar -->
    <div class="progress-container">
      <div class="progress-bar" id="harness-progress"></div>
      <span id="progress-text">0/6 Tasks Complete</span>
    </div>
    
    <!-- Task Timeline -->
    <div class="task-timeline">
      <div class="task-item completed" id="task-1">
        <h3>✓ Task 1: Baseline Analysis</h3>
        <p>Token cost baseline: 3640 | Clarity: 72/100</p>
        <small>Completed: 2026-10-07 10:30</small>
      </div>
      <div class="task-item pending" id="task-2">
        <h3>⏳ Task 2: Variant A</h3>
        <p>Syntax polish...</p>
      </div>
      <!-- Task 3-6 반복 -->
    </div>
    
    <!-- Token Cost Comparison Chart -->
    <div class="chart-container">
      <canvas id="token-chart"></canvas>
    </div>
    
    <!-- Clarity Score Chart -->
    <div class="chart-container">
      <canvas id="clarity-chart"></canvas>
    </div>
    
    <!-- Latest Report -->
    <div class="latest-report">
      <h3>Latest Report</h3>
      <iframe src="task-1-report.md" width="100%" height="400px"></iframe>
    </div>
  </div>
</div>
```

### 2.2 자동 업데이트 스크립트

**`docs/update-harness-dashboard.sh`** (Task 완료 후 자동 실행)

```bash
#!/bin/bash

# Task 완료 로그를 JSON 메트릭으로 변환
TASK_ID=$1
LOG_FILE=".claude-harness-analysis/logs/task-${TASK_ID}.log"
METRIC_FILE=".claude-harness-analysis/metrics/task-${TASK_ID}-metrics.json"

if [ ! -f "$LOG_FILE" ]; then
  echo "Log file not found: $LOG_FILE"
  exit 1
fi

# 로그에서 주요 메트릭 추출
TOKEN_COST=$(grep "Token cost" "$LOG_FILE" | head -1 | grep -oE '[0-9]+' | head -1)
CLARITY=$(grep "Clarity score" "$LOG_FILE" | head -1 | grep -oE '[0-9]+' | tail -1)
DURATION=$(grep "Duration" "$LOG_FILE" | head -1 | grep -oE '[0-9]+' | head -1)

# JSON 생성
cat > "$METRIC_FILE" <<EOF
{
  "task_id": "task-${TASK_ID}",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "token_cost": ${TOKEN_COST:-0},
  "clarity_score": ${CLARITY:-0},
  "duration_minutes": ${DURATION:-0},
  "status": "completed"
}
EOF

echo "✓ Metrics updated: $METRIC_FILE"

# 대시보드 HTML 업데이트
python3 << 'PYTHON'
import json
import os
from pathlib import Path

# 모든 메트릭 JSON 읽기
metrics_dir = Path(".claude-harness-analysis/metrics")
all_tasks = sorted(metrics_dir.glob("task-*.json"))

completed = len([t for t in all_tasks if t.exists()])
total = 6

progress = (completed / total) * 100

# index.html 업데이트 (querySelector 사용)
html_update = f"""
document.getElementById('harness-progress').style.width = '{progress}%';
document.getElementById('progress-text').textContent = '{completed}/6 Tasks Complete';
"""

print("Update JavaScript:")
print(html_update)

PYTHON

# Git 커밋
git add ".claude-harness-analysis/"
git commit -m "chore: update harness engineering metrics for task-${TASK_ID}" || true
```

---

## 3. 시각화 대시보드 구성

### 3.1 4가지 차트 표시

```
┌─────────────────────────────────────────────────────┐
│         🔧 Harness Engineering Progress             │
├─────────────────────────────────────────────────────┤
│ Progress: ████████░░ 80% (5/6 Tasks Complete)      │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│         📊 Token Cost Trend                         │
├─────────────────────────────────────────────────────┤
│  3700 │                                             │
│  3650 │ ●(baseline:3640)                           │
│  3600 │    ●(A:3635) ●(B:3642) ●(C:3586)        │
│  3550 │                            ●(master:3586)  │
│       └────────────────────────────────────────    │
│       Baseline    A      B      C     Master       │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│         ✨ Clarity Score (0-100)                    │
├─────────────────────────────────────────────────────┤
│ Baseline:  ████████░░ 72/100                       │
│ Variant A: ████████░░ 78/100 (+6)                  │
│ Variant B: █████████░ 85/100 (+13)                 │
│ Variant C: ████████░░ 77/100 (+5)                  │
│ Master:    █████████░ 86/100 (+14)                 │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│         ⏱️ Task Duration (minutes)                   │
├─────────────────────────────────────────────────────┤
│ Task 1: ███░░░ 28 min                              │
│ Task 2: ████░░ 42 min                              │
│ Task 3: █████░ 58 min                              │
│ Task 4: █████░ 59 min                              │
│ Task 5: ██████ 87 min                              │
│ Task 6: ████░░ 45 min                              │
└─────────────────────────────────────────────────────┘
```

### 3.2 실시간 Task 타임라인

```html
<div class="task-timeline">
  <div class="task-card completed">
    <span class="status">✓ COMPLETE</span>
    <h3>Task 1: Baseline Analysis</h3>
    <div class="metrics">
      <span>📊 Token: 3640</span>
      <span>✨ Clarity: 72</span>
      <span>⏱️ 28 min</span>
    </div>
    <a href=".claude-harness-analysis/task-1-report.md">📄 Report</a>
  </div>
  
  <div class="task-card in-progress">
    <span class="status">⏳ IN PROGRESS</span>
    <h3>Task 2: Variant A</h3>
    <div class="metrics">
      <span>📊 Token: ... (measuring)</span>
      <span>✨ Clarity: ...</span>
      <span>⏱️ Started: 10:45</span>
    </div>
    <a href=".claude-harness-analysis/logs/task-2-variant-a.log">📝 Live Log</a>
  </div>
</div>
```

---

## 4. GitHub Actions 자동화

### 4.1 새로운 Workflow: `harness-analysis-report.yml`

```yaml
name: Harness Engineering Report

on:
  push:
    paths:
      - '.claude-harness-analysis/**'
      - 'plan.md'
  workflow_dispatch:

jobs:
  generate-harness-report:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Analyze Harness Metrics
        run: |
          python3 << 'EOF'
          import json
          from pathlib import Path
          
          # 메트릭 수집
          metrics_dir = Path(".claude-harness-analysis/metrics")
          all_metrics = []
          
          for metric_file in sorted(metrics_dir.glob("*.json")):
              with open(metric_file) as f:
                  all_metrics.append(json.load(f))
          
          # 요약 보고서 생성
          summary = {
              "total_tasks": 6,
              "completed": len(all_metrics),
              "metrics": all_metrics,
              "timestamp": __import__('datetime').datetime.utcnow().isoformat()
          }
          
          with open(".claude-harness-analysis/summary.json", "w") as f:
              json.dump(summary, f, indent=2)
          
          print(f"✓ Analysis complete: {len(all_metrics)}/6 tasks")
          EOF

      - name: Update Dashboard
        run: |
          # Git I/O 대시보드 업데이트
          python3 docs/update-harness-dashboard.py \
            --metrics .claude-harness-analysis/metrics \
            --output docs/index.html

      - name: Commit Updates
        run: |
          git config user.name "Harness Bot"
          git config user.email "noreply@github.com"
          git add .claude-harness-analysis/ docs/
          git commit -m "chore: update harness engineering dashboard" || true
          git push
```

### 4.2 대시보드 업데이트 Python 스크립트

**`docs/update-harness-dashboard.py`**

```python
#!/usr/bin/env python3

import json
import argparse
from pathlib import Path
from datetime import datetime

def load_all_metrics(metrics_dir):
    """모든 메트릭 JSON 로드"""
    metrics = {}
    for metric_file in sorted(Path(metrics_dir).glob("*.json")):
        with open(metric_file) as f:
            data = json.load(f)
            metrics[metric_file.stem] = data
    return metrics

def generate_html_update(metrics):
    """HTML 업데이트 코드 생성"""
    completed = len(metrics)
    progress = (completed / 6) * 100
    
    # Task 목록 생성
    task_html = ""
    for i in range(1, 7):
        task_key = f"task-{i}"
        if task_key in metrics:
            data = metrics[task_key]
            token = data.get("token_cost", "N/A")
            clarity = data.get("clarity_score", "N/A")
            task_html += f"""
            <div class="task-card completed">
              <span class="status">✓ Complete</span>
              <h3>Task {i}</h3>
              <p>Token: {token} | Clarity: {clarity}/100</p>
            </div>
            """
        else:
            task_html += f"""
            <div class="task-card pending">
              <span class="status">⏳ Pending</span>
              <h3>Task {i}</h3>
              <p>Waiting...</p>
            </div>
            """
    
    return f"""
    <script>
    document.getElementById('harness-progress').style.width = '{progress}%';
    document.getElementById('progress-text').innerHTML = '{completed}/6 Tasks Complete';
    document.getElementById('task-list').innerHTML = `{task_html}`;
    </script>
    """

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--metrics", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    
    metrics = load_all_metrics(args.metrics)
    update_script = generate_html_update(metrics)
    
    # 대시보드 HTML 업데이트
    print(update_script)
    print(f"✓ Dashboard update generated for {len(metrics)} metrics")

if __name__ == "__main__":
    main()
```

---

## 5. 구현 체크리스트

### Phase 1: 데이터 구조 (Task 진행 중)
- [ ] `.claude-harness-analysis/logs/` 디렉토리 생성
- [ ] `.claude-harness-analysis/metrics/` 디렉토리 생성
- [ ] `.claude-harness-analysis/reports/` 디렉토리 생성
- [ ] 각 Task 완료 후 `task-N.log` 생성 (자동)
- [ ] 각 Task 완료 후 `task-N-metrics.json` 생성 (자동)

### Phase 2: 대시보드 통합 (Task 5 중)
- [ ] `docs/index.html` 새 섹션 "Harness Engineering" 추가
- [ ] Chart.js로 Token Cost 트렌드 그래프 구현
- [ ] Clarity Score 막대 그래프 구현
- [ ] Task Timeline 카드 구현 (completed/in-progress/pending)

### Phase 3: 자동화 (Task 5 후)
- [ ] `.github/workflows/harness-analysis-report.yml` 생성
- [ ] `docs/update-harness-dashboard.py` 생성
- [ ] 자동 메트릭 수집 + HTML 업데이트
- [ ] 매 push 시 대시보드 자동 갱신

### Phase 4: 실시간 모니터링 (선택)
- [ ] Task 진행 중 실시간 로그 스트리밍 (WebSocket)
- [ ] 진행률 바 실시간 업데이트
- [ ] Slack 알림 (Task 완료 시)

---

## 6. 최종 결과물

### Git I/O 대시보드에서 볼 수 있는 것

```
📊 Harness Engineering Dashboard
├─ Progress Bar: 5/6 Tasks (83%)
├─ 📈 Token Cost Trend Chart
│  └─ Baseline → A → B → C → Master 비교
├─ ✨ Clarity Score Trend
│  └─ 각 Variant별 점수 개선
├─ ⏱️ Task Duration Overview
│  └─ 각 Task 소요 시간
├─ 📋 Task Timeline
│  ├─ Task 1: ✓ Complete (28 min)
│  ├─ Task 2: ✓ Complete (42 min)
│  ├─ Task 3: ✓ Complete (58 min)
│  ├─ Task 4: ✓ Complete (59 min)
│  ├─ Task 5: ⏳ In Progress
│  └─ Task 6: ⏳ Pending
├─ 📄 Latest Reports (드래그 가능)
│  └─ 각 Task 완료 보고서 인라인 표시
└─ 📝 Live Log Viewer
   └─ 현재 진행 중인 Task의 실시간 로그
```

---

## 7. 수동 로그 명령어 (Task 진행 중)

```bash
# Task 1 진행 중 로그 시작
task_id=1
log_file=".claude-harness-analysis/logs/task-${task_id}-baseline.log"
mkdir -p $(dirname "$log_file")

# 실행 및 로그 기록
{
  echo "=== Task ${task_id}: Baseline Analysis ===" 
  echo "Start: $(date)"
  echo ""
  
  # 실제 Task 명령어 실행
  # ...
  
  echo ""
  echo "End: $(date)"
} | tee "$log_file"

# 메트릭 JSON 생성
python3 .claude-harness-analysis/extract-metrics.py \
  --log "$log_file" \
  --output ".claude-harness-analysis/metrics/task-${task_id}-metrics.json"
```

---

## 결론

**Git I/O에서 실시간으로 보는 것**:
1. ✅ Task별 진행률 (Progress Bar)
2. ✅ 토큰 비용 트렌드 (Chart.js)
3. ✅ 명확성 점수 개선 (Chart.js)
4. ✅ 소요 시간 비교 (Timeline)
5. ✅ 각 Task별 완료 보고서 (Markdown 임베드)
6. ✅ 실시간 로그 (현재 진행 Task)

**자동화**:
- Task 완료 → 로그 생성 (자동)
- 로그 → 메트릭 JSON 추출 (자동)
- 메트릭 → 대시보드 업데이트 (자동)
- Push → GitHub Pages 배포 (자동)
