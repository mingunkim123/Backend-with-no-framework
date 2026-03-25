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
    
    