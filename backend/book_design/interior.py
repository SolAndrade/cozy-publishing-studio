from dataclasses import dataclass

from .profiles import BookProfile,COZY_SQUARE


@dataclass(frozen=True,slots=True)
class InteriorPage:
    page_number: int
    scene_number: int|None
    blank: bool


@dataclass(frozen=True,slots=True)
class InteriorPlan:
    profile: BookProfile
    pages: tuple[InteriorPage,...]

    @property
    def page_count(self): return len(self.pages)


def build_interior_plan(profile: BookProfile=COZY_SQUARE) -> InteriorPlan:
    profile.validate()
    pages=[]
    for scene in range(1,profile.scene_count+1):
        pages.append(InteriorPage(len(pages)+1,scene,False))
        if profile.blank_reverse:
            pages.append(InteriorPage(len(pages)+1,None,True))
    return InteriorPlan(profile,tuple(pages))
