"""Genera assets/actividad.svg con las contribuciones de los últimos 31 días.

Uso:  python scripts/actividad.py   (requiere `gh` autenticado; en Actions usa GH_TOKEN)
"""
import json
import subprocess
from datetime import date
from pathlib import Path

USER = "Saler123"
DAYS = 31
QUERY = """query($login:String!){user(login:$login){contributionsCollection{
  contributionCalendar{totalContributions weeks{contributionDays{date contributionCount}}}}}}"""

data = json.loads(subprocess.check_output(
    ["gh", "api", "graphql", "-f", f"query={QUERY}", "-f", f"login={USER}"], text=True, encoding="utf-8"))
cal = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]
days = [d for w in cal["weeks"] for d in w["contributionDays"]][-DAYS:]
counts = [d["contributionCount"] for d in days]

W, H = 1000, 320
left, right, top, bottom = 60, 30, 70, 50
pw, ph = W - left - right, H - top - bottom
peak = max(max(counts), 4)
step = pw / (len(counts) - 1)
pts = [(left + i * step, top + ph - c / peak * ph) for i, c in enumerate(counts)]

line = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
area = f"M {left},{top + ph} L " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in pts) + f" L {left + pw},{top + ph} Z"

grid = []
for i in range(5):
    v = peak * i / 4
    y = top + ph - ph * i / 4
    grid.append(f'<line x1="{left}" y1="{y:.1f}" x2="{left + pw}" y2="{y:.1f}" class="grid"/>'
                f'<text x="{left - 10}" y="{y + 4:.1f}" class="axis" text-anchor="end">{v:.0f}</text>')
labels = []
for i, d in enumerate(days):
    if i % 5 == 0 or i == len(days) - 1:
        dd = date.fromisoformat(d["date"])
        labels.append(f'<text x="{pts[i][0]:.1f}" y="{H - 22}" class="axis" text-anchor="middle">{dd.day:02d}/{dd.month:02d}</text>')
dots = "".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" class="dot"><title>{d["date"]}: {c}</title></circle>'
               for (x, y), d, c in zip(pts, days, counts))

svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="100%">
  <defs>
    <linearGradient id="fill" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#00F5D4" stop-opacity="0.35"/>
      <stop offset="100%" stop-color="#00F5D4" stop-opacity="0"/>
    </linearGradient>
  </defs>
  <style>
    .title {{ font: 700 18px 'Segoe UI', sans-serif; fill: #00F5D4; }}
    .meta {{ font: 600 13px Consolas, monospace; fill: #94A3B8; }}
    .axis {{ font: 12px Consolas, monospace; fill: #6B7280; }}
    .grid {{ stroke: #1F2937; stroke-width: 1; }}
    .line {{ fill: none; stroke: #D91023; stroke-width: 3; stroke-linejoin: round;
             stroke-dasharray: 4000; stroke-dashoffset: 4000; animation: draw 2.5s ease-out forwards; }}
    .dot {{ fill: #38BDF8; stroke: #0D1117; stroke-width: 2; }}
    @keyframes draw {{ to {{ stroke-dashoffset: 0; }} }}
  </style>
  <rect width="{W}" height="{H}" rx="14" fill="#0D1117" stroke="#1F2937"/>
  <text x="{left}" y="38" class="title">📈 Gráfico de actividad — últimos {DAYS} días</text>
  <text x="{W - right}" y="38" class="meta" text-anchor="end">{sum(counts)} en {DAYS} días • {cal["totalContributions"]} en el año</text>
  {''.join(grid)}
  <path d="{area}" fill="url(#fill)"/>
  <polyline points="{line}" class="line"/>
  {dots}
  {''.join(labels)}
</svg>
"""
out = Path(__file__).resolve().parent.parent / "assets" / "actividad.svg"
out.write_text(svg, encoding="utf-8")
print(f"{sum(counts)} contribuciones en {DAYS} días, {cal['totalContributions']} en el año")
