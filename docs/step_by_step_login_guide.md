# 순수 파이썬 로그인 API — 1단계부터 직접 구현 가이드

이 문서는 프레임워크 없이 **Python 표준 라이브러리만**으로 로그인 API를 직접 구현하면서 배우기 위한 **실습 안내서**입니다.

- **목표**: `GET /health`, `POST /signup`, `POST /login`, `GET /me`(보호된 API)까지 구현
- **핵심 개념**: 서버(HTTPServer) → 라우터(경로/메서드 분기) → 핸들러(비즈니스 로직) → 유틸/DB/인증(도구 모듈)
- **인증 방식**: 서명 토큰(JWT) 대신 **세션 방식(DB에 token→user_id 저장)** 으로 학습

---

## 준비: 디렉토리와 실행 위치

아래 경로에서 작업합니다.

- `/home/mingun/backend_with_no_framework/`

파일 구조(최종 목표):

```
backend_with_no_framework/
├── server.py
├── router.py
├── handlers.py
├── utils.py
├── database.py
├── auth.py
├── README.md
└── docs/
    ├── data_flow.png
    ├── folder_structure.png
    └── step_by_step_login_guide.md
```

> 참고: `users.db`는 **런타임에 생성되는 파일**입니다(소스 파일이 아님). 필요하면 `.gitignore`에 넣는 편이 좋습니다.

---

## 큰 그림(개념)

요청이 들어오면 내부적으로 이런 순서로 움직입니다.

1. **Client**가 HTTP 요청을 보냄 (curl/Postman/브라우저)
2. **server.py**(HTTPServer + BaseHTTPRequestHandler)가 요청을 받음
3. **router.py**가 `(METHOD, PATH)`를 기준으로 “어떤 핸들러 함수를 부를지” 결정
4. **handlers.py**가 비즈니스 로직 수행
5. handlers가 필요에 따라
   - **utils.py**(JSON 파싱/응답 전송)
   - **database.py**(SQLite 저장/조회)
   - **auth.py**(비밀번호 해싱/검증)
   를 **호출**해서 사용

---

## 응답 포맷 규칙(통일)

이 프로젝트에서는 응답 JSON을 아래 규칙으로 통일합니다.

- **성공**: `{"success": true, "data": {...}}` 또는 `{"success": true, "message": "..."}`
- **실패**: `{"success": false, "message": "..."}`

이렇게 통일하면 프론트/클라이언트가 에러 처리를 일관되게 할 수 있고, 디버깅도 쉬워집니다.

---

## 1단계: 기본 HTTP 서버 띄우기 (+ GET /health)

### 지금 내가 하는 것(개념)

프레임워크 없이도 “웹 서버”는 결국 아래만 하면 됩니다.

- TCP 포트(예: 8000)에서 연결을 받아 HTTP 요청을 읽고
- 요청의 **메서드(GET/POST)**, **경로(/health 등)** 를 확인한 뒤
- 상태 코드(200/404 등)와 JSON 본문을 돌려주는 것

Python 표준 라이브러리 `http.server`는 이 기본 기능을 제공합니다.

여기서 `BaseHTTPRequestHandler`는 “요청 1개를 처리하는 핸들러 객체”이고,
`do_GET`, `do_POST` 같은 메서드를 오버라이드하면 “GET 요청이 오면 무엇을 할지”를 정의할 수 있습니다.

### 생성할 파일

- `server.py`

### 내가 직접 구현해야 할 내용(체크리스트)

1. `HTTPServer`, `BaseHTTPRequestHandler` import
2. `RequestHandler(BaseHTTPRequestHandler)` 클래스 만들기
3. `do_GET` 구현
   - `self.path == "/health"` 이면 200 + `{"status":"ok"}`
   - 그 외는 404 + `{"success": false, "message": "Not Found"}`
4. `do_POST` 구현
   - 일단은 아무 POST나 200 + `{"message":"hello"}` (학습용)
5. `if __name__ == "__main__":`에서 서버 실행
   - `HTTPServer(("localhost", 8000), RequestHandler).serve_forever()`

### 여기서 중요한 HTTP 포인트(짧게 정리)

- **Status Code**: 200(성공), 404(없음)
- **Header**: `Content-Type: application/json`은 “본문이 JSON이다”라고 알려줌
- **Body**: `wfile.write()`는 바이트로 써야 하므로 `.encode()` 필요

### 테스트(직접 확인)

서버 실행:

```bash
python server.py
```

다른 터미널에서 확인:

```bash
curl http://localhost:8000/health
# 기대: {"status":"ok"} (200)

curl http://localhost:8000/anything
# 기대: {"success":false,"message":"Not Found"} (404)

curl -X POST http://localhost:8000/test
# 기대: {"message":"hello"} (200)
```

### 정답 코드(막히면 참고)

직접 구현해보고 안 되면 아래를 그대로 붙여 넣어서 비교해보세요.

```python
from http.server import HTTPServer, BaseHTTPRequestHandler
import json


class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok"}).encode())
            return

        self.send_response(404)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"success": False, "message": "Not Found"}).encode())

    def do_POST(self):
        # 1단계에서는 POST 바디를 아직 사용하지 않는다(연결/응답 확인용)
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"message": "hello"}).encode())


if __name__ == "__main__":
    server = HTTPServer(("localhost", 8000), RequestHandler)
    print("Server running on http://localhost:8000")
    server.serve_forever()
```

---

## 2단계: JSON 요청/응답 유틸리티 만들기 (utils.py)

### 지금 내가 하는 것(개념)

실제 API를 만들면 `send_response`, `send_header`, `end_headers`, `wfile.write`를 매번 반복하게 됩니다.
이걸 **한 함수로 묶어 재사용**하면 코드가 짧아지고 실수도 줄어듭니다.

또한 POST 요청의 본문(body)은 보통 JSON입니다. 이걸 읽고 파싱하는 것도 반복되므로 **파싱 함수**로 뺍니다.

> 프레임워크가 해주는 “자동 JSON 파싱, JSON 응답”을 우리가 직접 만드는 단계입니다.

### 생성할 파일

- `utils.py`

### 내가 직접 구현해야 할 내용(체크리스트)

1. `send_json_response(handler, status_code, data)` 함수
   - status_code 설정
   - `Content-Type: application/json` 헤더 설정
   - `data`를 JSON으로 덤프 후 `.encode()` 해서 전송
2. `parse_request_body(handler)` 함수
   - `Content-Length` 읽기(없으면 0)
   - 0이면 `ValueError` 발생
   - body 읽고 JSON 파싱
   - JSON 파싱 실패 시 `ValueError` 발생

### 테스트(직접 확인)

`server.py`에서 직접 응답 만들던 코드를 `utils.send_json_response`로 리팩터링했을 때 똑같이 동작하면 성공입니다.

### 정답 코드(막히면 참고)

```python
import json


def send_json_response(handler, status_code, data):
    handler.send_response(status_code)
    handler.send_header("Content-Type", "application/json")
    handler.end_headers()
    handler.wfile.write(json.dumps(data).encode())


def parse_request_body(handler):
    content_length = int(handler.headers.get("Content-Length", 0))
    if content_length <= 0:
        raise ValueError("Empty request body")

    body = handler.rfile.read(content_length)
    try:
        return json.loads(body)
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON")
```

---

## 3단계: 라우터 만들기 (router.py)

### 지금 내가 하는 것(개념)

엔드포인트가 늘어나면 `do_GET`/`do_POST`에서 `if self.path == ...`로 분기하는 건 금방 복잡해집니다.

**라우터(router)**는 아래를 관리합니다.

- “GET /health가 오면 handle_health를 호출”
- “POST /login이 오면 handle_login을 호출”

즉, 라우터는 `(method, path)` → `handler_function`의 매핑 테이블입니다.

그리고 `self.path`에는 쿼리스트링이 붙을 수 있으므로(`/login?next=/a`) `urlparse`로 **경로만** 뽑는 습관이 중요합니다.

### 생성할 파일

- `router.py`

### 내가 직접 구현해야 할 내용(체크리스트)

1. `routes = {}` 선언 (키: `(method, path)` / 값: 함수)
2. `register_route(method, path, handler_func)`
3. `dispatch(handler)`
   - `method = handler.command`
   - `path = urlparse(handler.path).path`
   - routes에서 찾으면 호출, 없으면 404 JSON 응답

### 테스트(직접 확인)

아직 핸들러가 없으니, 일단 import가 되는지만 확인합니다.

```bash
python -c "import router; print('OK')"
```

### 정답 코드(막히면 참고)

```python
from urllib.parse import urlparse
from utils import send_json_response


routes = {}


def register_route(method, path, handler_func):
    routes[(method, path)] = handler_func


def dispatch(handler):
    method = handler.command
    path = urlparse(handler.path).path
    key = (method, path)

    handler_func = routes.get(key)
    if handler_func:
        handler_func(handler)
        return

    send_json_response(handler, 404, {"success": False, "message": "Not Found"})
```

---

## 4단계: 핸들러 골격 만들고(server → router → handler) 연결하기

### 지금 내가 하는 것(개념)

여기서부터 “배관 공사”입니다.

- server.py는 요청을 받는다
- router.py는 어디로 보낼지 결정한다
- handlers.py는 실제 동작을 한다

핸들러에 아직 비즈니스 로직(DB/해싱/세션)이 없더라도, **하드코딩 응답**을 반환하도록만 만들어서
전체 연결이 제대로 되는지 먼저 확인합니다.

이 단계를 해두면 이후에는 핸들러 함수 내부 로직만 채우면 되어서 덜 꼬입니다.

### 생성/수정할 파일

- `handlers.py` (생성)
- `server.py` (수정: `router.dispatch(self)` 사용)

### 내가 직접 구현해야 할 내용(체크리스트)

1. `handlers.py`에 아래 3개의 핸들러 함수를 만든다(하드코딩 응답):
   - `handle_health(handler)` → 200
   - `handle_signup(handler)` → 200
   - `handle_login(handler)` → 200
2. `handlers.py`에 `register_routes()` 함수를 만들고, 라우터에 라우트 3개를 등록한다.
   - `GET /health` → `handle_health`
   - `POST /signup` → `handle_signup`
   - `POST /login` → `handle_login`
3. `server.py`에서 `do_GET`, `do_POST`는 분기 로직 없이 **무조건** `router.dispatch(self)`만 호출하게 바꾼다.
4. 서버 실행 전에 `handlers.register_routes()`를 호출한다(라우트 등록이 먼저 되어야 함).

### 테스트(직접 확인)

서버 실행:

```bash
python server.py
```

다른 터미널에서 확인:

```bash
curl http://localhost:8000/health
# 기대: {"success":true,"message":"server is running"} (200)

curl -X POST http://localhost:8000/signup
# 기대: {"success":true,"message":"signup placeholder"} (200)

curl -X POST http://localhost:8000/login
# 기대: {"success":true,"message":"login placeholder"} (200)

curl http://localhost:8000/notfound
# 기대: {"success":false,"message":"Not Found"} (404)
```

### 정답 코드(막히면 참고)

`handlers.py`:

```python
from utils import send_json_response
import router


def handle_health(handler):
    send_json_response(handler, 200, {"success": True, "message": "server is running"})


def handle_signup(handler):
    send_json_response(handler, 200, {"success": True, "message": "signup placeholder"})


def handle_login(handler):
    send_json_response(handler, 200, {"success": True, "message": "login placeholder"})


def register_routes():
    router.register_route("GET", "/health", handle_health)
    router.register_route("POST", "/signup", handle_signup)
    router.register_route("POST", "/login", handle_login)
```

`server.py`(수정 후):

```python
from http.server import HTTPServer, BaseHTTPRequestHandler
import router
import handlers


class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        router.dispatch(self)

    def do_POST(self):
        router.dispatch(self)


if __name__ == "__main__":
    handlers.register_routes()
    server = HTTPServer(("localhost", 8000), RequestHandler)
    print("Server running on http://localhost:8000")
    server.serve_forever()
```

---

## 5단계: DB 붙이기 (SQLite + users 테이블)

### 지금 내가 하는 것(개념)

회원가입은 결국 “유저 정보를 저장”하는 작업이고, 로그인은 “유저 정보를 조회해서 검증”하는 작업입니다.

학습용으로는 외부 DB 설치 없이 파일 하나로 동작하는 `sqlite3`가 적합합니다.

그리고 중요한 실무 규칙 1개:

- SQL에 값을 문자열로 이어붙이지 말고, 항상 `?` 바인딩을 사용한다(= SQL Injection 방지)

### 생성할 파일

- `database.py`

### 내가 직접 구현해야 할 내용(체크리스트)

1. `DB_PATH = "users.db"` 선언
2. `get_connection()` 함수
   - `sqlite3.connect(DB_PATH)`
   - `conn.row_factory = sqlite3.Row` (조회 결과를 dict처럼 쓰기 위해)
3. `init_db()` 함수
   - `users` 테이블 생성(없으면)
   - 컬럼:
     - `id INTEGER PRIMARY KEY AUTOINCREMENT`
     - `username TEXT UNIQUE NOT NULL`
     - `password_hash TEXT NOT NULL`
     - `salt TEXT NOT NULL`
     - `created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP`
4. `create_user(username, password_hash, salt)`
5. `get_user_by_username(username)` → 없으면 `None`

### 테스트(직접 확인)

```bash
python -c "
from database import init_db, create_user, get_user_by_username
init_db()
create_user('testuser', 'fakehash', 'fakesalt')
u = get_user_by_username('testuser')
print(dict(u))
"
rm -f users.db
```

### 정답 코드(막히면 참고)

```python
import sqlite3

DB_PATH = "users.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()
    conn.close()


def create_user(username, password_hash, salt):
    conn = get_connection()
    conn.execute(
        "INSERT INTO users (username, password_hash, salt) VALUES (?, ?, ?)",
        (username, password_hash, salt),
    )
    conn.commit()
    conn.close()


def get_user_by_username(username):
    conn = get_connection()
    cur = conn.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cur.fetchone()
    conn.close()
    return user
```

---

## 6단계: 비밀번호 해싱 붙이기 (pbkdf2_hmac)

### 지금 내가 하는 것(개념)

비밀번호는 **절대 평문 저장 금지**입니다.

가장 단순한 접근은 `sha256(password)` 같은 해시이지만, 비밀번호 저장에는 적합하지 않습니다.
학습용이더라도 “왜 부적절한지”를 알고, 표준 라이브러리에서 가능한 더 나은 선택을 쓰는 게 좋습니다.

`hashlib.pbkdf2_hmac`는 아래를 제공합니다:

- 랜덤 `salt`로 같은 비밀번호라도 결과가 다르게 만듦
- `iterations`로 해시를 반복 수행해 brute-force 비용을 크게 올림

### 생성할 파일

- `auth.py`

### 내가 직접 구현해야 할 내용(체크리스트)

1. `hash_password(password)`:
   - `salt = os.urandom(32)`
   - `key = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, iterations=100_000)`
   - `(salt.hex(), key.hex())` 반환
2. `verify_password(password, salt_hex, hash_hex)`:
   - `salt = bytes.fromhex(salt_hex)`
   - 같은 방식으로 `key` 재계산
   - `key.hex() == hash_hex` 반환

### 테스트(직접 확인)

```bash
python -c "
from auth import hash_password, verify_password
salt, h = hash_password('mypassword')
print(verify_password('mypassword', salt, h))
print(verify_password('wrong', salt, h))
"
```

### 정답 코드(막히면 참고)

```python
import hashlib
import os


def hash_password(password):
    salt = os.urandom(32)
    key = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, iterations=100_000)
    return salt.hex(), key.hex()


def verify_password(password, salt_hex, hash_hex):
    salt = bytes.fromhex(salt_hex)
    key = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, iterations=100_000)
    return key.hex() == hash_hex
```

---

## 7단계: 회원가입/로그인 핸들러 “진짜 로직” 채우기

### 지금 내가 하는 것(개념)

지금까지 만든 것들을 조합합니다.

- 회원가입: 입력(JSON) → 검증 → 해싱 → DB 저장 → 응답
- 로그인: 입력(JSON) → DB 조회 → 해시 검증 → 응답

아직은 “로그인 상태”가 없습니다. 즉 7단계의 로그인은 “비밀번호가 맞는지만 확인”입니다.
로그인 상태(토큰/세션)는 8단계에서 완성합니다.

### 수정할 파일

- `handlers.py` (signup/login에 로직 추가)
- `server.py` (서버 시작 전에 `database.init_db()` 호출 추가)

### 내가 직접 구현해야 할 내용(체크리스트)

**handle_signup(handler)**:

1. `parse_request_body`로 JSON 파싱 → 실패하면 400
2. `username`, `password` 추출 → 빈 값이면 400
3. `get_user_by_username`으로 중복 체크 → 있으면 409
4. `hash_password`로 `(salt, password_hash)` 생성
5. `create_user`로 저장
6. 201 응답

**handle_login(handler)**:

1. JSON 파싱(실패 400)
2. username/password 검증(빈 값 400)
3. `get_user_by_username`으로 유저 조회(없으면 401)
4. `verify_password`로 검증(틀리면 401)
5. 성공 200 응답(토큰은 아직 없음)

**server.py**:

- `if __name__ == "__main__":`에서 `database.init_db()`를 `handlers.register_routes()`보다 먼저 호출

### 테스트(직접 확인)

```bash
rm -f users.db
python server.py
```

```bash
curl -X POST http://localhost:8000/signup \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"mypassword"}'

curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"mypassword"}'

curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"wrong"}'
```

### 정답 코드(막히면 참고)

이 단계는 파일 간 연결이 많아서, 막히면 아래를 그대로 참고하세요.

`handlers.py`(전체 예시):

```python
from utils import send_json_response, parse_request_body
from database import get_user_by_username, create_user
from auth import hash_password, verify_password
import router


def handle_health(handler):
    send_json_response(handler, 200, {"success": True, "message": "server is running"})


def handle_signup(handler):
    try:
        body = parse_request_body(handler)
    except ValueError as e:
        send_json_response(handler, 400, {"success": False, "message": str(e)})
        return

    username = body.get("username", "").strip()
    password = body.get("password", "")

    if not username or not password:
        send_json_response(handler, 400, {"success": False, "message": "Username and password are required"})
        return

    if get_user_by_username(username):
        send_json_response(handler, 409, {"success": False, "message": "Username already exists"})
        return

    salt, password_hash = hash_password(password)
    create_user(username, password_hash, salt)
    send_json_response(handler, 201, {"success": True, "message": "User created"})


def handle_login(handler):
    try:
        body = parse_request_body(handler)
    except ValueError as e:
        send_json_response(handler, 400, {"success": False, "message": str(e)})
        return

    username = body.get("username", "").strip()
    password = body.get("password", "")

    if not username or not password:
        send_json_response(handler, 400, {"success": False, "message": "Username and password are required"})
        return

    user = get_user_by_username(username)
    if not user:
        send_json_response(handler, 401, {"success": False, "message": "Invalid username or password"})
        return

    if not verify_password(password, user["salt"], user["password_hash"]):
        send_json_response(handler, 401, {"success": False, "message": "Invalid username or password"})
        return

    send_json_response(handler, 200, {"success": True, "message": "Login successful"})


def register_routes():
    router.register_route("GET", "/health", handle_health)
    router.register_route("POST", "/signup", handle_signup)
    router.register_route("POST", "/login", handle_login)
```

`server.py`(init_db 추가):

```python
from http.server import HTTPServer, BaseHTTPRequestHandler
import router
import handlers
import database


class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        router.dispatch(self)

    def do_POST(self):
        router.dispatch(self)


if __name__ == "__main__":
    database.init_db()
    handlers.register_routes()
    server = HTTPServer(("localhost", 8000), RequestHandler)
    print("Server running on http://localhost:8000")
    server.serve_forever()
```

---

## 8단계: 세션 저장소 추가(sessions 테이블 + 토큰 발급)

### 지금 내가 하는 것(개념)

7단계까지는 로그인 성공해도 “이후 요청에서 로그인 상태를 증명”할 방법이 없습니다.

세션 방식은 아래처럼 동작합니다.

1. 로그인 성공 → 서버가 랜덤 토큰 생성
2. DB의 `sessions` 테이블에 `token → user_id` 저장
3. 클라이언트에 토큰 반환
4. 클라이언트가 이후 요청에 `Authorization: Bearer <token>`으로 토큰을 보내면
5. 서버가 DB에서 토큰을 조회해 user_id를 찾고 인증 처리

즉, **토큰을 생성만 하는 건 인증이 아니다** → 서버가 검증/기억할 수 있어야 한다.

### 수정할 파일

- `database.py` (sessions 테이블 + create_session/get_user_by_token 추가)
- `handlers.py` (login 성공 시 token 반환)

### 내가 직접 구현해야 할 내용(체크리스트)

1. `init_db()`에 `sessions` 테이블 추가
   - `token TEXT PRIMARY KEY`
   - `user_id INTEGER NOT NULL`
   - `created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP`
2. `create_session(user_id)`:
   - `secrets.token_hex(32)`로 token 생성
   - INSERT 후 token 반환
3. `get_user_by_token(token)`:
   - sessions JOIN users 해서 유저 정보(id/username/created_at) 반환
4. `handle_login`에서 성공 시 `create_session(user["id"])` 호출 후 응답에 token 포함

### 테스트(직접 확인)

```bash
rm -f users.db
python server.py
```

```bash
curl -X POST http://localhost:8000/signup \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"mypassword"}'

curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"mypassword"}'
# 기대: {"success":true,"token":"...64자리..."}
```

### 정답 코드(막히면 참고)

`database.py`에 추가/확장(예시):

```python
import secrets


def init_db():
    conn = get_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS sessions (
            token TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        """
    )
    conn.commit()
    conn.close()


def create_session(user_id):
    token = secrets.token_hex(32)
    conn = get_connection()
    conn.execute("INSERT INTO sessions (token, user_id) VALUES (?, ?)", (token, user_id))
    conn.commit()
    conn.close()
    return token


def get_user_by_token(token):
    conn = get_connection()
    cur = conn.execute(
        """
        SELECT users.id, users.username, users.created_at
        FROM sessions
        JOIN users ON sessions.user_id = users.id
        WHERE sessions.token = ?
        """,
        (token,),
    )
    user = cur.fetchone()
    conn.close()
    return user
```

`handlers.py`의 로그인 성공 응답을 다음으로 변경:

```python
from database import create_session  # import 추가 필요

# ...
token = create_session(user["id"])
send_json_response(handler, 200, {"success": True, "token": token})
```

---

## 9단계: 보호된 API 추가 (GET /me)

### 지금 내가 하는 것(개념)

토큰을 “어디에 쓰는지” 보여주는 가장 좋은 예가 `GET /me`입니다.

- 클라이언트는 `Authorization: Bearer <token>`을 보내고
- 서버는 토큰으로 user를 찾아
- “현재 로그인한 사용자 정보”를 반환합니다.

이 패턴이 그대로 확장되어, 실제 서비스의 “내 주문 목록”, “내 프로필 수정” 같은 API가 됩니다.

### 수정할 파일

- `handlers.py` (`handle_me` 추가 + 라우트 등록)

### 내가 직접 구현해야 할 내용(체크리스트)

1. `Authorization` 헤더 읽기
2. `Bearer `로 시작하지 않으면 401
3. token 추출
4. `get_user_by_token(token)`으로 유저 조회
5. 없으면 401, 있으면 200 + 유저 정보 반환
6. 라우터에 `GET /me` 등록

### 테스트(직접 확인)

```bash
rm -f users.db
python server.py
```

```bash
# signup
curl -X POST http://localhost:8000/signup \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"mypassword"}'

# login (토큰 복사)
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"mypassword"}'

# 토큰 없이 /me -> 401
curl http://localhost:8000/me

# 토큰으로 /me -> 200
curl http://localhost:8000/me -H "Authorization: Bearer <토큰>"
```

### 정답 코드(막히면 참고)

`handlers.py`에 추가:

```python
from database import get_user_by_token  # import 추가 필요


def handle_me(handler):
    auth_header = handler.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        send_json_response(handler, 401, {"success": False, "message": "Authorization header required"})
        return

    token = auth_header[len("Bearer ") :]
    user = get_user_by_token(token)
    if not user:
        send_json_response(handler, 401, {"success": False, "message": "Invalid or expired token"})
        return

    send_json_response(
        handler,
        200,
        {"success": True, "data": {"id": user["id"], "username": user["username"], "created_at": user["created_at"]}},
    )
```

`register_routes()`에 추가:

```python
router.register_route("GET", "/me", handle_me)
```

---

## 10단계: 전체 흐름(curl)로 최종 검증

### 지금 내가 하는 것(개념)

정상 케이스만 되는 API는 반쪽짜리입니다.
**에러 케이스**까지 모두 확인해야 서버가 “진짜로” 동작한다고 말할 수 있습니다.

### 최종 테스트 시나리오(8개)

서버 실행(초기화):

```bash
rm -f users.db
python server.py
```

테스트:

```bash
# 1) health
curl http://localhost:8000/health

# 2) signup success
curl -X POST http://localhost:8000/signup \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"mypassword"}'

# 3) signup duplicate -> 409
curl -X POST http://localhost:8000/signup \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"mypassword"}'

# 4) login success -> token
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"mypassword"}'

# 5) login wrong password -> 401
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"wrong"}'

# 6) /me without token -> 401
curl http://localhost:8000/me

# 7) /me with token -> 200
curl http://localhost:8000/me -H "Authorization: Bearer <4번에서_받은_토큰>"

# 8) notfound -> 404
curl http://localhost:8000/notfound
```

8개가 다 통과하면 “순수 파이썬 로그인 API” 최소 구현 완료입니다.

