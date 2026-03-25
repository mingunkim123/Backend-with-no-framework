# Step 2 — JSON 요청 바디를 Python `dict`로 파싱하기

> 관련 코드: `utils.py`의 `parse_request_body()`

이번 단계의 목표는 **클라이언트가 JSON으로 보낸 요청 바디(body)를 읽어서**, Python에서 다루기 쉬운 **`dict`로 변환**하는 것입니다.

---

## 왜 이걸 직접 만들어야 하나?

Flask/Django/FastAPI 같은 프레임워크에서는 보통 `request.json` 같은 형태로 이미 파싱된 값을 줍니다.  
하지만 프레임워크 없이 `http.server`를 쓰면,

- 요청 바디는 기본적으로 **바이트(bytes)** 스트림으로 들어오고
- 우리가 직접 “몇 바이트를 읽을지”와 “JSON으로 파싱할지”를 결정해야 합니다.

이 단계를 해보면 프레임워크가 내부에서 해주는 작업이 무엇인지 감이 잡힙니다.

---

## HTTP 요청 바디를 읽는 핵심 흐름

JSON 파싱은 다음 파이프라인으로 이해하면 깔끔합니다.

1. **헤더에서 Content-Length 확인**  
2. 그 길이만큼 **바이트를 읽기 (`rfile.read`)**  
3. 읽은 바이트를 **JSON으로 파싱 (`json.loads`)**  
4. 결과를 **Python `dict`로 사용**

---

## 1) Content-Length가 왜 필요해?

`BaseHTTPRequestHandler`에서 POST 바디는 `handler.rfile`이라는 **스트림**으로 제공됩니다.

스트림은 “언제 끝날지”를 자동으로 알 수 없기 때문에,
서버는 보통 헤더의 `Content-Length`를 보고 **딱 그만큼만** 읽습니다.

- `Content-Length: 42` → 바디가 42바이트라는 의미

만약 Content-Length가 없거나 0이라면(혹은 바디가 없다면) 이 프로젝트에서는 에러로 처리합니다.

> 참고: `Transfer-Encoding: chunked` 같은 방식도 있지만(길이를 미리 모름), 지금은 학습 단계를 단순하게 가져가기 위해 다루지 않습니다.

---

## 2) JSON 파싱은 `json.loads()`로 한다

Python 표준 라이브러리 `json`의 `json.loads()`는 다음 입력을 받을 수 있습니다.

- `str` (문자열 JSON)
- `bytes` / `bytearray` (바이트 JSON)

즉, 우리가 `rfile.read()`로 읽은 바이트를 그대로 `json.loads(body_bytes)`에 넣어도 됩니다.

### 파싱 실패는 어떻게 잡나?

JSON이 깨져 있으면 `json.JSONDecodeError`가 발생합니다.  
이건 클라이언트의 잘못된 요청이므로 보통 서버는 **400 Bad Request**로 응답합니다.

우리는 `parse_request_body()` 안에서 `JSONDecodeError`를 잡아서 `ValueError("Invalid JSON")`로 바꿔 던지고,
핸들러에서 그 예외를 받아 400을 내려주는 방식으로 처리할 예정입니다.

---

## 3) Step 2에서 만들 함수 2개(역할)

### `parse_request_body(handler) -> dict`

- 입력: `handler`(= BaseHTTPRequestHandler 인스턴스)
- 출력: 파싱된 Python `dict`
- 실패:
  - 바디가 비었으면 `ValueError("Empty request body")`
  - JSON이 깨졌으면 `ValueError("Invalid JSON")`

### `send_json_response(handler, status_code, data)`

이번 요청의 초점은 “요청 파싱”이지만, 실제로는 응답도 반복이 많아서 같이 유틸로 묶습니다.

---

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

## 스스로 점검 체크리스트

- `Content-Length`가 없거나 0이면, 서버는 **바디를 읽지 않고** 에러로 처리한다
- `rfile.read(n)`은 **bytes**를 돌려준다
- `json.loads(bytes)`로 **dict**를 얻는다
- JSON 파싱 실패는 400으로 이어질 수 있도록 예외로 올린다

