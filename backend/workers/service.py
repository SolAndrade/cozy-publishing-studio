import os

from backend.providers.factory import ProviderFactory, ProviderNotConfigured
from backend.runtime import Runtime
from backend.storage.artifact_factory import artifact_store_from_env
from backend.workers.production_worker import ProductionWorker
from backend.workers.runner import Worker


def _build_configured_worker(runtime: Runtime) -> Worker:
    production = ProductionWorker(
        runtime,
        ProviderFactory.image_generator(),
        ProviderFactory.visual_reviewer(),
        artifact_store_from_env(),
    )
    return Worker(runtime.queue, production.handlers())


def build_development_worker(runtime: Runtime) -> Worker:
    return _build_configured_worker(runtime)


def build_worker(runtime: Runtime) -> Worker:
    env = os.getenv("COZY_ENV", "development").strip().lower()
    if env != "production":
        return build_development_worker(runtime)
    if ProviderFactory.image_provider_name() == "mock" or ProviderFactory.vision_provider_name() == "mock":
        raise ProviderNotConfigured(
            "Production worker blocked: mock image/vision providers are not allowed"
        )
    paid_enabled = os.getenv("COZY_ENABLE_PAID_PROVIDERS", "false").strip().lower()
    if paid_enabled != "true":
        raise ProviderNotConfigured(
            "Production worker blocked: paid providers require explicit COZY_ENABLE_PAID_PROVIDERS=true"
        )
    return _build_configured_worker(runtime)


def drain(worker: Worker, limit: int = 200):
    completed = []
    for _ in range(limit):
        job = worker.run_one()
        if job is None:
            break
        completed.append(job)
        if job.status.value == "FAILED":
            break
    return completed
