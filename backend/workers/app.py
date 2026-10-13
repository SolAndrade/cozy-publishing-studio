import os
import time

from backend.runtime_factory import runtime_from_env
from backend.workers.service import build_worker


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
