from __future__ import annotations

from pathlib import Path
from typing import Any

from .input import load_pages
from .models import Confidence, Detection, FloorPlan
from .ocr import extract_ocr
from .vision import detect_geometry


def _rooms_from_image(pixels: Any) -> list[Detection]:
    try:
        import cv2
        import numpy as np
    except ImportError:
        return []
    image = np.asarray(pixels.convert("L")) if hasattr(pixels, "convert") else pixels
    _, binary = cv2.threshold(image, 210, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(binary, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    image_area = image.shape[0] * image.shape[1]
    rooms: list[Detection] = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if image_area * .01 < area < image_area * .75:
            polygon = cv2.approxPolyDP(contour, max(1.5, cv2.arcLength(contour, True) * .01), True)
            if 4 <= len(polygon) <= 12:
                x, y, w, h = cv2.boundingRect(contour)
                rooms.append(Detection(f"room-{len(rooms)+1}", "room", [float(x), float(y), float(w), float(h)], Confidence(.35, "opencv-closed-region", "방 후보 영역; 실제 벽 경계와 대조 필요"), points=[[float(p[0][0]), float(p[0][1])] for p in polygon]))
    return rooms


def _line(layer: str, x1: float, y1: float, x2: float, y2: float) -> list[str]:
    return ["0", "LINE", "8", layer, "10", f"{x1:.3f}", "20", f"{y1:.3f}", "30", "0", "11", f"{x2:.3f}", "21", f"{y2:.3f}", "31", "0"]


def _polyline(layer: str, points: list[list[float]], scale: float) -> list[str]:
    result = ["0", "LWPOLYLINE", "8", layer, "90", str(len(points)), "70", "1"]
    for x, y in points:
        result += ["10", f"{x*scale:.3f}", "20", f"{-y*scale:.3f}"]
    return result


def floorplan_to_dxf(plan: FloorPlan, scale_mm_per_pixel: float = 10.0) -> str:
    rows = ["0", "SECTION", "2", "HEADER", "0", "ENDSEC", "0", "SECTION", "2", "ENTITIES"]
    for wall in plan.walls:
        if wall.points and len(wall.points) >= 2:
            (x1, y1), (x2, y2) = wall.points[:2]
            rows += _line("WALLS", x1*scale_mm_per_pixel, -y1*scale_mm_per_pixel, x2*scale_mm_per_pixel, -y2*scale_mm_per_pixel)
    for room in plan.rooms:
        if room.points:
            rows += _polyline("ROOMS", room.points, scale_mm_per_pixel)
    for item, layer in ((plan.doors, "DOORS"), (plan.windows, "WINDOWS")):
        for opening in item:
            x, y, w, h = opening.bbox
            rows += _line(layer, x*scale_mm_per_pixel, -y*scale_mm_per_pixel, (x+w)*scale_mm_per_pixel, -(y+h)*scale_mm_per_pixel)
    for item in plan.measurements:
        x, y, _, _ = item.bbox
        rows += ["0", "TEXT", "8", "ANNOTATIONS", "10", f"{x*scale_mm_per_pixel:.3f}", "20", f"{-y*scale_mm_per_pixel:.3f}", "30", "0", "40", "120", "1", (item.text or "").replace("\\", "")]
    rows += ["0", "ENDSEC", "0", "EOF"]
    return "\n".join(rows) + "\n"


def export_sketchup_reference(source: str | Path, output_dir: str | Path, scale_mm_per_pixel: float = 10.0, lang: str = "kor+eng") -> tuple[Path, Path]:
    source = Path(source); output = Path(output_dir); output.mkdir(parents=True, exist_ok=True)
    page = load_pages(source)[0]
    texts, measurements = extract_ocr(page.pixels, lang)
    _, walls, doors, windows = detect_geometry(page.pixels)
    rooms = _rooms_from_image(page.pixels)
    plan = FloorPlan(source={"path": str(source), "format": source.suffix.lower().lstrip(".")}, image={"width": page.width, "height": page.height}, scale={"unit": "mm", "mm_per_pixel": scale_mm_per_pixel}, rooms=rooms, walls=walls, doors=doors, windows=windows, measurements=measurements, ocr=texts)
    dxf = output / "floorplan-sketchup.dxf"; svg = output / "floorplan-sketchup.svg"
    dxf.write_text(floorplan_to_dxf(plan, scale_mm_per_pixel), encoding="utf-8")
    lines = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {page.width} {page.height}"><rect width="100%" height="100%" fill="white"/>']
    for wall in walls:
        if wall.points and len(wall.points) >= 2:
            a, b = wall.points[:2]; lines.append(f'<line x1="{a[0]}" y1="{a[1]}" x2="{b[0]}" y2="{b[1]}" stroke="#222" stroke-width="2"/>')
    for room in rooms:
        if room.points: lines.append(f'<polygon points="{" ".join(f"{x},{y}" for x,y in room.points)}" fill="none" stroke="#2a9d8f" stroke-width="1"/>')
    lines.append("</svg>"); svg.write_text("\n".join(lines), encoding="utf-8")
    return dxf, svg
