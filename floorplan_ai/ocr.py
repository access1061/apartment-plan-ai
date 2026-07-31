from __future__ import annotations

import re
from typing import Any

from .models import Confidence, Detection

MEASUREMENT = re.compile(r"(?P<num>\d+(?:[.,]\d+)?)\s*(?P<unit>㎡|m2|m²|cm|mm|m)?", re.I)


def extract_ocr(pixels: Any, lang: str = "kor+eng") -> tuple[list[Detection], list[Detection]]:
    try:
        import pytesseract
        from pytesseract import Output
        data = pytesseract.image_to_data(pixels, lang=lang, output_type=Output.DICT)
    except (ImportError, RuntimeError, ValueError):
        return [], []
    texts, measurements = [], []
    for i, raw in enumerate(data.get("text", [])):
        text = str(raw).strip()
        if not text:
            continue
        try:
            conf = max(0.0, min(1.0, float(data["conf"][i]) / 100))
        except (KeyError, ValueError, TypeError):
            conf = 0.2
        bbox = [float(data["left"][i]), float(data["top"][i]), float(data["width"][i]), float(data["height"][i])]
        item = Detection(f"ocr-{len(texts)+1}", "ocr", bbox, Confidence(conf, "tesseract"), text=text)
        texts.append(item)
        match = MEASUREMENT.fullmatch(text.replace(" ", ""))
        if match:
            value = float(match.group("num").replace(",", "."))
            measurements.append(Detection(f"measurement-{len(measurements)+1}", "measurement", bbox,
                Confidence(conf * 0.9, "tesseract+unit-pattern"), text=text, value=value,
                unit=match.group("unit") or "unknown"))
    return texts, measurements
