from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ImageSpec:
    width_px: int
    height_px: int
    target_width_in: float
    target_height_in: float
    min_ppi: float = 300.0

    @property
    def effective_ppi(self) -> tuple[float, float]:
        return self.width_px / self.target_width_in, self.height_px / self.target_height_in


def validate_image_spec(spec: ImageSpec) -> list[str]:
    issues: list[str] = []
    if spec.width_px <= 0 or spec.height_px <= 0:
        issues.append("Image dimensions must be positive")
        return issues
    if spec.target_width_in <= 0 or spec.target_height_in <= 0:
        issues.append("Target dimensions must be positive")
        return issues
    x_ppi, y_ppi = spec.effective_ppi
    if min(x_ppi, y_ppi) < spec.min_ppi:
        issues.append(f"Effective resolution below {spec.min_ppi:g} ppi")
    if abs((spec.width_px / spec.height_px) - (spec.target_width_in / spec.target_height_in)) > 0.001:
        issues.append("Aspect ratio mismatch")
    return issues
