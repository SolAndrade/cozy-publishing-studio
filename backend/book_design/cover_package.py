from dataclasses import dataclass

from .cover import CoverPlan,CoverSpec,build_cover_plan
from .profiles import BookProfile


@dataclass(frozen=True,slots=True)
class CoverContent:
    title: str
    subtitle: str
    back_heading: str
    back_copy: str
    hero_scene: int
    thumbnail_scenes: tuple[int,int,int]


@dataclass(frozen=True,slots=True)
class CoverBuildRequest:
    profile: BookProfile
    page_count: int
    spine_width_in: float
    content: CoverContent


def prepare_cover(request: CoverBuildRequest) -> CoverPlan:
    request.profile.validate()
    if request.page_count<=0: raise ValueError("page_count must be positive")
    if request.content.hero_scene in request.content.thumbnail_scenes:
        raise ValueError("Hero scene should not be reused as a back-cover thumbnail")
    if len(set(request.content.thumbnail_scenes))!=3:
        raise ValueError("Back-cover thumbnails must be three distinct scenes")
    if any(n<1 or n>request.profile.scene_count for n in (request.content.hero_scene,*request.content.thumbnail_scenes)):
        raise ValueError("Cover scene reference outside book manifest")
    return build_cover_plan(CoverSpec(
        trim_width_in=request.profile.trim_width_in,
        trim_height_in=request.profile.trim_height_in,
        page_count=request.page_count,
        spine_width_in=request.spine_width_in,
    ))
