from dataclasses import dataclass, field

from backend.domain.project import PublishingProject
from backend.jobs.queue import FileJobQueue, InMemoryJobQueue
from backend.production.controller import ProductionController
from backend.storage.file_store import FileProjectStore


@dataclass(slots=True)
class Runtime:
    projects: dict[str, PublishingProject] = field(default_factory=dict)
    queue: object = field(default_factory=InMemoryJobQueue)
    store: object | None = None
    cache_projects: bool = True

    @property
    def production(self) -> ProductionController:
        return ProductionController(self.queue)

    def add(self, project: PublishingProject) -> PublishingProject:
        self.projects[project.id] = project
        self.persist(project)
        return project

    def get(self, project_id: str) -> PublishingProject:
        if self.cache_projects and project_id in self.projects:
            return self.projects[project_id]
        if self.store is not None:
            try:
                project = self.store.load(project_id)
            except FileNotFoundError:
                pass
            else:
                self.projects[project.id] = project
                return project
        raise KeyError("project_not_found")

    def persist(self, project: PublishingProject) -> None:
        project.touch()
        if self.store is not None:
            self.store.save(project)
