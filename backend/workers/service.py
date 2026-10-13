import os

from backend.providers.factory import ProviderNotConfigured
from backend.providers.mock import MockImageGenerator, MockVisualReviewer
from backend.runtime import Runtime
from backend.workers.production_worker import ProductionWorker
from backend.workers.runner import Worker


def build_development_worker(runtime: Runtime) -> Worker:
    production=ProductionWorker(runtime,MockImageGenerator(),MockVisualReviewer())
    return Worker(runtime.queue,production.handlers())


def build_worker(runtime: Runtime) -> Worker:
    env=os.getenv("COZY_ENV","development").strip().lower()
    if env!="production":
        return build_development_worker(runtime)
    raise ProviderNotConfigured(
        "Production worker blocked: configure real image and vision provider adapters before processing jobs"
    )


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
