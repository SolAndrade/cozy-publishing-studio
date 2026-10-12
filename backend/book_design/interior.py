from dataclasses import dataclass


@dataclass(frozen=True,slots=True)
class InteriorSpec:
    trim_width_in: float=8.5
    trim_height_in: float=8.5
    art_width_in: float=7.5
    art_height_in: float=7.5
    scene_count: int=40
    blank_reverse: bool=True
    bleed: bool=False


@dataclass(frozen=True,slots=True)
class InteriorPage:
    page_number: int
    scene_number: int|None
    blank: bool


@dataclass(frozen=True,slots=True)
class InteriorPlan:
    spec: InteriorSpec
    pages: tuple[InteriorPage,...]

    @property
    def page_count(self): return len(self.pages)


def build_interior_plan(spec: InteriorSpec=InteriorSpec()) -> InteriorPlan:
    if spec.scene_count!=40:
        raise ValueError("Current coloring-book template requires exactly 40 scenes")
    pages=[]
    for scene in range(1,spec.scene_count+1):
        pages.append(InteriorPage(len(pages)+1,scene,False))
        if spec.blank_reverse:
            pages.append(InteriorPage(len(pages)+1,None,True))
    return InteriorPlan(spec,tuple(pages))
