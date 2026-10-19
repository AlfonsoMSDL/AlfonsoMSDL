#!/usr/bin/env python3
"""
radar.py - dibuja el radar de habilidades del README como SVG. Solo biblioteca estándar.

Uso:
    python scripts/radar.py --data assets/skills.json -o assets/radar

Escribe assets/radar-dark.svg y assets/radar-light.svg; el README alterna entre
los dos con <picture> + prefers-color-scheme.

Forma de skills.json (valores de 0 a 100):
    { "axes": [ {"label": "Java & Spring Boot", "value": 80}, ... ] }
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from xml.sax.saxutils import escape

WIDTH, HEIGHT = 700, 480
CX, CY, RADIUS = WIDTH / 2, HEIGHT / 2 + 4, 150
RINGS = (20, 40, 60, 80, 100)
FONT = "ui-monospace, SFMono-Regular, Menlo, Consolas, 'DejaVu Sans Mono', monospace"

THEMES = {
    "dark": {
        "grid": "#30363d",
        "label": "#e6edf3",
        "value": "#8b949e",
        "from": "#f89820",
        "to": "#6db33f",
    },
    "light": {
        "grid": "#d0d7de",
        "label": "#1f2328",
        "value": "#57606a",
        "from": "#e07b00",
        "to": "#3f8a1f",
    },
}


def load_axes(path: Path) -> list[tuple[str, float]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return [(a["label"], max(0.0, min(100.0, float(a["value"])))) for a in data["axes"]]


def point(index: int, total: int, radius: float) -> tuple[float, float]:
    """Punto del eje `index` a `radius` del centro; el primer eje apunta hacia arriba."""
    angle = -math.pi / 2 + 2 * math.pi * index / total
    return CX + radius * math.cos(angle), CY + radius * math.sin(angle)


def polygon(points: list[tuple[float, float]]) -> str:
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in points)


def anchor_for(x: float) -> str:
    if abs(x - CX) < 8:
        return "middle"
    return "start" if x > CX else "end"


def render(axes: list[tuple[str, float]], theme: dict[str, str]) -> str:
    n = len(axes)
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" '
        f'viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-labelledby="title">',
        "  <title id=\"title\">Radar de habilidades: "
        + escape(", ".join(f"{label} {value:g}" for label, value in axes))
        + "</title>",
        "  <defs>",
        f'    <linearGradient id="brand" gradientUnits="userSpaceOnUse" x1="{CX - RADIUS}" y1="0" x2="{CX + RADIUS}" y2="0">',
        f'      <stop offset="0" stop-color="{theme["from"]}"/>',
        f'      <stop offset="1" stop-color="{theme["to"]}"/>',
        "    </linearGradient>",
        "  </defs>",
    ]

    for ring in RINGS:
        pts = [point(i, n, RADIUS * ring / 100) for i in range(n)]
        out.append(f'  <polygon points="{polygon(pts)}" fill="none" stroke="{theme["grid"]}" stroke-width="1"/>')
    for i in range(n):
        x, y = point(i, n, RADIUS)
        out.append(f'  <line x1="{CX}" y1="{CY}" x2="{x:.1f}" y2="{y:.1f}" stroke="{theme["grid"]}" stroke-width="1"/>')

    shape = [point(i, n, RADIUS * value / 100) for i, (_, value) in enumerate(axes)]
    out.append(
        f'  <polygon points="{polygon(shape)}" fill="url(#brand)" fill-opacity=".28" '
        f'stroke="url(#brand)" stroke-width="2.5" stroke-linejoin="round"/>'
    )
    for x, y in shape:
        out.append(f'  <circle cx="{x:.1f}" cy="{y:.1f}" r="4.5" fill="url(#brand)"/>')

    out.append(f'  <g font-family="{FONT}">')
    for i, (label, value) in enumerate(axes):
        x, y = point(i, n, RADIUS + 26)
        anchor = anchor_for(x)
        out.append(
            f'    <text x="{x:.1f}" y="{y - 3:.1f}" text-anchor="{anchor}" fill="{theme["label"]}" '
            f'font-size="15" font-weight="700">{escape(label)}</text>'
        )
        out.append(
            f'    <text x="{x:.1f}" y="{y + 15:.1f}" text-anchor="{anchor}" fill="{theme["value"]}" '
            f'font-size="13">{value:g} / 100</text>'
        )
    out.append("  </g>")
    out.append("</svg>")
    return "\n".join(out) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--data", default="assets/skills.json", type=Path, help="JSON con los ejes y valores")
    parser.add_argument("-o", "--out", default="assets/radar", help="prefijo de salida (-dark.svg / -light.svg)")
    args = parser.parse_args()

    axes = load_axes(args.data)
    if len(axes) < 3:
        raise SystemExit("Se necesitan al menos 3 ejes")
    for name, theme in THEMES.items():
        target = Path(f"{args.out}-{name}.svg")
        target.write_text(render(axes, theme), encoding="utf-8")
        print(f"escrito {target}")


if __name__ == "__main__":
    main()
