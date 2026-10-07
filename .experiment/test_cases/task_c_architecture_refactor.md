# Task C: 아키텍처 변경 - 서비스 계층 분리

## 요구사항
기존 모놀리식 Python 백엔드를 도메인별 서비스 계층으로 리팩토링

### 현재 구조 (before)
```
app.py (1000+ 라인)
├── user 관련 로직
├── product 관련 로직
├── order 관련 로직
├── DB 쿼리
└── 비즈니스 로직 섞임
```

### 요구사항
- `services/user_service.py` - 사용자 도메인 로직 분리
- `services/product_service.py` - 상품 도메인 로직 분리
- `services/order_service.py` - 주문 도메인 로직 분리
- 각 서비스는 명확한 인터페이스만 노출
- 기존 API 엔드포인트는 변경 없음 (역호환성)
- 테스트 케이스:
  - `test_user_service_create()` - 사용자 생성
  - `test_user_service_get()` - 사용자 조회
  - `test_product_service_list()` - 상품 목록
  - `test_order_service_create_with_validation()` - 주문 생성 + 검증
  - `test_api_endpoint_still_works()` - 기존 API 호환성
  - (총 8-10개 테스트)

## 성공 기준
- 모든 테스트 통과
- complexity_score = 9 (복잡한 작업)
