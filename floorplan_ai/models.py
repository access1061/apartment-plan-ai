from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class Confidence:
    value: float
    method: str
    notes: str | None = None

    def __post_init__(self) -> None:
        self.value = max(0.0, min(1.0, float(self.value)))


@dataclass
class Detection:
    id: str
    kind: str
    bbox: list[float]
    confidence: Confidence
    label: str | None = None
    points: list[list[float]] | None = None
    text: str | None = None
    value: float | None = None
    unit: str | None = None


@dataclass
class FloorPlan:
    schema_version: str = "1.0"
    source: dict[str, Any] = field(default_factory=dict)
    image: dict[str, Any] = field(default_factory=dict)
    scale: dict[str, Any] = field(default_factory=dict)
    rooms: list[Detection] = field(default_factory=list)
    walls: list[Detection] = field(default_factory=list)
    doors: list[Detection] = field(default_factory=list)
    windows: list[Detection] = field(default_factory=list)
    measurements: list[Detection] = field(default_factory=list)
    ocr: list[Detection] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
