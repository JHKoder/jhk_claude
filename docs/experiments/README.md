# 🧪 Claude Code 실험 분석 대시보드

자동 생성되는 Claude Code 세션 성능 분석 리포트입니다.

각 세션의 **토큰 사용량**, **품질 지표**, **비용**을 자동으로 추적하고 시간별 추세를 분석합니다.

## 📊 인터랙티브 대시보드

👉 **[대시보드 열기](./dashboard.html)** - Chart.js 기반 인터랙티브 그래프

- 📈 실시간 차트 (Token 비율, 품질 분포, 캐시 효율)
- 🏃 러너별 성능 비교
- 📊 30일 추세 분석
- 🤖 모델 성능 비교
- 📋 상세 통계 테이블 (탭 기반)

---

## 📊 분석 카테고리

### 1️⃣ 일일 세션 리포트 (`daily`)
```
세션 ID | 러너 | Input Token | Output Token | 테스트 통과율 | Turn 수 | 컴파일 | 실행시간
```
- 그날의 모든 Claude Code 세션 기록
- 각 세션별 토큰 사용량 및 품질 점수

### 2️⃣ 토큰 효율 분석 (`efficiency`)
- **총 토큰 사용량**: Input vs Output 비율
- **캐시 히트율**: Prompt 캐시 효율성
- **비용 분석**: 세션별 실제 비용
- **품질/토큰**: 토큰 대비 품질 점수

### 3️⃣ 품질 지표 (`quality`)
- **통과율 통계**: 평균 / 중앙값
- **컴파일 성공율**: 빌드 성공 여부
- **러너별 성능**: 팀별 효율성 비교
- **코드 변경량**: 파일/라인 수정 통계

### 4️⃣ 30일 추세 분석 (`trends`)
- 일별 세션 수 추이
- 일일 평균 품질 추세
- 토큰 사용 추이
- 비용 추이

### 5️⃣ 모델 성능 비교 (`models`)
- 모델별 실행 횟수
- 모델별 평균 품질
- 모델별 실행 시간
- 모델별 비용

---

## 🔍 리포트 형식

### Markdown 파일
- **가독성**: 테이블과 텍스트로 정리된 형식
- **용도**: 리뷰, 문서화, 추세 시각화

### JSON 파일 (`analysis.json`)
- **구조**: 프로그래매틱 분석에 최적화
- **용도**: 대시보드 연동, 자동화 처리

---

## 📅 업데이트 스케줄

| 방식 | 스케줄 | 시간 |
|------|--------|------|
| **자동** | 매일 | UTC 00:00 (서울 시간 09:00) |
| **수동** | 언제든 | `bash .experiment/export_report.sh` |

---

## 🚀 로컬에서 실행

### 최신 리포트 생성
```bash
bash .experiment/export_report.sh
```

### 특정 디렉토리에 생성
```bash
bash .experiment/export_report.sh /path/to/output
```

### 분석 데이터만 출력
```bash
python3 -c "
import sys
sys.path.insert(0, '.experiment')
from export.analyzer import ExperimentAnalyzer
analyzer = ExperimentAnalyzer('.experiment/experiment.db')
import json
print(json.dumps(analyzer.generate_summary_report(), indent=2, ensure_ascii=False, default=str))
"
```

---

## 📂 파일 구조

```
docs/experiments/
├── README.md                           # 이 문서
├── index.md                            # 리포트 인덱스
├── {YYYY-MM-DD}-full-report.md         # 통합 리포트
├── {YYYY-MM-DD}-daily.md               # 일일 세션
├── {YYYY-MM-DD}-efficiency.md          # 효율성 분석
├── {YYYY-MM-DD}-quality.md             # 품질 지표
├── {YYYY-MM-DD}-trends.md              # 추세 분석
├── {YYYY-MM-DD}-models.md              # 모델 성능
└── {YYYY-MM-DD}-analysis.json          # 구조화된 데이터
```

---

## 🛠️ 기술 스택

| 구성 | 도구 |
|------|------|
| **데이터 저장** | SQLite (`.experiment/experiment.db`) |
| **분석** | Python 3.11+ |
| **자동화** | GitHub Actions |
| **문서** | Markdown + JSON |

---

## 📖 사용 예시

### 최근 30일 비용 추이 확인
```bash
cat docs/experiments/YYYY-MM-DD-trends.md | grep -A 20 "일일 데이터"
```

### 모델별 효율 비교
```bash
cat docs/experiments/YYYY-MM-DD-models.md
```

### JSON 데이터로 커스텀 분석
```bash
python3 << 'EOF'
import json
from pathlib import Path

data = json.loads(Path("docs/experiments/YYYY-MM-DD-analysis.json").read_text())
efficiency = data['token_efficiency']

print(f"평균 품질: {efficiency['avg_quality']:.2f}%")
print(f"캐시 히트율: {efficiency['cache_hit_rate']:.2f}%")
print(f"토큰당 품질: {efficiency['quality_per_token']:.2f}")
EOF
```

---

## 🔗 관련 링크

- [실험 시스템 설명서](.experiment/README.md)
- [대시보드](http://localhost:7788) - `exp serve`로 실행
- [GitHub Actions 워크플로우](.github/workflows/experiment-report.yml)

---

## ❓ FAQ

### Q: 왜 데이터가 없나요?
**A**: 아직 Claude Code 세션이 없거나 기준을 만족하지 못했을 수 있습니다.
- 최소 조건: Turn 수 ≥ 5, Output 토큰 ≥ 500, 파일 변경 1개 이상

### Q: 자동 리포트가 생성되지 않아요.
**A**: GitHub Actions 권한 확인:
```bash
git push # 로컬에서 강제 push
gh workflow view experiment-report  # 워크플로우 상태 확인
```

### Q: JSON 데이터를 활용하고 싶어요.
**A**: Python에서 쉽게 로드할 수 있습니다:
```python
import json
from pathlib import Path

data = json.loads(Path("docs/experiments/latest-analysis.json").read_text())
# data 구조: {token_efficiency, quality_metrics, trends, model_performance}
```

---

*자동 생성 중심의 연구일지 시스템입니다. 매일 세션 데이터가 누적되며, 추세 분석으로 성능 개선을 추적합니다.*
