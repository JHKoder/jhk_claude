# AI 인수인계 프롬프트

새 Claude Code 세션을 시작할 때 이 파일의 내용을 첫 메시지로 붙여넣는다.

---

## 프로젝트 개요

**서비스**: `midam.store` — 장인 수공예 마켓플레이스 (장인↔고객 거래 플랫폼)  
**기술 스택**: Java 17 + Spring Boot 3 + JPA + QueryDSL + Redis + PostgreSQL  
**서버 포트**: 9090 (로컬), Spring Actuator `/healthz`  
**브랜치 전략**: git-flow (`main` → `release` → `develop` → `feat/*`)  
**현재 브랜치**: `develop`

---

## 필수 규칙 (변경 불가)

### 코드
- 기술 스택·버전 다운그레이드 절대 금지
- ORM은 JPA 기본, 성능 이슈 시 QueryDSL / Native Query
- `@Valid` 1차 유효성 → Service/Domain 비즈니스 검증
- 트랜잭션 `@Transactional(readOnly=true)` 메서드 단위 명시
- null을 비즈니스 로직에 포함 금지 — Optional 또는 예외 사용
- setter/property 사용 금지, `@RequiredArgsConstructor` 우선

### 테스트
- 컨트롤러 엔드포인트 = REST Docs 테스트 필수
- `MockMvcRestDocumentationWrapper.document()` + `ResourceSnippetParameters.builder()` 형태
- GIVEN-WHEN-THEN 패턴, `@DisplayName` 한글
- 테스트 클래스 분류: `JunitTest`, `JunitExceptionTest`, `IntegrationTest`, `IntegrationExceptionTest`
- 테스트 코드 내 JSON 리터럴 금지 → `ObjectMapper.writeValueAsString()` 사용
- 코드/라인 커버리지 95% 이상

### Git
- `main`, `develop` 브랜치 직접 커밋 금지
- PR 생성·직접 push 금지 → 작업 완료 시 `/pr-output.md` 생성(덮어쓰기)
- 커밋 메시지: 제목 영어, 본문 한국어
- 커밋에 Claude 흔적(Co-Authored-By 등) 남기지 않기
- 기능·성능/인프라·테스트 단위로 커밋 분리

### OpenAPI
- POST 생성 → 201 반환, 204는 빈 바디만
- datetime → `Instant` (UTC, `Z` 접미사)
- 내부 API: `/internal/**` — `hasRole("AGENT")` 보호
- `documentation.gradle`의 `roleByOperationId`에 operationId별 역할 등록

---

## 패키지 구조

```
src/main/java/com/jangingmall/backend/
├── admin/          관리자
├── chatbot/        AI 챗봇
├── content/        장인 콘텐츠·AI 생성 승인 흐름
├── global/         공통 설정, 예외, 인증
├── image/          이미지 업로드 (S3)
├── member/         회원·장인·이메일 인증·계정 잠금
├── notification/   알림
├── payment/        결제·주문·반품·배송
├── product/        상품
├── revalidate/     Vercel 스테이징 캐시 재검증 웹훅
```

---

## 최근 완료된 주요 작업

| 작업 | 브랜치 | 내용 |
|---|---|---|
| QA No.2 | `feat/payment-compensation` | PG 승인 후 로컬 저장 실패 시 paymentGateway.cancel() 보상 |
| QA No.16/18 | `feat/return-7day-deadline` | 배송완료 7일 반품 조건 + 24h 미처리 관리자 알림 스케줄러 |
| QA No.20/21 | `feat/email-verification-and-account-lock` | 이메일 인증코드 6자리 + 5회 실패 시 30분 잠금 |
| Vercel 웹훅 | `feat/revalidate-webhook` | HMAC-SHA256 서명, @TransactionalEventListener |
| 공개 API 문서 | `feat/public-api-docs` | GitHub Pages 배포, Postman Collection, TypeScript 타입 |
| E2E 통합 테스트 | `feat/user-journey-e2e` | 가입→구매→반품 15개 시나리오 |
| 샘플 시드 데이터 | `develop` | 장인 61명·제품 729개 data.sql |

---

## 진행 중인 작업

| 작업 | 브랜치 | 상태 |
|---|---|---|
| GitHub Pages 산출물 추가 | `feat/public-docs-artifacts` | 진행 중 — Postman·TS·HTML 요약 3개 산출물 추가 |

---

## 충돌 방지

새 작업 시작 전 반드시 `.claude/agent/agent_live.md`를 읽는다.  
브랜치·파일이 겹치면 사용자에게 보고 후 대기한다.

---

## .experiment 실험 툴

Claude Code 세션의 토큰·비용·품질을 자동 수집해 브라우저 대시보드로 비교하는 툴.

### 빠른 사용
```bash
exp serve          # 대시보드 (http://localhost:7788)
exp list           # 수집된 실험 목록
exp show <id>      # 단일 실험 상세
exp compare <a> <b>  # A/B 터미널 비교
exp rate <id> <1-5>  # 수동 평점
exp analyze        # AI 분석 (Haiku)
```

### 구조
```
.experiment/
├── server.py           — 대시보드 서버 (포트 7788)
├── templates/
│   ├── dashboard.html  — 메인 UI
│   ├── harness.html    — Harness Explorer
│   └── snapshot_viewer.html  — 스냅샷 뷰어 (__PLACEHOLDER__ 치환 방식)
├── test_templates.py   — 템플릿 구조 회귀 테스트
│                         실행: python3 .experiment/test_templates.py
├── collectors/         — Stop Hook 수집기
└── config/tasks.json   — 실험 태스크 정의
```

### 템플릿 수정 후 필수
```bash
python3 .experiment/test_templates.py
```
탭↔섹션 인덱스 불일치, 플레이스홀더 미치환, f-string 잔류, 인라인 파일 삽입을 검증한다.

---

## 참고 경로

| 항목 | 경로 |
|---|---|
| 규칙 모음 | `.claude/rules/` |
| 에이전트 작업 레지스트리 | `.claude/agent/agent_live.md` |
| PR 출력 | `/pr-output.md` (루트, 커밋 안 함) |
| OpenAPI 문서화 | `gradle/documentation.gradle` |
| BE QA 시트 | `docs/BE_QA_시트.csv` |
