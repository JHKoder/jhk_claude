# Task 5 Report: 대시보드 UI 업데이트

## 완료 상태: DONE

## 변경 파일

### 생성
- `.experiment/templates/quality_comparison.html` — 품질 vs 토큰 scatter 차트 + 비교 테이블

### 수정
- `.experiment/server.py`
  - `DB_PATH` import 추가
  - `/api/quality-metrics` GET 라우트 → `_serve_quality_metrics()` (SQLite 쿼리)
  - `/quality-comparison` GET 라우트 → `_serve_quality_comparison()`
- `.experiment/templates/dashboard.html`
  - `.main-tabs` / `.main-tab` / `.tab-content` CSS 추가
  - 헤더 아래 탭 바 (Overview / Sessions / Quality Comparison)
  - 기존 `.page` div를 `#mainTab0` 으로 감쌈
  - `#mainTab1` (Sessions 준비 중), `#mainTab2` (iframe → /quality-comparison) 추가
  - `switchMainTab()` JS 함수 추가

## 주요 결정 사항
- `DB_PATH`는 store.py에서 이미 export됨 — server.py가 직접 sqlite3로 쿼리
- `_serve_quality_comparison`은 `_load_template` 패턴 재사용 (HTMLResponse 없음, 표준 라이브러리만)
- 기존 대시보드에 탭이 없어 새로 추가; 기존 콘텐츠는 그대로 tab0에 유지
