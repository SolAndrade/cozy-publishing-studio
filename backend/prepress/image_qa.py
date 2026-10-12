from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class TechnicalImageReport:
    path: str
    width: int
    height: int
    mode: str
    min_value: int
    max_value: int
    gray_fraction: float
    issues: tuple[str, ...]

    @property
    def passed(self) -> bool:
        return not self.issues


def inspect_line_art(path: str, *, expected_size: tuple[int,int]=(2400,2400),
                     max_gray_fraction: float=0.08) -> TechnicalImageReport:
    try:
        from PIL import Image
    except ImportError as exc:
        raise RuntimeError("Pillow is required for image preflight") from exc
    source=Path(path)
    with Image.open(source) as image:
        image.load()
        gray=image.convert("L")
        values=list(gray.getdata())
        width,height=image.size
        gray_pixels=sum(1 for v in values if 8 < v < 247)
        fraction=gray_pixels/max(1,len(values))
        issues=[]
        if (width,height)!=expected_size:
            issues.append(f"Expected {expected_size[0]}x{expected_size[1]} px")
        if fraction>max_gray_fraction:
            issues.append("Excessive mid-tone pixels for clean line art")
        if max(values)<245:
            issues.append("Background does not reach near-white")
        return TechnicalImageReport(str(source),width,height,image.mode,min(values),max(values),fraction,tuple(issues))
