from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True,slots=True)
class PDFPreflight:
    passed: bool
    page_count: int
    width_pt: float
    height_pt: float
    issues: tuple[str,...]


def preflight_interior(path: str, expected_pages=80, expected_size_pt=(612.0,612.0)) -> PDFPreflight:
    try:
        import fitz
    except ImportError as exc:
        raise RuntimeError("PyMuPDF is required for PDF preflight") from exc
    doc=fitz.open(Path(path))
    issues=[]
    if doc.page_count!=expected_pages: issues.append(f"Expected {expected_pages} pages")
    first=doc[0].rect
    if abs(first.width-expected_size_pt[0])>.5 or abs(first.height-expected_size_pt[1])>.5:
        issues.append("Unexpected trim size")
    for i,page in enumerate(doc):
        if abs(page.rect.width-first.width)>.1 or abs(page.rect.height-first.height)>.1:
            issues.append(f"Inconsistent page size at page {i+1}"); break
    result=PDFPreflight(not issues,doc.page_count,first.width,first.height,tuple(issues))
    doc.close()
    return result
