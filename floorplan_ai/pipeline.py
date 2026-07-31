from __future__ import annotations

import json
from pathlib import Path

from .input import load_pages
from .models import Confidence, Detection, FloorPlan
from .ocr import extract_ocr
from .svg import render_svg
from .vision import detect_geometry


def analyze(path: str | Path, output_dir: str | Path, lang: str = "kor+eng", dpi: int = 200) -> list[Path]:
    source = Path(path); out = Path(output_dir); out.mkdir(parents=True, exist_ok=True)
    results = []
    for page in load_pages(source, dpi):
        texts, measurements = extract_ocr(page.pixels, lang)
        rooms, walls, doors, windows = detect_geometry(page.pixels)
        plan = FloorPlan(source={"path": str(source), "format": source.suffix.lower().lstrip(".")}, image={"width": page.width, "height": page.height, "page": page.page}, scale={"unit": "pixel", "confidence": Confidence(.15, "not-calibrated").__dict__}, rooms=rooms, walls=walls, doors=doors, windows=windows, measurements=measurements, ocr=texts)
        if not texts: plan.warnings.append("OCR 결과가 없습니다. Tesseract 설치, 언어 데이터, 이미지 품질을 확인하세요.")
        if not walls: plan.warnings.append("벽 후보가 없습니다. OpenCV 설치 또는 도면 대비를 확인하세요.")
        suffix = f"-page-{page.page}" if len(load_pages(source, dpi)) > 1 else ""
        json_path = out / f"floorplan{suffix}.json"; svg_path = out / f"floorplan{suffix}.svg"
        json_path.write_text(json.dumps(plan.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
        svg_path.write_text(render_svg(plan), encoding="utf-8")
        results.extend([json_path, svg_path])
    return results
