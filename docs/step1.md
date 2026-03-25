# Step 1 — 순수 파이썬 HTTP 서버 만들기

> 원본 메모: `docs/step1.txt`  
> 이 파일은 GitHub에서 읽기 좋게 Markdown으로 정리한 버전입니다.

## 오늘의 목표

- 프레임워크 없이 `localhost:8000`에서 HTTP 요청을 받고
- `GET /health`에 JSON으로 응답하며
- 없는 경로에는 `404 Not Found`를 내려주는 **최소 서버 뼈대**를 만든다.

---

## 핵심 개념 정리

### localhost / 127.0.0.1

- **`localhost`**: “내 컴퓨터 자신”을 의미하는 호스트 이름
- **`127.0.0.1`**: 루프백(Loopback) IP. 네트워크로 나가지 않고 자기 자신에게 돌아오는 주소

즉 `http://localhost:8000`은 “내 컴퓨터의 8000번 포트로 요청한다”는 뜻.

---

## 서버를 구성하는 2개의 부품

### 1) `HTTPServer`

- **실제 서버 엔진**
- “어디서 받을지(주소/포트)”와 “누가 처리할지(Handler 클래스)”를 연결한다

예:

```python
HTTPServer(("localhost", 8000), RequestHandler)
```

- `serve_forever()`를 호출하면 서버는 요청을 기다리면서 계속 돈다.

### 2) `RequestHandler(BaseHTTPRequestHandler)`

- **요청 1개를 처리하는 담당자**
- 클라이언트가 보낸 HTTP 메서드에 따라 아래가 호출된다:
  - `do_GET()` (GET 요청)
  - `do_POST()` (POST 요청)

핸들러는 요청 정보를 읽고(메서드/경로/헤더/바디), 응답을 만든다.

---

## HTTP 요청을 구분하는 기준: 메서드 + 경로

핵심:

- **메서드**: `GET`, `POST`
- **경로(path)**: `/health`, `/signup`, `/login` …

핸들러에서 자주 보는 값:

- `self.command`: `"GET"`, `"POST"`
- `self.path`: `"/health"` 같은 경로 문자열

### (미리 알아두기) 쿼리스트링

`self.path`에는 쿼리스트링이 붙을 수 있다.

- 예: `/login?next=/home`

라우터를 만들 때는 보통 `urlparse`로 **경로만** 분리해서 매칭한다.

---

## HTTP 응답은 3요소: status / header / body

### status (상태 코드)

- `200`: 성공
- `404`: Not Found (없는 경로)
- (로그인 구현 시 추가로) `400`, `401`, `409` 등을 많이 쓰게 됨

### header (헤더)

클라이언트에게 “바디 형식”을 알려줌.

- JSON을 내려주려면: `Content-Type: application/json`

### body (바디)

실제 데이터.

중요 포인트:

- `wfile.write()`는 문자열이 아니라 **bytes**를 받는다
- 그래서 보통 이렇게 보냄:

```python
json.dumps(data).encode()
```

---

## Handler에서 자주 쓰는 메서드(암기 레벨)

- `send_response(status_code)` : 상태 코드 설정
- `send_header(key, value)` : 헤더 추가
- `end_headers()` : 헤더 전송 끝(이제 body 쓸 수 있음)
- `wfile.write(bytes_body)` : 바디 전송

---

## Step 1에서 구현하는 최소 엔드포인트

- `GET /health`
  - `200` + `{"status":"ok"}`
- 그 외 GET 경로
  - `404` + `{"success": false, "message": "Not Found"}`
- `POST`는 아직 학습용 placeholder
  - `200` + `{"message":"hello"}`

---

## 테스트(curl)

서버 실행:

```bash
python server.py
```

다른 터미널에서:

```bash
curl http://localhost:8000/health
curl http://localhost:8000/anything
curl -X POST http://localhost:8000/test
```

기대:

- `/health` → 성공 JSON
- 없는 경로 → 404 JSON
- POST → placeholder JSON

---


