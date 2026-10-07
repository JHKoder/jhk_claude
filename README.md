# 🧪 Claude Code 실험 연구 블로그

Claude Code 세션의 **성능 분석**, **토큰 효율성**, **품질 지표**를 자동으로 추적하고 **Git Pages 블로그**로 공개하는 통합 시스템입니다.

## 🌟 주요 기능

### 1️⃣ 자동 데이터 수집
- ✅ 매 Claude Code 세션마다 자동 기록
- ✅ SQLite 데이터베이스 저장
- ✅ 토큰, 비용, 품질, 시간 추적

### 2️⃣ 자동 분석 & 리포팅
- ✅ 매일 자정 자동 분석
- ✅ Markdown 리포트 생성 (5가지)
- ✅ JSON 데이터 출력
- ✅ Git 자동 커밋

### 3️⃣ 블로그 자동 생성
- ✅ 분석 → Jekyll 게시물 자동 변환
- ✅ 사이드바 (카테고리, 최신 연구, 태그)
- ✅ 검색 & 정렬 (최신순/제목순)
- ✅ 카테고리 필터링

### 4️⃣ GitHub Pages 배포
- ✅ 자동 빌드 & 배포
- ✅ 공개 블로그 URL
- ✅ 모바일 반응형

---

## 📊 시스템 흐름

```
Claude Code Session
        ↓
   Stop Hook (데이터 수집)
        ↓
   SQLite Database
        ↓ (매일 자정)
GitHub Actions (자동화)
        ├→ Python 분석 엔진
        │  ├→ Token Efficiency (토큰 효율)
        │  ├→ Quality Metrics (품질)
        │  ├→ Trends (추세)
        │  └→ Model Performance (모델 비교)
        │
        ├→ Markdown Reports (docs/experiments/)
        │
        ├→ Blog Generator (블로그 생성)
        │  └→ Jekyll Posts (_research/)
        │
        └→ Git Commit & Push
           └→ GitHub Pages 자동 배포
              └→ https://YOUR_USERNAME.github.io/jhk_claude
```

---

## 🚀 빠른 시작 (5분)

### Step 1: Git Pages 활성화

1. GitHub 저장소 Settings 이동
2. **Pages** 탭 선택
3. Source: `main` / Folder: `/root`
4. **Save**

✅ 1-2분 후 블로그 라이브됨

### Step 2: 분석 확인

```bash
# 로컬에서 즉시 분석 생성
bash .experiment/export_report.sh

# 생성된 리포트 확인
cat docs/experiments/$(date +%Y-%m-%d)-full-report.md
```

### Step 3: 블로그 방문

```
https://YOUR_USERNAME.github.io/jhk_claude
```

---

## 📚 문서

| 문서 | 내용 |
|------|------|
| [EXPERIMENT_SETUP.md](./EXPERIMENT_SETUP.md) | 분석 시스템 완벽 가이드 |
| [BLOG_SETUP.md](./BLOG_SETUP.md) | Git Pages 블로그 설정 |
| [docs/experiments/README.md](./docs/experiments/README.md) | 실험 시스템 설명 |
| [.experiment/README.md](./.experiment/README.md) | 수집 & 분석 상세 |

---

## 🎯 사용 방식

### 자동 모드 (권장)

```
매일 자정 UTC (한국 시간 09:00)
    ↓
GitHub Actions 자동 실행
    ├→ 분석 (최근 100개 세션)
    ├→ 리포트 생성
    ├→ 블로그 게시물 생성
    └→ Git 커밋 & 푸시
```

**설정**: 이미 완료됨 (`.github/workflows/experiment-report.yml`)

### 수동 모드

```bash
# 지금 바로 분석 & 블로그 생성
bash .experiment/export_report.sh

# 결과 확인
ls docs/experiments/$(date +%Y-%m-%d)-*.md
ls _research/$(date +%Y-%m-%d)-*.md

# Git 커밋 (선택)
git add docs/experiments/ _research/
git commit -m "docs(research): add analysis $(date +%Y-%m-%d)"
git push
```

---

## 📂 디렉토리 구조

```
jhk_claude/
├── _config.yml                  # Jekyll 설정
├── _layouts/
│   ├── default.html            # 기본 레이아웃 (사이드바 포함)
│   └── research.html           # 연구 게시물 레이아웃
├── _research/                  # 연구 게시물 (자동 생성)
│   ├── 2026-10-07-daily-analysis.md
│   ├── 2026-10-07-efficiency-analysis.md
│   └── ...
├── index.md                     # 홈페이지
├── research/index.md           # 연구 목록
├── about/index.md              # 프로젝트 소개
├── docs/
│   └── experiments/            # 분석 리포트
│       ├── README.md
│       ├── 2026-10-07-full-report.md
│       ├── 2026-10-07-daily.md
│       └── ...
└── .experiment/
    ├── experiment.db            # SQLite 데이터
    ├── export/
    │   ├── analyzer.py         # 분석 엔진
    │   ├── reports.py          # 리포트 생성
    │   └── blog_generator.py   # 블로그 생성
    └── export_report.sh        # 수동 실행
```

---

## 🔍 블로그 기능

### 홈페이지 (`/`)
- 최신 연구 6개 표시
- 검색 박스
- 정렬 (최신순/오래된순/제목순)
- 카테고리 필터
- 통계 (총 연구, 업데이트 주기)

### 연구 목록 (`/research/`)
- 전체 연구 목록
- 검색, 정렬, 필터

### 사이드바
- 📌 사이트 소개
- 📁 카테고리 (6개)
- 🔥 최신 연구 (5개)
- 🏷️ 태그 클라우드
- 🚀 내부 시스템 링크

---

## 📊 분석 항목

### 토큰 효율성
- Input/Output 비율
- 캐시 히트율
- 총 비용
- 토큰당 품질

### 품질 지표
- 테스트 통과율
- 컴파일 성공율
- 러너별 성능

### 추세 분석
- 일별 세션 수
- 평균 품질 추이
- 토큰 사용 추이
- 비용 추이

### 모델 성능
- 모델별 효율성 비교
- 평균 품질, 시간, 비용

---

## 🛠️ 기술 스택

| 계층 | 기술 |
|------|------|
| 데이터 수집 | Claude Code Stop Hook |
| 저장소 | SQLite |
| 분석 | Python 3.11+ |
| 블로그 | Jekyll |
| 자동화 | GitHub Actions |
| 배포 | GitHub Pages |

---

## ✅ 체크리스트

- [ ] Git Pages 활성화 (Settings → Pages)
- [ ] `_config.yml` 확인
- [ ] 첫 분석 실행 (`bash .experiment/export_report.sh`)
- [ ] 블로그 접속 확인
- [ ] GitHub Actions 로그 확인

---

**마지막 업데이트**: 2026-10-07  
**상태**: ✅ 프로덕션 준비 완료

> 🎉 Claude Code 분석을 자동으로 블로그로 공유하세요!
