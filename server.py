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
    server = HTTPServer(("localhost", 8004), RequestHandler)
    print("Server running on http://localhost:8004")
    server.serve_forever()
