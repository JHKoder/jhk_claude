# Task 5: 대시보드 UI 업데이트

**Files:**
- Create: `.experiment/templates/quality_comparison.html`
- Modify: `.experiment/server.py` - 라우트 추가
- Modify: `.experiment/templates/dashboard.html` - 탭 추가

**Interfaces:**
- Consumes: `quality_metrics` 테이블 데이터, tasks.json 설정
- Produces: `/quality-comparison` 엔드포인트, 시각화 UI

## Step 1: 품질 비교 HTML 템플릿 작성

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

## Step 2: server.py에 API 엔드포인트 추가

`.experiment/server.py`에 다음 함수 추가:

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
        LEFT JOIN runs s ON qm.session_id = s.session_id
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

## Step 3: 대시보드 탭에 Quality Comparison 추가

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

## Step 4: Commit

```bash
git add .experiment/templates/quality_comparison.html .experiment/server.py .experiment/templates/dashboard.html
git commit -m "feat: add quality comparison dashboard with metrics visualization"
```
