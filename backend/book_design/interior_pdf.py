from pathlib import Path

from .interior import InteriorPlan


def build_interior_pdf(plan: InteriorPlan, scene_paths: dict[int,str], output_path: str) -> str:
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.utils import ImageReader
    except ImportError as exc:
        raise RuntimeError("ReportLab is required to build interiors") from exc

    missing=[p.scene_number for p in plan.pages if p.scene_number and p.scene_number not in scene_paths]
    if missing: raise ValueError(f"Missing scene masters: {missing}")

    width=plan.spec.trim_width_in*72
    height=plan.spec.trim_height_in*72
    art_w=plan.spec.art_width_in*72
    art_h=plan.spec.art_height_in*72
    x=(width-art_w)/2; y=(height-art_h)/2
    target=Path(output_path); target.parent.mkdir(parents=True,exist_ok=True)
    pdf=canvas.Canvas(str(target),pagesize=(width,height),pageCompression=1)
    for page in plan.pages:
        if not page.blank:
            pdf.drawImage(ImageReader(scene_paths[page.scene_number]),x,y,width=art_w,height=art_h,preserveAspectRatio=True,anchor="c",mask="auto")
        pdf.showPage()
    pdf.save()
    return str(target)
