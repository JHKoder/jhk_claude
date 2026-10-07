# Task B: 기능 구현 - 간단한 API 엔드포인트

## 요구사항
FastAPI 백엔드에 사용자 데이터 캐싱 레이어 추가

### 현재 코드 (before)
```python
# main.py
from fastapi import FastAPI
app = FastAPI()

@app.get("/users/{user_id}")
def get_user(user_id: int):
    # DB에서 직접 조회
    user = fetch_user_from_db(user_id)
    return user
```

### 요구사항
- Redis/메모리 캐시 레이어 추가 (TTL: 5분)
- 캐시 miss 시 DB 조회, hit 시 캐시 반환
- `GET /users/{user_id}` - 캐시 적용
- `POST /cache-clear` - 전체 캐시 초기화
- 테스트 케이스:
  - `test_get_user_cache_miss()` - 첫 호출은 DB에서, 토큰 저장
  - `test_get_user_cache_hit()` - 두 번째 호출은 캐시에서 (DB 호출 없음)
  - `test_cache_clear()` - POST 후 다시 DB에서 조회
  - `test_cache_expiration()` - 5분 후 자동 만료

## 성공 기준
- 모든 테스트 통과
- complexity_score = 6 (중간 난이도)
