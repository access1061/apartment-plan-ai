from __future__ import annotations

from html import escape
from .models import FloorPlan


def render_svg(plan: FloorPlan) -> str:
    width = int(plan.image.get("width", 1000)); height = int(plan.image.get("height", 1000))
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">', '<rect width="100%" height="100%" fill="white"/>']
    for wall in plan.walls:
        if wall.points and len(wall.points) >= 2:
            a, b = wall.points[:2]; out.append(f'<line x1="{a[0]}" y1="{a[1]}" x2="{b[0]}" y2="{b[1]}" stroke="#222" stroke-width="4"/>')
    for kind, color in ((plan.rooms, "#4b9"), (plan.doors, "#e76f51"), (plan.windows, "#268bd2")):
        for item in kind:
            x,y,w,h = item.bbox; out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="none" stroke="{color}" stroke-width="2" data-confidence="{item.confidence.value:.2f}"/>')
    out.append('</svg>'); return "\n".join(out)
