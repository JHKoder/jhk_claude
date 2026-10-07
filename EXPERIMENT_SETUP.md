# 🧪 실험 분석 시스템 완벽 가이드

## 📋 목차

1. [개요](#개요)
2. [구성 요소](#구성-요소)
3. [사용법](#사용법)
4. [AI 이미지 캡처 우회 방식](#ai-이미지-캡처-우회-방식)
5. [Git Pages + Wiki 연동](#git-pages--wiki-연동)
6. [자동화 설정](#자동화-설정)

---

## 개요

Claude Code 세션의 **토큰 사용량**, **품질 지표**, **비용**, **성능 추이**를 자동으로 추적하고 분석합니다.

**핵심 특징**:
- ✅ AI가 이미지를 캡처할 필요 없음 (데이터 기반 분석)
- ✅ 자동 Markdown 리포트 생성
- ✅ 매일 자정 자동 실행 (GitHub Actions)
- ✅ JSON 형식으로 프로그래매틱 분석 가능
- ✅ Git 히스토리에 자동 커밋

---

## 구성 요소

### 1. 분석 엔진 (`.experiment/export/`)

#### `analyzer.py`
SQLite 데이터베이스에서 다양한 메트릭을 추출하고 분석합니다.

```python
class ExperimentAnalyzer:
    - analyze_token_efficiency()      # 토큰 효율
    - analyze_quality_metrics()       # 품질 지표
    - analyze_trends()                # 추세 분석
    - analyze_model_performance()     # 모델 성능
    - generate_summary_report()       # 전체 요약
```

**분석 항목**:
- Input/Output 토큰 비율
- 캐시 히트율
- 테스트 통과율
- 컴파일 성공율
- 실행 시간
- 코드 변경량
- 러너별 성능
- 모델별 효율

#### `reports.py`
분석 결과를 Markdown 및 JSON으로 변환합니다.

```python
class MarkdownReportGenerator:
    - generate_daily_report()         # 일일 세션
    - generate_efficiency_report()    # 효율성
    - generate_quality_report()       # 품질
    - generate_trend_report()         # 추세
    - generate_model_report()         # 모델 성능
    - generate_full_report()          # 통합 리포트
```

**출력**:
- `YYYY-MM-DD-daily.md` - 일일 세션 기록
- `YYYY-MM-DD-efficiency.md` - 토큰/캐시/비용 분석
- `YYYY-MM-DD-quality.md` - 테스트/컴파일 지표
- `YYYY-MM-DD-trends.md` - 30일 추이
- `YYYY-MM-DD-models.md` - 모델 성능 비교
- `YYYY-MM-DD-full-report.md` - 통합
- `YYYY-MM-DD-analysis.json` - 구조화된 데이터

### 2. 자동화 스크립트

#### `export_report.sh`
로컬에서 즉시 리포트를 생성합니다.

```bash
bash .experiment/export_report.sh          # docs/experiments에 생성
bash .experiment/export_report.sh /path    # 특정 디렉토리에 생성
```

### 3. GitHub Actions

#### `.github/workflows/experiment-report.yml`
매일 자정에 자동으로 리포트를 생성하고 커밋합니다.

- **스케줄**: 매일 UTC 00:00 (서울 시간 09:00)
- **동작**:
  1. `.experiment/experiment.db` 에서 데이터 읽음
  2. 분석 실행
  3. Markdown & JSON 생성
  4. Git에 커밋 및 푸시

---

## 사용법

### 방법 1: 자동 (GitHub Actions)
```
매일 자정 → 자동 리포트 생성 → Git 커밋
```

아무 설정 없이 작동합니다. 단, 리포지토리에 push 권한이 필요합니다.

### 방법 2: 수동 (로컬 실행)
```bash
bash .experiment/export_report.sh
```

출력 예시:
```
📊 실험 분석 리포트 생성 중...
  Project Root: /Users/kang/gitdir/jhk_claude
  Output: docs/experiments

✅ 리포트 생성 완료!

생성된 파일:
  - 2026-10-07-daily.md
  - 2026-10-07-efficiency.md
  - 2026-10-07-quality.md
  - 2026-10-07-trends.md
  - 2026-10-07-models.md
  - analysis.json
  - full-report.md (통합)
```

### 방법 3: Python에서 직접 사용
```python
import sys
sys.path.insert(0, '.experiment')
from export.analyzer import ExperimentAnalyzer

analyzer = ExperimentAnalyzer('.experiment/experiment.db')
analysis = analyzer.generate_summary_report()

# 데이터 확인
print(f"총 실행: {analysis['token_efficiency']['total_runs']}")
print(f"평균 품질: {analysis['quality_metrics']['avg_pass_rate']:.2f}%")
print(f"총 비용: ${analysis['token_efficiency']['total_cost_usd']:.4f}")
```

---

## AI 이미지 캡처 우회 방식

**문제**: Claude가 스크린샷 이미지를 분석할 수 없음  
**해결**: 데이터 기반 분석으로 이미지 대체

### 1. 직접 데이터 추출 (추천)

```python
# Prometheus/Grafana → Python → Markdown
import requests

metrics = requests.get('http://prometheus:9090/api/v1/query',
    params={'query': 'cpu_usage_percent'}).json()

# 마크다운 테이블로 변환
md = "| Timestamp | CPU Usage |\n"
for m in metrics['data']['result']:
    md += f"| {m['timestamp']} | {m['value']}% |\n"
```

### 2. 이미지 → 텍스트 변환 (OCR)

```bash
# 로컬 OCR 도구 (AI 없음)
brew install tesseract
tesseract screenshot.png output.txt
```

### 3. 구조화된 메타데이터 기록

```markdown
## 모니터링 결과 [2026-10-07 14:30]

![CPU 사용률](./images/cpu.png)

<!-- 메타데이터: 마크다운으로 기록 -->
- CPU 사용률: 85% (14:30)
- 메모리: 78%
- 디스크 IO: 450MB/s
- 이벤트: 배치 작업 시작
```

### 4. 자동화된 데이터 수집

```python
# 매시간 자동으로 메트릭 수집
import schedule
import requests

def collect_metrics():
    data = {
        'timestamp': datetime.now().isoformat(),
        'cpu': get_cpu(),
        'memory': get_memory(),
        'disk_io': get_disk_io(),
    }
    save_to_markdown(data)

schedule.every().hour.do(collect_metrics)
```

---

## Git Pages + Wiki 연동

### 구조

```
jhk_claude/
├── docs/                          # Git Pages 소스
│   └── experiments/
│       ├── README.md              # 대시보드 설명
│       ├── index.md               # 리포트 인덱스
│       └── YYYY-MM-DD-*.md       # 일일 리포트
│
├── wiki/                          # GitHub Wiki (자동 동기화)
│   ├── Home.md
│   ├── Experiment-Guide.md
│   └── Quality-Metrics.md
│
└── .github/workflows/
    ├── experiment-report.yml      # 매일 자정
    └── sync-wiki.yml              # Wiki 동기화
```

### Git Pages 활성화

1. **Settings** → **Pages**
2. **Source**: `main` / `docs` 선택
3. **URL**: `https://yourusername.github.io/jhk_claude`

### Wiki 동기화 (선택사항)

자동으로 `docs/experiments` 내용을 Wiki에 동기화하려면:

```yaml
# .github/workflows/sync-wiki.yml
name: Sync Experiment Reports to Wiki

on:
  push:
    paths:
      - 'docs/experiments/**'

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Sync to Wiki
        run: |
          mkdir -p /tmp/wiki
          cp docs/experiments/*.md /tmp/wiki/
          
          # Wiki 저장소 클론
          git clone https://github.com/${{ github.repository }}.wiki.git /tmp/wiki-repo
          cp /tmp/wiki/*.md /tmp/wiki-repo/
          
          cd /tmp/wiki-repo
          git config user.name "Wiki Sync Bot"
          git add .
          git commit -m "sync: experiment reports" || true
          git push
```

---

## 자동화 설정

### GitHub Actions (기본)

이미 설정됨. 확인 방법:

```bash
# 워크플로우 상태 확인
gh workflow list

# 최근 실행 확인
gh workflow view experiment-report

# 수동 실행
gh workflow run experiment-report.yml
```

### 로컬 크론 (선택사항)

```bash
# macOS/Linux
crontab -e

# 매일 09:00에 리포트 생성
0 9 * * * cd /Users/kang/gitdir/jhk_claude && bash .experiment/export_report.sh

# 저장 후 확인
crontab -l
```

### Slack 알림 (고급)

```yaml
# .github/workflows/experiment-report.yml에 추가
- name: Send Slack Notification
  if: always()
  uses: slackapi/slack-github-action@v1
  with:
    webhook-url: ${{ secrets.SLACK_WEBHOOK }}
    payload: |
      {
        "text": "📊 Daily Experiment Report Generated",
        "blocks": [
          {
            "type": "section",
            "text": {
              "type": "mrkdwn",
              "text": "*Experiment Report*\n📅 $(date +%Y-%m-%d)\n✅ Reports generated and committed"
            }
          }
        ]
      }
```

---

## 📊 데이터베이스 스키마

SQLite 테이블 구조:

```sql
-- 세션 기록
CREATE TABLE runs (
    id              INTEGER PRIMARY KEY,
    recorded_at     TEXT,
    session_id      TEXT,
    runner          TEXT,
    input_tokens    INTEGER,
    output_tokens   INTEGER,
    cache_read      INTEGER,
    cache_write     INTEGER,
    test_pass_rate  REAL,
    compile_ok      INTEGER,
    wall_clock_sec  INTEGER,
    billing_usd     REAL,
    turn_count      INTEGER,
    changed_files_cnt INTEGER,
    added_lines     INTEGER,
    deleted_lines   INTEGER
);

-- 분석 결과
CREATE TABLE analyses (
    id           INTEGER PRIMARY KEY,
    recorded_at  TEXT,
    config_hash  TEXT,
    analysis_json TEXT
);
```

---

## 🔍 활용 사례

### Case 1: 월별 비용 분석
```bash
# 최근 30일 비용 추이
python3 << 'EOF'
import json
from pathlib import Path

latest_json = list(Path("docs/experiments").glob("*-analysis.json"))[-1]
data = json.loads(latest_json.read_text())

daily = data['trends']['daily_data']
print("날짜\t\t비용")
for d in daily:
    print(f"{d['date']}\t${d['daily_cost']:.4f}")
EOF
```

### Case 2: 모델 성능 순위
```bash
python3 << 'EOF'
import json
from pathlib import Path

data = json.loads(list(Path("docs/experiments").glob("*-analysis.json"))[-1].read_text())
models = sorted(data['model_performance']['models'], 
                key=lambda x: x['avg_quality'], reverse=True)

for m in models:
    print(f"{m['name']:15} | 품질: {m['avg_quality']:5.2f}% | 비용: ${m['total_cost']:.4f}")
EOF
```

### Case 3: 캐시 효율성 추세
```bash
python3 << 'EOF'
import json
from pathlib import Path

# 최근 5일 캐시 히트율
reports = sorted(Path("docs/experiments").glob("*-efficiency.md"))[-5:]

for report in reports:
    date = report.name.split('-')[0:3]
    content = report.read_text()
    for line in content.split('\n'):
        if '캐시 히트율' in line:
            print(f"{'-'.join(date)}: {line.split(':')[1].strip()}")
EOF
```

---

## 🚀 다음 단계

1. **로컬에서 테스트**: `bash .experiment/export_report.sh`
2. **리포트 확인**: `cat docs/experiments/$(date +%Y-%m-%d)-full-report.md`
3. **Git Pages 활성화**: Settings → Pages
4. **자동화 확인**: GitHub Actions 탭에서 "Daily Experiment Report" 확인
5. **Wiki 연동** (선택): 위 설정 참고

---

## 📞 지원

| 항목 | 해결 방법 |
|------|---------|
| 리포트 생성 실패 | `python3 .experiment/export/reports.py` 직접 실행 |
| 데이터 없음 | `.experiment/experiment.db` 파일 확인 |
| 자동화 미작동 | GitHub Actions 탭에서 워크플로우 로그 확인 |
| 커스텀 분석 필요 | JSON 파일 활용 (Python/JS로 파싱 가능) |

---

**마지막 업데이트**: 2026-10-07  
**시스템 버전**: 1.0  
**담당**: JHKoder
