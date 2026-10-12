from dataclasses import dataclass, field

from backend.domain.project import PublishingProject
from backend.jobs.queue import InMemoryJobQueue
from backend.production.controller import ProductionController


@dataclass(slots=True)
class Runtime:
    projects: dict[str, PublishingProject] = field(default_factory=dict)
    queue: InMemoryJobQueue = field(default_factory=InMemoryJobQueue)

    @property
    def production(self) -> ProductionController:
        return ProductionController(self.queue)

    def add(self, project: PublishingProject) -> PublishingProject:
        self.projects[project.id] = project
        return project

    def get(self, project_id: str) -> PublishingProject:
        try:
            return self.projects[project_id]
        except KeyError:
            raise KeyError("project_not_found")
