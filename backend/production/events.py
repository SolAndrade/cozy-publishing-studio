from dataclasses import dataclass,field
from datetime import datetime,timezone


@dataclass(frozen=True,slots=True)
class ProductionEvent:
    project_id: str
    book_position: int
    event: str
    scene_number: int|None=None
    detail: str=""
    created_at: str=field(default_factory=lambda:datetime.now(timezone.utc).isoformat())


class EventLog:
    def __init__(self):
        self._events=[]

    def append(self,event: ProductionEvent):
        self._events.append(event)
        return event

    def recent(self,project_id: str,limit: int=50):
        return [e for e in self._events if e.project_id==project_id][-limit:]
