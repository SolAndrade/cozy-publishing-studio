import os
import time

from backend.jobs.queue import FileJobQueue
from backend.runtime import Runtime
from backend.storage.file_store import FileProjectStore
from backend.workers.service import build_worker


def runtime_from_env() -> Runtime:
    return Runtime(
        store=FileProjectStore(os.getenv("COZY_PROJECTS_DIR",".cozy-data/projects")),
        queue=FileJobQueue(os.getenv("COZY_JOBS_DIR",".cozy-data/jobs")),
    )


def run() -> None:
    runtime=runtime_from_env()
    worker=build_worker(runtime)
    poll_seconds=max(float(os.getenv("COZY_WORKER_POLL_SECONDS","1")),0.1)
    while True:
        job=worker.run_one()
        if job is None:
            time.sleep(poll_seconds)


if __name__=="__main__":
    run()
