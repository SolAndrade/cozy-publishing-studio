from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from urllib.parse import urlparse

from backend.orchestrator.engine import ProductionEngine
from backend.runtime import Runtime
from backend.api.status import system_status
from backend.runtime_factory import runtime_from_env
from backend.security.api_auth import authorize_header

engine = ProductionEngine()
runtime = runtime_from_env()


def response(handler, status, payload):
    body=json.dumps(payload,ensure_ascii=False).encode()
    handler.send_response(status)
    handler.send_header("Content-Type","application/json; charset=utf-8")
    handler.send_header("Access-Control-Allow-Origin",os.getenv("COZY_PUBLIC_APP_ORIGIN","*"))
    handler.send_header("Access-Control-Allow-Headers","Content-Type")
    handler.send_header("Access-Control-Allow-Methods","GET, POST, OPTIONS")
    handler.end_headers()
    handler.wfile.write(body)


def series_concepts(payload):
    return [
        (
            item["title"],
            item.get("subtitle", ""),
            item.get("locked_brief", ""),
        )
        for item in payload["books"]
    ]


def book_payload(book):
    return {
        "position":book.position,"title":book.title,"subtitle":book.subtitle,
        "locked_brief":book.locked_brief,
        "state":book.state,"progress":runtime.production.progress(book),
        "scenes":[{"number":s.number,"title":s.title,"state":s.state,"generations":s.generations} for s in book.scenes],
    }


class Handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self): response(self,204,{})

    def authorized(self):
        if authorize_header(self.headers.get("Authorization")):
            return True
        response(self,401,{"error":"unauthorized"})
        return False

    def do_GET(self):
        path=urlparse(self.path).path
        if path=="/health":
            return response(self,200,{"status":"ok","service":"cozy-publishing-studio"})
        if path=="/api/status":
            if not self.authorized(): return
            return response(self,200,system_status())
        parts=path.strip("/").split("/")
        if len(parts)==3 and parts[:2]==["api","projects"]:
            if not self.authorized(): return
            try:
                project=runtime.get(parts[2])
                return response(self,200,{"id":project.id,"name":project.series.name,"books":[book_payload(b) for b in project.series.books]})
            except KeyError:
                return response(self,404,{"error":"project_not_found"})
        return response(self,404,{"error":"not_found"})

    def do_POST(self):
        path=urlparse(self.path).path
        if path.startswith("/api/") and not self.authorized(): return
        length=int(self.headers.get("Content-Length","0"))
        try: data=json.loads(self.rfile.read(length) or b"{}")
        except json.JSONDecodeError: return response(self,400,{"error":"invalid_json"})

        if path=="/api/series":
            try:
                concepts=series_concepts(data)
                project=runtime.add(engine.create_series(data["name"],concepts))
                return response(self,201,{"id":project.id,"name":project.series.name,"books":[book_payload(b) for b in project.series.books]})
            except (KeyError,ValueError) as exc: return response(self,422,{"error":str(exc)})

        parts=path.strip("/").split("/")
        if len(parts)==6 and parts[:2]==["api","projects"] and parts[3]=="books":
            project_id,position,action=parts[2],parts[4],parts[5]
            try:
                project=runtime.get(project_id)
                book=next(b for b in project.series.books if b.position==int(position))
                if action=="manifest":
                    engine.install_manifest(book,data["scenes"])
                    runtime.persist(project)
                    return response(self,200,book_payload(book))
                if action=="brief":
                    engine.set_locked_brief(book,data["locked_brief"])
                    runtime.persist(project)
                    return response(self,200,book_payload(book))
                if action=="start":
                    engine.start_generation(book)
                    job=runtime.production.enqueue_next_scene(project.id,book)
                    runtime.persist(project)
                    return response(self,202,{"book":book_payload(book),"job_id":job.id if job else None})
            except (KeyError,ValueError,StopIteration) as exc:
                return response(self,422,{"error":str(exc)})
        return response(self,404,{"error":"not_found"})


def run():
    port=int(os.getenv("PORT","8000"))
    ThreadingHTTPServer(("0.0.0.0",port),Handler).serve_forever()

if __name__=="__main__": run()
