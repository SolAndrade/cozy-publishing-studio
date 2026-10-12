from dataclasses import dataclass


@dataclass(frozen=True,slots=True)
class CoverSpec:
    trim_width_in: float
    trim_height_in: float
    page_count: int
    spine_width_in: float
    bleed_in: float=0.125
    barcode_width_in: float=2.0
    barcode_height_in: float=1.2


@dataclass(frozen=True,slots=True)
class CoverPlan:
    spec: CoverSpec
    full_width_in: float
    full_height_in: float
    front_x_in: float
    barcode_reserved: bool=True


def build_cover_plan(spec: CoverSpec) -> CoverPlan:
    if spec.page_count<=0 or spec.spine_width_in<0: raise ValueError("Invalid cover dimensions")
    full_width=2*spec.trim_width_in+spec.spine_width_in+2*spec.bleed_in
    full_height=spec.trim_height_in+2*spec.bleed_in
    front_x=spec.bleed_in+spec.trim_width_in+spec.spine_width_in
    return CoverPlan(spec,full_width,full_height,front_x)
