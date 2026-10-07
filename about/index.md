---
layout: default
title: "프로젝트 소개"
permalink: /about/
---

# 🧪 Claude Code 실험 연구소

## 프로젝트 개요

이 연구 블로그는 Claude Code 사용 시 **토큰 효율성**, **품질 지표**, **비용 최적화**를 추적하고 분석하는 프로젝트입니다.

### 핵심 목표

- ✅ **자동화된 성능 분석**: 매 세션마다 자동으로 데이터 수집
- ✅ **시각화된 인사이트**: 일별/월별 추세 분석
- ✅ **효율성 최적화**: 토큰 사용량과 품질의 관계 파악
- ✅ **모델 비교**: 다양한 Claude 모델의 성능 비교

---

## 📊 분석 항목

### 1. 토큰 효율성 (Token Efficiency)
- Input/Output 토큰 비율
- Prompt 캐시 히트율
- 세션별 비용 분석
- 토큰당 품질 점수

### 2. 품질 지표 (Quality Metrics)
- 테스트 통과율 (Pass Rate)
- 컴파일 성공율
- 코드 변경량 (LOC)
- 러너별 성능 비교

### 3. 추세 분석 (Trends)
- 일별 세션 수
- 평균 품질 추이
- 토큰 사용량 추이
- 비용 추이 (30일, 월별)

### 4. 모델 성능 (Model Performance)
- 모델별 실행 횟수
- 모델별 평균 품질
- 모델별 평균 실행 시간
- 모델별 총 비용

---

## 🏗️ 기술 스택

| 계층 | 기술 |
|------|------|
| **데이터 수집** | Claude Code Stop Hook |
| **저장소** | SQLite (`.experiment/experiment.db`) |
| **분석 엔진** | Python 3.11+ |
| **리포트 생성** | Markdown + JSON |
| **자동화** | GitHub Actions |
| **웹사이트** | Jekyll + Minima Theme |
| **배포** | GitHub Pages |

---

## 📈 시스템 아키텍처

```
Claude Code Session
        ↓
    Stop Hook (데이터 수집)
        ↓
    SQLite Database
        ↓
    Python Analysis Engine
        ├→ Token Efficiency
        ├→ Quality Metrics
        ├→ Trends
        └→ Model Performance
        ↓
    Report Generator
        ├→ Markdown Reports
        ├→ JSON Data
        └→ Git Commit
        ↓
    GitHub Pages (블로그)
```

---

## 🚀 주요 기능

### 자동 수집
- **조건**: Turn ≥ 5, Output Token ≥ 500, 파일 변경 ≥ 1
- **저장**: SQLite 데이터베이스
- **주기**: 매 세션 종료 시

### 자동 분석
- **스케줄**: 매일 자정 UTC (한국 시간 09:00)
- **분석**: 최근 100개 세션
- **출력**: 5가지 분석 리포트 + JSON

### 자동 배포
- **저장소**: GitHub 자동 커밋
- **웹사이트**: GitHub Pages 자동 업데이트
- **URL**: `https://github.com/JHKoder/jhk_claude`

---

## 📂 파일 구조

```
jhk_claude/
├── _config.yml                    # Jekyll 설정
├── _layouts/
│   ├── default.html              # 기본 레이아웃 (사이드바 포함)
│   └── research.html             # 연구 게시물 레이아웃
├── index.md                       # 홈페이지
├── about/
│   └── index.md                  # 소개 페이지
├── research/
│   └── index.md                  # 연구 목록
├── _research/                    # 연구 게시물 (자동 생성)
│   └── 2026-10-07-token-efficiency.md
├── docs/experiments/
│   ├── README.md                 # 실험 시스템 가이드
│   ├── 2026-10-07-full-report.md
│   └── 2026-10-07-*.md          # 분석 리포트
├── .experiment/
│   ├── experiment.db             # SQLite 데이터베이스
│   ├── export/
│   │   ├── analyzer.py           # 분석 엔진
│   │   └── reports.py            # 리포트 생성
│   └── export_report.sh          # 수동 실행 스크립트
└── .github/workflows/
    └── experiment-report.yml     # 자동화 워크플로우
```

---

## 💡 사용 방식

### 1️⃣ 자동 모드 (권장)
```
매일 자정 → GitHub Actions 실행
         → 분석 및 리포트 생성
         → Git 자동 커밋
         → 블로그 자동 업데이트
```

### 2️⃣ 수동 모드
```bash
bash .experiment/export_report.sh
# 즉시 리포트 생성 및 Git 커밋
```

### 3️⃣ Python API
```python
import sys
sys.path.insert(0, '.experiment')
from export.analyzer import ExperimentAnalyzer

analyzer = ExperimentAnalyzer('.experiment/experiment.db')
analysis = analyzer.generate_summary_report()
```

---

## 📊 분석 예시

### 토큰 효율성 분석
```
총 실행: 7회
총 Input Token: 39,268
총 Output Token: 284,144
캐시 히트율: 96.48%
총 비용: $20.2219
평균 품질: 0.00%
```

### 추세 분석 (30일)
```
2026-09-23: 7 runs, $20.2219 비용
평균 품질: 0.00%
```

---

## 🔍 특징

### 1. 이미지 캡처 불필요
- ✅ 데이터 기반 분석
- ✅ 자동화된 테이블 생성
- ✅ JSON 형식의 구조화된 데이터

### 2. Git Pages 통합
- ✅ 사이드바 네비게이션
- ✅ 검색 기능
- ✅ 정렬 기능 (최신순/제목순)
- ✅ 태그 필터링
- ✅ 카테고리 분류

### 3. 완전 자동화
- ✅ 데이터 수집
- ✅ 분석 실행
- ✅ 리포트 생성
- ✅ Git 커밋
- ✅ 블로그 업데이트

---

## 🎯 개선 로드맵

- [ ] Slack 알림 통합
- [ ] 비용 예측 모델
- [ ] 토큰 최적화 추천
- [ ] 모델 자동 선택 시스템
- [ ] API 서버 (데이터 조회)
- [ ] 대시보드 시각화 개선

---

## 📞 연락처

- **GitHub**: [JHKoder](https://github.com/JHKoder)
- **Email**: jeonghun.kang.dev@gmail.com

---

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

---

**마지막 업데이트**: 2026-10-07  
**시스템 상태**: ✅ 활성화
