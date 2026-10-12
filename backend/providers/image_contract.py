from dataclasses import dataclass


@dataclass(frozen=True,slots=True)
class GenerationRequest:
    project_id: str
    book_position: int
    scene_number: int
    scene_title: str
    locked_brief: str
    mode: str="GENERATE"
    defect_reason: str=""


def build_coloring_prompt(request: GenerationRequest) -> str:
    return f"""Create one original adult coloring-book illustration.
Book brief: {request.locked_brief}
Scene {request.scene_number:02}: {request.scene_title}
Mode: {request.mode}
Material defect to correct, if any: {request.defect_reason or "none"}
Requirements: clean black line art on pure white; no intentional grayscale, shadows,
hatching or tonal rendering; no readable text, logos or brands; large and medium
colorable areas dominate; structurally plausible; preserve the locked book identity."""
