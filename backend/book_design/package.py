from dataclasses import dataclass

from backend.book_design.interior import InteriorSpec,build_interior_plan
from backend.book_design.interior_pdf import build_interior_pdf
from backend.book_design.preflight import preflight_interior


@dataclass(frozen=True,slots=True)
class InteriorBuildResult:
    path: str
    page_count: int
    passed: bool
    issues: tuple[str,...]


def assemble_interior(scene_paths: dict[int,str], output_path: str, spec: InteriorSpec=InteriorSpec()):
    plan=build_interior_plan(spec)
    path=build_interior_pdf(plan,scene_paths,output_path)
    check=preflight_interior(path,plan.page_count,(spec.trim_width_in*72,spec.trim_height_in*72))
    return InteriorBuildResult(path,check.page_count,check.passed,check.issues)
