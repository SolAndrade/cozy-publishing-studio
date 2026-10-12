from dataclasses import dataclass
from enum import StrEnum


class RequirementState(StrEnum):
    READY="READY"
    BLOCKED="BLOCKED"
    HUMAN="HUMAN"


@dataclass(frozen=True,slots=True)
class Requirement:
    name: str
    state: RequirementState
    detail: str


@dataclass(frozen=True,slots=True)
class ReadinessReport:
    requirements: tuple[Requirement,...]

    @property
    def machine_ready(self):
        return all(r.state!=RequirementState.BLOCKED for r in self.requirements)

    @property
    def human_actions(self):
        return tuple(r for r in self.requirements if r.state==RequirementState.HUMAN)


def publishing_readiness(*,interior_locked: bool,cover_locked: bool,metadata_ready: bool,
                         ai_declaration_ready: bool,kdp_draft_connector_ready: bool) -> ReadinessReport:
    def req(name,ok,detail):
        return Requirement(name,RequirementState.READY if ok else RequirementState.BLOCKED,detail)
    return ReadinessReport((
        req("Interior",interior_locked,"Locked interior PDF required"),
        req("Cover",cover_locked,"Locked cover PDF required"),
        req("Metadata",metadata_ready,"Validated metadata required"),
        req("AI declaration",ai_declaration_ready,"AI-content declaration must be prepared"),
        req("KDP draft connector",kdp_draft_connector_ready,"Requires a validated authorized mechanism"),
        Requirement("Final publish",RequirementState.HUMAN,"Final publication approval is always human"),
    ))
