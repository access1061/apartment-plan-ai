import json
from pathlib import Path

import pytest

from floorplan_ai.input import load_pages
from floorplan_ai.models import Confidence, Detection, FloorPlan
from floorplan_ai.svg import render_svg


def test_confidence_is_bounded():
    assert Confidence(4, "test").value == 1
    assert Confidence(-1, "test").value == 0


def test_svg_contains_geometry_and_confidence():
    plan = FloorPlan(image={"width": 100, "height": 80}, walls=[Detection("w", "wall", [0, 0, 1, 1], Confidence(.8, "test"), points=[[1, 2], [30, 2]])])
    svg = render_svg(plan)
    assert '<line' in svg and 'data-confidence' not in svg.split('<line', 1)[1].split('/>', 1)[0]


def test_input_rejects_unknown_extension(tmp_path: Path):
    p = tmp_path / "plan.txt"; p.write_text("x")
    with pytest.raises(ValueError): load_pages(p)
