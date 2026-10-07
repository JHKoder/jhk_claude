# 📊 인터랙티브 대시보드 가이드

## 개요

분석 리포트를 **Chart.js 기반의 인터랙티브 HTML 대시보드**로 자동 생성합니다.

### 🌟 주요 기능

- ✅ **실시간 그래프**: Token 비율, 품질 분포, 캐시 효율
- ✅ **성능 비교**: 러너별, 모델별 성능 비교
- ✅ **추세 분석**: 30일 일별 데이터 시각화
- ✅ **상세 통계**: 탭 기반 메트릭 테이블
- ✅ **반응형 디자인**: 모바일/태블릿 지원

---

## 📈 포함된 차트

### 1️⃣ Token 비율 (Doughnut)
```
Input Token : Output Token 비율
- 원형 차트
- 퍼센트 표시
- 실시간 계산
```

### 2️⃣ 품질 점수 분포 (Bar)
```
0-20% | 20-40% | 40-60% | 60-80% | 80-100%
- 구간별 세션 수
- 품질 레벨 분류
```

### 3️⃣ 캐시 효율 (Doughnut)
```
캐시 히트 : 캐시 미스 비율
- 높을수록 좋음 (>90%)
- 실시간 백분율
```

### 4️⃣ 러너별 성능 (Bar)
```
Runner A | Runner B | Runner C...
- 러너별 평균 품질
- 비교 분석
```

### 5️⃣ 30일 추세 (Line, 이중 축)
```
왼쪽 Y축: 실행 수
오른쪽 Y축: 평균 품질 (%)
X축: 날짜 (30일)

- 멀티 라인 차트
- 상호작용 가능 (hover)
```

### 6️⃣ 모델 성능 (Bar)
```
Claude 3 Opus | Claude 3 Sonnet...
- 모델별 평균 품질
- 비용 효율성
```

---

## 🎨 대시보드 레이아웃

```
┌──────────────────────────────────────────┐
│ 🧪 Claude Code 실험 분석 대시보드         │
│ 생성일: 2026-10-07 15:00:00              │
└──────────────────────────────────────────┘

┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐
│ 7   │ │$20  │ │0.00%│ │96%  │  ← 핵심 지표 (카드)
│ Run │ │Cost │ │Qual│ │Cache│
└─────┘ └─────┘ └─────┘ └─────┘

┌──────────────────────────────────────┐
│ 📊 Token 비율      │  ✅ 품질 분포    │
│   (원형 차트)      │   (막대 차트)     │
├────────────────────┼──────────────────┤
│ ⚡ 캐시 효율       │  🏃 러너 성능    │
│   (원형 차트)      │   (막대 차트)     │
└────────────────────┴──────────────────┘

┌──────────────────────────────────────┐
│ 📈 30일 추세 분석 (멀티라인 차트)    │
│ 실행수 / 품질 / 토큰 / 비용          │
└──────────────────────────────────────┘

┌──────────────────────────────────────┐
│ 🤖 모델 성능 비교 (막대 차트)        │
│ Claude 3 Opus | Sonnet | Haiku       │
└──────────────────────────────────────┘

┌──────────────────────────────────────┐
│ 📊 상세 통계                         │
│ [효율성] [품질] [추세] [모델]        │
├──────────────────────────────────────┤
│ 총 Input Token: 39,268              │
│ 총 Output Token: 284,144            │
│ 평균 품질: 0.00%                     │
│ ...                                  │
│                                      │
│ [테이블: 모든 메트릭]                │
└──────────────────────────────────────┘

푸터: "이 대시보드는 자동으로 생성됩니다"
```

---

## 🚀 사용 방법

### 1️⃣ 로컬에서 보기

```bash
# 대시보드 생성
bash .experiment/export_report.sh

# 브라우저에서 열기
open docs/experiments/dashboard.html
```

### 2️⃣ GitHub Pages에서 보기

```
https://YOUR_USERNAME.github.io/jhk_claude/docs/experiments/dashboard.html
```

### 3️⃣ 자동 업데이트

매일 자정에 자동으로 생성됩니다:
```
GitHub Actions → Dashboard 생성 → Git 커밋 → 자동 배포
```

---

## 📊 대시보드 상호작용

### 마우스 호버
```
차트 위에 마우스를 올리면:
- 값 표시 (Tooltip)
- 배경 강조
- 실시간 데이터 표시
```

### 탭 전환
```
상세 통계 섹션에서 탭 클릭:
- 효율성: Input/Output, 캐시, 비용
- 품질: 통과율, 컴파일, 코드 변경
- 추세: 일별 데이터 테이블
- 모델: 모델별 성능 테이블
```

### 반응형
```
화면 크기에 따라 자동 조정:
- 데스크톱: 2×3 그리드
- 태블릿: 1×2 그리드
- 모바일: 1×1 (스택)
```

---

## 📈 차트별 상세

### Token 비율
```js
{
  type: 'doughnut',
  data: {
    labels: ['Input Token', 'Output Token'],
    datasets: [{
      data: [39268, 284144],
      backgroundColor: ['#667eea', '#764ba2']
    }]
  }
}
```

**특징**:
- 원형 차트로 비율 시각화
- 퍼센트 자동 계산
- 호버 시 값 표시

### 러너별 성능
```js
{
  type: 'bar',
  data: {
    labels: Object.keys(by_runner),
    datasets: [{
      label: '평균 품질 (%)',
      data: Object.values(avg_quality),
      backgroundColor: '#667eea'
    }]
  }
}
```

**특징**:
- 수평/수직 막대
- 러너별 비교
- 평균값 표시

### 30일 추세
```js
{
  type: 'line',
  data: {
    labels: [...dates],
    datasets: [
      {
        label: '실행 수',
        data: [...runs],
        yAxisID: 'y'
      },
      {
        label: '평균 품질 (%)',
        data: [...quality],
        yAxisID: 'y1'
      }
    ]
  }
}
```

**특징**:
- 멀티라인 차트
- 이중 Y축 (실행수/품질)
- 30일 추이 분석

---

## 🔧 커스터마이징

### 색상 변경

파일: `.experiment/export/dashboard_generator.py` (약 60-70줄)

```python
backgroundColor: ['#667eea', '#764ba2'],  # ← 색상 코드 변경
```

변경 예:
```python
backgroundColor: ['#FF6B6B', '#4ECDC4'],  # Red & Teal
```

### 폰트 변경

```python
# 상단 <style> 섹션에서
font-family: YOUR_FONT_HERE;
```

### 차트 타입 변경

```python
type: 'bar',  # ← 'line', 'doughnut', 'pie', 'radar' 등
```

### 범례 위치 변경

```python
plugins: {
    legend: {
        position: 'bottom',  # ← 'top', 'left', 'right'
    }
}
```

---

## 📋 데이터 소스

### SQLite 데이터
```
.experiment/experiment.db

run 테이블:
- input_tokens
- output_tokens
- test_pass_rate
- compile_ok
- wall_clock_sec
- billing_usd
- turn_count
- runner (러너 이름)
- model (모델 이름)
```

### 분석 엔진
```python
# .experiment/export/analyzer.py

- analyze_token_efficiency()      # 토큰 효율
- analyze_quality_metrics()       # 품질 지표
- analyze_trends()                # 추세 (30일)
- analyze_model_performance()    # 모델 비교
```

### 대시보드 생성기
```python
# .experiment/export/dashboard_generator.py

class DashboardGenerator:
    - generate_dashboard()    # HTML 생성
    - export_dashboard()      # 파일 저장
```

---

## 🚀 배포

### GitHub Pages

```
Settings → Pages → Branch: main / Folder: /root
↓
매일 자정에 dashboard.html 자동 생성 & 커밋
↓
GitHub Pages 자동 빌드
↓
https://YOUR_USERNAME.github.io/jhk_claude/docs/experiments/dashboard.html
```

### CI/CD 통합

```yaml
# .github/workflows/experiment-report.yml

- 분석 실행
- 대시보드 생성
- Git 커밋
- Pages 자동 배포
```

---

## ⚙️ 기술 스택

| 항목 | 기술 |
|------|------|
| 차트 라이브러리 | Chart.js 4.4.0 |
| 데이터 라벨 | chartjs-plugin-datalabels 2.2.0 |
| 스타일 | CSS3 (Grid, Flexbox) |
| 상호작용 | Vanilla JavaScript |
| 반응형 | Media Queries |

---

## 📊 지표 설명

### 핵심 지표 (4개 카드)

| 지표 | 설명 | 단위 |
|------|------|------|
| 총 실행 | Claude Code 세션 수 | 회 |
| 총 비용 | 모든 세션 합산 비용 | USD |
| 평균 품질 | 테스트 통과율 평균 | % |
| 캐시 히트율 | Prompt 캐시 효율 | % |

### 상세 메트릭

**효율성**:
- Input/Output Token 수
- Token 비율
- 토큰당 품질
- 평균 Turn 수

**품질**:
- 통과율 (평균/중앙값)
- 컴파일 성공율
- 파일 변경 수
- 코드 라인 추가/삭제

**추세**:
- 일별 세션 수
- 일별 평균 품질
- 일별 총 토큰
- 일별 비용

**모델**:
- 모델별 실행 횟수
- 모델별 평균 품질
- 모델별 평균 시간
- 모델별 총 비용

---

## 🔗 관련 링크

- [분석 시스템](./EXPERIMENT_SETUP.md)
- [블로그 설정](./BLOG_SETUP.md)
- [Markdown 리포트](./docs/experiments/)
- [Chart.js 공식 문서](https://www.chartjs.org/)

---

## ✅ 체크리스트

- [ ] 대시보드 생성 (`bash .experiment/export_report.sh`)
- [ ] 로컬에서 확인 (`open docs/experiments/dashboard.html`)
- [ ] GitHub Pages 활성화
- [ ] 자동화 워크플로우 확인
- [ ] 매일 업데이트 확인

---

**마지막 업데이트**: 2026-10-07  
**차트 라이브러리**: Chart.js 4.4.0  
**상태**: ✅ 프로덕션 준비 완료
