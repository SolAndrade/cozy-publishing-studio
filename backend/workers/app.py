import os
import time

from backend.runtime_factory import runtime_from_env
from backend.workers.service import build_worker


def recover_stale_jobs(runtime, stale_seconds: int) -> None:
    env = os.getenv("COZY_ENV", "development").strip().lower()
    if env == "production":
        block = getattr(runtime.queue, "block_stale_running", None)
        if block is not None:
            block(stale_seconds)
        return
    recover = getattr(runtime.queue, "recover_stale_running", None)
    if recover is not None:
        recover(stale_seconds)


def run() -> None:
    runtime = runtime_from_env()
    worker = build_worker(runtime)
    poll_seconds = max(float(os.getenv("COZY_WORKER_POLL_SECONDS", "1")), 0.1)
    stale_seconds = max(int(os.getenv("COZY_JOB_STALE_SECONDS", "900")), 60)
    recover_stale_jobs(runtime, stale_seconds)
    while True:
        job = worker.run_one()
        if job is None:
            time.sleep(poll_seconds)


if __name__ == "__main__":
    run()
