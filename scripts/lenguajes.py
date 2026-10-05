"""Genera assets/lenguajes.svg sumando los lenguajes de TODOS los repos (públicos y privados).

Uso:  python scripts/lenguajes.py   (requiere `gh` autenticado)
"""
import json
import math
import subprocess
from pathlib import Path

USER = "Saler123"
COLORS = {
    "TypeScript": "#3178C6", "Blade": "#F7523F", "PHP": "#777BB4", "HTML": "#E34C26",
    "CSS": "#663399", "JavaScript": "#F1E05A", "Python": "#3572A5", "C++": "#F34B7D",
    "C": "#555555", "Java": "#B07219", "Vue": "#41B883", "Shell": "#89E051",
}
TOP = 6


def gh(*args):
    return json.loads(subprocess.check_output(["gh", *args], text=True, encoding="utf-8"))


totals = {}
for repo in gh("repo", "list", USER, "--limit", "200", "--json", "name"):
    for lang, size in gh("api", f"repos/{USER}/{repo['name']}/languages").items():
        totals[lang] = totals.get(lang, 0) + size

items = sorted(totals.items(), key=lambda kv: kv[1], reverse=True)
if len(items) > TOP:
    items = items[:TOP - 1] + [("Otros", sum(v for _, v in items[TOP - 1:]))]
total = sum(v for _, v in items)

cx, cy, r, w = 150, 150, 95, 42
circ = 2 * math.pi * r
arcs, legend, offset = [], [], 0.0
for i, (lang, size) in enumerate(items):
    pct = size / total
    color = COLORS.get(lang, "#8B949E")
    dash = pct * circ
    arcs.append(
        f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{color}" stroke-width="{w}" '
        f'stroke-dasharray="{dash:.2f} {circ - dash:.2f}" stroke-dashoffset="{-offset:.2f}" '
        f'transform="rotate(-90 {cx} {cy})" class="arc" style="animation-delay:{i * 0.15:.2f}s"/>'
    )
    offset += dash
    y = 88 + i * 34
    legend.append(
        f'<rect x="330" y="{y - 12}" width="14" height="14" rx="3" fill="{color}"/>'
        f'<text x="354" y="{y}" class="lang">{lang}</text>'
        f'<text x="560" y="{y}" class="pct">{pct * 100:.1f}%</text>'
        f'<rect x="354" y="{y + 7}" width="206" height="4" rx="2" fill="#1F2937"/>'
        f'<rect x="354" y="{y + 7}" width="{max(pct * 206, 2):.1f}" height="4" rx="2" fill="{color}"/>'
    )

svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 300" width="600" height="300">
  <style>
    .title {{ font: 700 18px 'Segoe UI', sans-serif; fill: #00F5D4; }}
    .lang {{ font: 600 14px 'Segoe UI', sans-serif; fill: #E5E7EB; }}
    .pct {{ font: 600 13px Consolas, monospace; fill: #94A3B8; text-anchor: end; }}
    .center {{ font: 800 22px 'Segoe UI', sans-serif; fill: #FFFFFF; text-anchor: middle; }}
    .sub {{ font: 600 11px 'Segoe UI', sans-serif; fill: #94A3B8; text-anchor: middle; letter-spacing: 1px; }}
    .arc {{ opacity: 0; animation: fade .6s ease-out forwards; }}
    @keyframes fade {{ to {{ opacity: 1; }} }}
  </style>
  <rect width="600" height="300" rx="14" fill="#0D1117" stroke="#1F2937"/>
  <text x="330" y="48" class="title">🧬 Lenguajes más usados</text>
  {''.join(arcs)}
  <text x="{cx}" y="{cy + 2}" class="center">{items[0][0]}</text>
  <text x="{cx}" y="{cy + 22}" class="sub">LENGUAJE #1</text>
  {''.join(legend)}
</svg>
"""
out = Path(__file__).resolve().parent.parent / "assets" / "lenguajes.svg"
out.write_text(svg, encoding="utf-8")
for lang, size in items:
    print(f"{lang:12} {size / total * 100:5.1f}%")
