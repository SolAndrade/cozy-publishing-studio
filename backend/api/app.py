from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os

from backend.orchestrator.engine import ProductionEngine

engine = ProductionEngine()


def response(handler, status, payload):
    body = json.dumps(payload, ensure_ascii=False).encode()
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Access-Control-Allow-Origin", os.getenv("COZY_PUBLIC_APP_ORIGIN", "*"))
    handler.send_header("Access-Control-Allow-Headers", "Content-Type")
    handler.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
    handler.end_headers()
    handler.wfile.write(body)


class Handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        response(self, 204, {})

    def do_GET(self):
        if self.path == "/health":
            return response(self, 200, {"status": "ok", "service": "cozy-publishing-studio"})
        return response(self, 404, {"error": "not_found"})

    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0"))
        try:
            data = json.loads(self.rfile.read(length) or b"{}")
        except json.JSONDecodeError:
            return response(self, 400, {"error": "invalid_json"})

        if self.path == "/api/series":
            try:
                concepts = [(item["title"], item.get("subtitle", "")) for item in data["books"]]
                project = engine.create_series(data["name"], concepts)
                return response(self, 201, {
                    "id": project.id,
                    "name": project.series.name,
                    "books": [{"position": b.position, "title": b.title, "state": b.state} for b in project.series.books],
                })
            except (KeyError, ValueError) as exc:
                return response(self, 422, {"error": str(exc)})

        return response(self, 404, {"error": "not_found"})


def run():
    port = int(os.getenv("PORT", "8000"))
    ThreadingHTTPServer(("0.0.0.0", port), Handler).serve_forever()


if __name__ == "__main__":
    run()
