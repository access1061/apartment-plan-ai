from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


SUPPORTED = {".png", ".jpg", ".jpeg", ".pdf"}


@dataclass
class RasterPage:
    pixels: Any
    width: int
    height: int
    page: int = 1


def load_pages(path: str | Path, dpi: int = 200) -> list[RasterPage]:
    source = Path(path)
    if source.suffix.lower() not in SUPPORTED:
        raise ValueError(f"지원하지 않는 입력 형식: {source.suffix or '(확장자 없음)'}")
    if not source.is_file():
        raise FileNotFoundError(source)
    if source.suffix.lower() == ".pdf":
        try:
            import pypdfium2 as pdfium
        except ImportError as exc:
            raise RuntimeError("PDF 분석에는 선택 의존성 'pypdfium2'가 필요합니다.") from exc
        doc = pdfium.PdfDocument(str(source))
        pages = []
        for number in range(len(doc)):
            bitmap = doc[number].render(scale=dpi / 72)
            pil = bitmap.to_pil()
            pages.append(RasterPage(pil, pil.width, pil.height, number + 1))
        return pages
    try:
        from PIL import Image
        image = Image.open(source).convert("RGB")
        return [RasterPage(image, image.width, image.height)]
    except ImportError as exc:
        raise RuntimeError("이미지 분석에는 선택 의존성 'Pillow'가 필요합니다.") from exc
