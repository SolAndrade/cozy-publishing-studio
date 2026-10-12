from dataclasses import dataclass

from backend.book_design.interior import build_interior_plan
from backend.book_design.interior_pdf import build_interior_pdf
from backend.book_design.preflight import preflight_interior
from backend.book_design.profiles import BookProfile,COZY_SQUARE


@dataclass(frozen=True,slots=True)
class InteriorBuildResult:
    path: str
    page_count: int
    passed: bool
    issues: tuple[str,...]


def assemble_interior(scene_paths: dict[int,str], output_path: str, profile: BookProfile=COZY_SQUARE):
    plan=build_interior_plan(profile)
    path=build_interior_pdf(plan,scene_paths,output_path)
    check=preflight_interior(path,plan.page_count,(profile.trim_width_in*72,profile.trim_height_in*72))
    return InteriorBuildResult(path,check.page_count,check.passed,check.issues)
