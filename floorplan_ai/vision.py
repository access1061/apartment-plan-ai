from __future__ import annotations

from typing import Any

from .models import Confidence, Detection


def _gray(pixels: Any) -> Any:
    import numpy as np
    if hasattr(pixels, "convert"):
        pixels = np.asarray(pixels.convert("L"))
    elif len(getattr(pixels, "shape", ())) == 3:
        pixels = pixels.mean(axis=2).astype("uint8")
    return pixels


def detect_geometry(pixels: Any) -> tuple[list[Detection], list[Detection], list[Detection], list[Detection]]:
    """Return rooms, walls, doors, windows using conservative OpenCV heuristics."""
    try:
        import cv2
        import numpy as np
    except ImportError:
        return [], [], [], []
    gray = _gray(pixels)
    edges = cv2.Canny(gray, 50, 150)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=max(20, min(gray.shape)//12), minLineLength=max(30, min(gray.shape)//10), maxLineGap=8)
    walls, doors, windows = [], [], []
    if lines is not None:
        for i, line in enumerate(lines[:, 0, :], 1):
            x1, y1, x2, y2 = map(int, line)
            length = ((x2-x1)**2 + (y2-y1)**2) ** 0.5
            bbox = [float(min(x1,x2)), float(min(y1,y2)), float(abs(x2-x1) or 1), float(abs(y2-y1) or 1)]
            item = Detection(f"wall-{i}", "wall", bbox, Confidence(min(.92, .45 + length / max(gray.shape) * .4), "opencv-hough"), points=[[x1,y1],[x2,y2]])
            walls.append(item)
    # Openings are intentionally conservative: short gaps/contours are candidates, not claims.
    contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    for i, contour in enumerate(contours, 1):
        x, y, w, h = cv2.boundingRect(contour)
        if 8 <= w <= max(80, gray.shape[1]//5) and 8 <= h <= max(80, gray.shape[0]//5):
            ratio = w / max(h, 1)
            target = windows if ratio > 2.2 or ratio < .45 else doors
            kind = "window" if target is windows else "door"
            target.append(Detection(f"{kind}-{len(target)+1}", kind, [float(x),float(y),float(w),float(h)], Confidence(.3, "opencv-contour-candidate", "후보 검출; 수동 확인 필요")))
    return [], walls, doors, windows
