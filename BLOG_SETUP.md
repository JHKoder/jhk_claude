# 🌐 Git Pages 블로그 완벽 설정 가이드

## 🎯 개요

Claude Code 실험 분석을 자동으로 **Jekyll 블로그**로 변환하고 **GitHub Pages**에 배포합니다.

### 핵심 기능
- ✅ **자동 분석**: SQLite 데이터 → Markdown 리포트
- ✅ **자동 게시**: 분석 → Jekyll 게시물 → 블로그
- ✅ **블로그 UI**: 사이드바, 검색, 필터, 정렬
- ✅ **매일 업데이트**: 자정마다 자동 생성 & 커밋

---

## 📋 설정 단계

### 1️⃣ Git Pages 활성화 (5분)

1. **GitHub 저장소 이동**
   ```
   https://github.com/YOUR_USERNAME/jhk_claude
   ```

2. **Settings 탭 클릭**
   ```
   Settings → Pages
   ```

3. **Source 설정**
   - **Branch**: `main`
   - **Folder**: `/root` 또는 `/docs`
   - **Save** 클릭

4. **확인**
   ```
   ✅ Your site is live at: https://YOUR_USERNAME.github.io/jhk_claude
   ```

> ⚠️ 변경 적용까지 1-2분 소요됩니다.

---

## 📁 블로그 구조

```
jhk_claude/
├── _config.yml              # Jekyll 설정
├── _layouts/
│   ├── default.html        # 기본 레이아웃 (사이드바 포함)
│   └── research.html       # 연구 게시물 레이아웃
├── _research/              # 연구 게시물 (자동 생성)
│   ├── 2026-10-07-daily-analysis.md
│   ├── 2026-10-07-efficiency-analysis.md
│   └── ...
├── index.md                 # 홈페이지
├── research/
│   └── index.md            # 연구 목록
├── about/
│   └── index.md            # 프로젝트 소개
└── assets/
    └── style.css           # (Jekyll이 자동 생성)
```

### 페이지 구조

| URL | 파일 | 설명 |
|-----|------|------|
| `/` | `index.md` | 홈페이지 (최신 연구 6개) |
| `/research/` | `research/index.md` | 연구 목록 (전체) |
| `/research/2026-10-07-daily-analysis/` | `_research/2026-10-07-daily-analysis.md` | 개별 게시물 |
| `/about/` | `about/index.md` | 프로젝트 소개 |

---

## 🎨 블로그 레이아웃

### 홈페이지 (`/`)

```
┌─────────────────────────────────────────────────────────┐
│ 🧪 JHK Claude Research Lab                             │
│ 홈  연구  가이드  소개                                  │
└─────────────────────────────────────────────────────────┘

  [검색 박스...................................]
  
  [📅 최신순] [📅 오래된순] [📝 제목순]
  
  [전체] [성능 분석] [효율성] [품질] [추세] [모델]

┌──────────────────────────────────┐  ┌────────────────────┐
│ 📚 최근 연구                       │  │ 📌 이 사이트        │
│                                   │  │                    │
│ • 토큰 효율성 분석    [2026-10-07] │  │ Claude Code 실험    │
│ • 품질 지표 분석      [2026-10-07] │  │ 연구 블로그입니다.  │
│ • 30일 추세 분석      [2026-10-06] │  │ → 전체 소개         │
│                                   │  │                    │
│ ┌─ 카드 1 ─┐ ┌─ 카드 2 ─┐        │  │ 📁 카테고리         │
│ │ 제목...   │ │ 제목...   │        │  │ • 성능 분석 (4)     │
│ │ 2026...   │ │ 2026...   │        │  │ • 효율성 (3)        │
│ │ 요약....  │ │ 요약....  │        │  │ • 품질 (2)          │
│ │ #tag      │ │ #tag      │        │  │                    │
│ └──────────┘ └──────────┘        │  │ 🔥 최신 연구        │
│                                   │  │ • 첫번째           │
└──────────────────────────────────┘  │ • 두번째           │
                                      │ • 세번째           │
                                      │                    │
                                      │ 🏷️ 태그            │
                                      │ #efficiency       │
                                      │ #trends           │
                                      │ #quality          │
                                      │                    │
                                      │ 🚀 내부 시스템      │
                                      │ • 실험 분석        │
                                      │ • 라이브 대시보드   │
                                      │ • 시스템 설정      │
                                      └────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ 🔗 링크          📚 리소스         👤 저자              │
│ • GitHub        • 시스템 가이드   • Contact           │
│ • 연구          • 분석 리포트    • GitHub            │
│ • 소개          • 사용 가이드                         │
└─────────────────────────────────────────────────────────┘
```

### 연구 목록 (`/research/`)

```
검색 박스 + 정렬 버튼 + 카테고리 필터

[카드 1] [카드 2] [카드 3]
[카드 4] [카드 5] [카드 6]
...
```

### 연구 게시물 (`/research/2026-10-07-daily-analysis/`)

```
제목
2026년 10월 07일 | 저자 | 5분 | 카테고리: 일일 분석

[태그] [태그] [태그]

---

## 📊 본문 내용

테이블, 통계, 분석 결과...

---

## 📌 관련 연구

[관련1] [관련2] [관련3]
```

---

## 🔧 설정 파일

### `_config.yml` (Jekyll 설정)

```yaml
title: "JHK Claude Research Lab"
description: "Claude Code 성능 분석 및 실험 연구소"
url: "https://github.com/JHKoder/jhk_claude"
theme: minima
plugins:
  - jekyll-feed
  - jekyll-seo-tag
locale: ko_KR
paginate: 10
```

### `_layouts/default.html`

기본 레이아웃 (모든 페이지가 상속):
- 헤더 (네비게이션)
- 메인 콘텐츠
- 사이드바 (카테고리, 최신 연구, 태그, 링크)
- 푸터

### `_layouts/research.html`

연구 게시물 레이아웃:
- 제목 & 메타데이터
- 본문 (마크다운)
- 관련 연구 (태그 기반)

---

## 📝 게시물 작성 규격

### 자동 생성 게시물 (분석 → 블로그)

```markdown
---
layout: research
title: "일일 분석 - 2026-10-07"
date: 2026-10-07T09:00:00+09:00
author: "Experiment Bot"
category: "일일 분석"
tags: ["daily", "session", "analysis"]
excerpt: "Claude Code 세션 7개 분석"
---

## 📊 오늘의 실험 결과

본문...
```

**프론트매터 필수 항목**:
- `title`: 제목
- `date`: 발행일 (ISO 8601)
- `layout`: `research` (고정)
- `category`: 카테고리 (1개)
- `tags`: 태그 배열 (여러 개)
- `excerpt`: 요약 (선택사항)

---

## 🤖 자동화 플로우

### 매일 자정 (자동)

```
1. Stop Hook 실행
   └→ .experiment/experiment.db에 세션 저장

2. GitHub Actions (experiment-report.yml) 실행
   ├→ 분석 엔진 실행
   │  └→ Markdown 리포트 생성 (docs/experiments/)
   │
   ├→ 블로그 생성기 실행
   │  └→ Jekyll 게시물 생성 (_research/)
   │
   └→ Git 커밋 & 푸시
      ├→ docs/experiments/* 커밋
      ├→ _research/* 커밋
      └→ Jekyll 빌드 & 배포 (자동)
```

### 수동 실행

```bash
# 즉시 분석 & 블로그 생성
bash .experiment/export_report.sh

# 커밋 & 푸시 필요
git add docs/experiments/ _research/
git commit -m "docs(research): add analysis"
git push
```

---

## 🔍 기능 상세

### 1️⃣ 검색 기능

**위치**: 홈페이지 / 연구 목록 페이지

**작동**: JavaScript로 실시간 검색
- 제목 검색
- 내용 검색
- 즉시 필터링

### 2️⃣ 정렬 기능

**옵션**:
- 📅 **최신순**: 최근 게시물 먼저
- 📅 **오래된순**: 오래된 게시물 먼저
- 📝 **제목순**: 제목 가나다순

### 3️⃣ 필터링

**카테고리 필터**:
- 전체
- 성능 분석
- 효율성
- 품질 지표
- 추세 분석
- 모델 비교

**태그 필터**: 사이드바에서 태그 클릭

### 4️⃣ 사이드바

**고정 섹션**:
- 📌 사이트 소개
- 📁 카테고리 (드롭다운)
- 🔥 최신 연구 (5개)
- 🏷️ 태그 클라우드
- 🚀 내부 시스템 (실험 분석, 대시보드 등)

---

## 🎨 커스터마이징

### 색상 변경

파일: `_layouts/default.html` (상단 `<style>`)

```css
:root {
    --primary-color: #0366d6;        /* 링크, 버튼 */
    --primary-dark: #044289;         /* 호버 */
    --border-color: #e1e4e8;         /* 테두리 */
    --bg-light: #fafbfc;             /* 배경 */
    --text-dark: #24292e;            /* 본문 */
    --text-secondary: #586069;       /* 회색 텍스트 */
}
```

### 폰트 변경

파일: `_layouts/default.html`

```css
body {
    font-family: YOUR_FONT_HERE;
}
```

### 레이아웃 너비 조정

파일: `_layouts/default.html`

```css
.container {
    max-width: 1280px;  /* ← 이 값 변경 */
}
```

---

## 📊 블로그 게시물 자동 생성

### `blog_generator.py` 작동

매일 자정에 다음 게시물 자동 생성:

1. **일일 분석** (매일)
   - 세션 기록 테이블
   - 통계 요약

2. **효율성 분석** (매일)
   - 토큰 효율성
   - 캐시 히트율

3. **품질 지표** (매일)
   - 테스트 통과율
   - 러너별 성능

4. **모델 비교** (매일)
   - 모델별 성능 테이블

5. **추세 분석** (주1회: 월요일)
   - 30일 일별 데이터
   - 추세 그래프 데이터

---

## 🚀 배포 확인

### 1. 로컬 프리뷰

```bash
# Jekyll 설치 (처음 1회)
gem install jekyll bundler

# 로컬 서버 실행
bundle exec jekyll serve

# 브라우저에서 확인
# http://localhost:4000/jhk_claude
```

### 2. GitHub Pages 확인

```
https://YOUR_USERNAME.github.io/jhk_claude
```

### 3. 빌드 상태 확인

GitHub 저장소:
- **Actions** 탭 → "pages build and deployment"
- ✅ 초록색 = 성공
- ❌ 빨간색 = 오류

---

## 🐛 문제 해결

### 블로그가 표시되지 않음

1. **GitHub Pages 활성화 확인**
   ```
   Settings → Pages → Source 확인
   ```

2. **`_config.yml` 확인**
   ```yaml
   url: "https://github.com/YOUR_USERNAME/jhk_claude"
   baseurl: "/jhk_claude"
   ```

3. **파일명 확인**
   - Markdown: `.md` 확장자
   - 레이아웃: `_layouts/` 디렉토리
   - 게시물: `_research/` 디렉토리

### 검색/정렬 기능 작동 안 함

```javascript
// _layouts/default.html에서 확인
// JavaScript 함수가 정의되어 있는지 확인
```

### 블로그 게시물이 자동 생성되지 않음

1. **GitHub Actions 로그 확인**
   ```
   Actions → Daily Experiment Report → 최신 실행
   ```

2. **Python 패스 확인**
   ```bash
   python3 -c "import sys; sys.path.insert(0, '.experiment'); from export.blog_generator import generate_blog_posts; print('OK')"
   ```

---

## 📊 예상 결과

### 1주 후
- 블로그: 7개 게시물
- 사이드바: 최신 연구 자동 업데이트
- 검색: 7개 결과

### 1개월 후
- 블로그: 30개 게시물
- 태그 클라우드: 20+ 태그
- 카테고리: 6개 분류

---

## 🔗 유용한 링크

- [Jekyll 공식 문서](https://jekyllrb.com/)
- [GitHub Pages 가이드](https://pages.github.com/)
- [Minima 테마](https://github.com/jekyll/minima)
- [Markdown 문법](https://www.markdownguide.org/)

---

## ✅ 체크리스트

- [ ] Git Pages 활성화 (Settings → Pages)
- [ ] `_config.yml` URL 확인
- [ ] `_layouts/default.html` 문법 확인
- [ ] 첫 게시물 수동 생성 테스트
- [ ] GitHub Actions 로그 확인
- [ ] 블로그 접속 확인 (https://...)

---

**마지막 업데이트**: 2026-10-07  
**시스템 상태**: ✅ 준비 완료  
**다음 단계**: Git Pages 활성화
