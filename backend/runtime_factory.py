import os

from backend.jobs.postgres_queue import PostgresJobQueue
from backend.jobs.queue import FileJobQueue
from backend.runtime import Runtime
from backend.storage.file_store import FileProjectStore
from backend.storage.postgres import PostgresProjectStore


def runtime_from_env() -> Runtime:
    database_url=os.getenv("DATABASE_URL","").strip()
    env=os.getenv("COZY_ENV","development").strip().lower()
    if database_url:
        return Runtime(
            store=PostgresProjectStore(database_url),
            queue=PostgresJobQueue(database_url),
            cache_projects=False,
        )
    if env=="production":
        raise RuntimeError("Production requires DATABASE_URL for shared project and job persistence")
    return Runtime(
        store=FileProjectStore(os.getenv("COZY_PROJECTS_DIR",".cozy-data/projects")),
        queue=FileJobQueue(os.getenv("COZY_JOBS_DIR",".cozy-data/jobs")),
    )
