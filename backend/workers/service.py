from backend.providers.mock import MockImageGenerator, MockVisualReviewer
from backend.runtime import Runtime
from backend.workers.production_worker import ProductionWorker
from backend.workers.runner import Worker


def build_development_worker(runtime: Runtime) -> Worker:
    production=ProductionWorker(runtime,MockImageGenerator(),MockVisualReviewer())
    return Worker(runtime.queue,production.handlers())


def drain(worker: Worker, limit: int=200):
    completed=[]
    for _ in range(limit):
        job=worker.run_one()
        if job is None:
            break
        completed.append(job)
        if job.status.value=="FAILED":
            break
    return completed
