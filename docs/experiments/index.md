# 📋 실험 리포트 인덱스

최근 생성된 리포트를 확인하세요.

## 🔄 최신 리포트 (2026-10-07)

| 분석 유형 | 파일 | 설명 |
|---------|------|------|
| 📊 **통합 리포트** | [2026-10-07-full-report.md](./2026-10-07-full-report.md) | 모든 분석을 한 페이지에 |
| 📅 **일일 세션** | [2026-10-07-daily.md](./2026-10-07-daily.md) | 그날의 모든 세션 기록 |
| ⚡ **효율성** | [2026-10-07-efficiency.md](./2026-10-07-efficiency.md) | 토큰 사용량 & 캐시 분석 |
| ✅ **품질 지표** | [2026-10-07-quality.md](./2026-10-07-quality.md) | 테스트 통과율 & 컴파일 성공율 |
| 📈 **추세 분석** | [2026-10-07-trends.md](./2026-10-07-trends.md) | 30일 일별 추이 |
| 🤖 **모델 성능** | [2026-10-07-models.md](./2026-10-07-models.md) | 모델별 효율성 비교 |
| 📦 **구조화 데이터** | [2026-10-07-analysis.json](./2026-10-07-analysis.json) | 프로그래매틱 분석용 |

---

## 🚀 빠른 시작

### 1️⃣ 즉시 리포트 생성
```bash
bash .experiment/export_report.sh
```

### 2️⃣ 생성된 파일 확인
```bash
ls docs/experiments/$(date +%Y-%m-%d)-*.md
```

### 3️⃣ 최신 리포트 보기
```bash
cat docs/experiments/$(date +%Y-%m-%d)-full-report.md
```

---

## 📊 분석 구조

### 토큰 효율 (Efficiency)
```
총 토큰 | Input/Output 비율 | 캐시 히트율 | 비용 | 토큰당 품질
```

### 품질 지표 (Quality)
```
테스트 통과율 | 컴파일 성공율 | 러너별 성능 | 코드 변경량
```

### 추세 분석 (Trends)
```
일별 세션 수 | 일별 평균 품질 | 토큰 추이 | 비용 추이
```

### 모델 성능 (Models)
```
모델명 | 실행 횟수 | 평균 품질 | 평균 시간 | 비용
```

---

## ⚙️ 자동화 설정

### GitHub Actions (매일 자동)
- **스케줄**: 매일 UTC 00:00 (서울 시간 09:00)
- **파일**: `.github/workflows/experiment-report.yml`
- **수동 실행**: GitHub Actions 탭 → "Daily Experiment Report" → "Run workflow"

### 로컬 크론 (선택사항)
```bash
# 매일 09:00에 리포트 생성
0 9 * * * cd /path/to/jhk_claude && bash .experiment/export_report.sh
```

---

## 📖 상세 가이드

각 리포트의 의미:

### Daily (일일 세션)
- **용도**: 그날의 모든 작업 기록
- **확인 항목**: 세션당 토큰 사용, 품질 점수, 컴파일 성공 여부

### Efficiency (효율성)
- **용도**: 비용 최적화 분석
- **주요 지표**:
  - 캐시 히트율 높을수록 좋음 (재사용률)
  - 토큰당 품질 높을수록 효율적

### Quality (품질)
- **용도**: 코드 품질 추적
- **주요 지표**:
  - 테스트 통과율 (평균 vs 중앙값)
  - 러너별 성능 비교

### Trends (추세)
- **용도**: 성능 개선 추적
- **분석**: 30일 일별 데이터
- **활용**: 주간/월간 성능 변화 감지

### Models (모델 성능)
- **용도**: 모델 효율성 비교
- **분석**: Claude 모델별 성능, 비용, 속도 비교

---

## 🔍 활용 예시

### Case 1: 비용 최적화
```bash
# 최근 토큰 효율 확인
cat docs/experiments/$(date +%Y-%m-%d)-efficiency.md | grep "캐시\|비용\|품질"
```

### Case 2: 품질 추세 분석
```bash
# 지난 달 품질 추이
tail -31 docs/experiments/$(date +%Y-%m-%d)-trends.md
```

### Case 3: 모델 성능 비교
```bash
# 모델별 효율성 (비용/품질)
python3 << 'EOF'
import json
from pathlib import Path

latest = list(Path("docs/experiments").glob("*-analysis.json"))[-1]
data = json.loads(latest.read_text())

for model in data['model_performance']['models']:
    efficiency = model['avg_quality'] / (model['total_cost'] + 0.0001)
    print(f"{model['name']:15} | 품질: {model['avg_quality']:5.2f}% | 비용: ${model['total_cost']:.4f} | 효율: {efficiency:.1f}")
EOF
```

---

## 📝 데이터 보관

| 기간 | 보관 정책 |
|------|---------|
| **30일 이내** | 모든 일일 리포트 보관 |
| **30일 이상** | 아카이브 (월단위) |
| **JSON 데이터** | 분석용 원본 데이터 |

---

## ❓ 자주 묻는 질문

**Q: 리포트가 비어있어요.**  
A: 기준을 만족하는 세션이 없을 수 있습니다:
- Turn 수 ≥ 5
- Output 토큰 ≥ 500
- 파일 변경 1개 이상

**Q: 커스텀 분석을 하고 싶어요.**  
A: JSON 파일을 사용하세요:
```python
import json
data = json.loads(Path("docs/experiments/YYYY-MM-DD-analysis.json").read_text())
# data['token_efficiency'], data['quality_metrics'] 등
```

**Q: 리포트를 슬랙에 공유하고 싶어요.**  
A: GitHub Actions에 추가할 수 있습니다:
```yaml
- name: Send to Slack
  uses: slackapi/slack-github-action@v1
  with:
    payload: |
      {
        "text": "Daily Experiment Report: ..."
      }
```

---

## 🔗 연관 문서

- [실험 시스템 README](./README.md)
- [.experiment/README.md](./.experiment/README.md)
- [GitHub Actions 워크플로우](./.github/workflows/experiment-report.yml)

---

**마지막 업데이트**: 2026-10-07 15:15  
**다음 자동 생성**: 2026-10-08 09:00 (KST)
