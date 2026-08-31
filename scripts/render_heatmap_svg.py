"""Desenha data/contributions.json como um heatmap SVG animado.

Os quadrados entram em diagonal (semana a semana, dia a dia), cada um com um
pequeno "pop". A animacao roda uma vez e congela - nada de brilho em loop, que
vira poluicao visual num README. Tudo e CSS dentro do proprio SVG, porque o
GitHub remove <script> e CSS externo do README mas executa a animacao de um SVG
embutido via <img>.

Uso:  python scripts/render_heatmap_svg.py
"""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

W = 1000
PAD = 20
LABEL_COL = 40          # coluna dos nomes dos dias da semana
STEP = 17.4             # passo entre celulas
BOX = 14.2              # lado da celula
RADIUS = 3.4
TOP = 44                # espaco para o titulo e os meses
WEEKS = 53

MONTHS = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
          "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
WEEKDAYS = {1: "Seg", 3: "Qua", 5: "Sex"}

THEMES = {
    "dark": dict(
        bg="none", empty="#161B22", grid=["#0B3B39", "#0D9488", "#2DD4BF", "#5EEAD4"],
        text="#E6EDF3", muted="#7D8590", accent="#2DD4BF",
    ),
    "light": dict(
        bg="none", empty="#EBEDF0", grid=["#99F6E4", "#5EEAD4", "#14B8A6", "#0F766E"],
        text="#101720", muted="#5B6672", accent="#0D9488",
    ),
}


def color(level: int, t: dict) -> str:
    return t["empty"] if level <= 0 else t["grid"][min(level, 4) - 1]


def build(data: dict, theme: str) -> str:
    t = THEMES[theme]
    days = data["days"]
    s = data["stats"]

    # coluna = semana, linha = dia da semana (0 = domingo, como no GitHub)
    cells = []
    first = date.fromisoformat(days[0]["date"])
    offset = (first.weekday() + 1) % 7          # segunda=0 -> domingo=0
    for i, d in enumerate(days):
        idx = i + offset
        cells.append((idx // 7, idx % 7, d))
    weeks = max(c[0] for c in cells) + 1

    grid_x = PAD + LABEL_COL
    grid_y = TOP + 18
    height = int(grid_y + 7 * STEP + 46)

    rects = []
    for col, row, d in cells:
        x = grid_x + col * STEP
        y = grid_y + row * STEP
        delay = col * 0.013 + row * 0.028
        cls = "c hi" if d["level"] >= 3 else "c"
        rects.append(
            '<rect class="%s" x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="%s" '
            'fill="%s" style="animation-delay:%.2fs"><title>%s: %s</title></rect>'
            % (cls, x, y, BOX, BOX, RADIUS, color(d["level"], t), delay,
               d["date"], d["count"])
        )

    # rotulos de mes: primeira semana em que o mes aparece, sem colar um no outro
    labels = []
    seen = set()
    last_x = -999.0
    for col, row, d in cells:
        m = int(d["date"][5:7])
        if m in seen or row != 0:
            continue
        seen.add(m)
        x = grid_x + col * STEP
        if x - last_x < 34:
            continue
        last_x = x
        labels.append('<text class="mo" x="%.1f" y="%d">%s</text>'
                      % (x, TOP + 8, MONTHS[m - 1]))

    wd = "\n".join(
        '<text class="wd" x="%d" y="%.1f">%s</text>'
        % (PAD + LABEL_COL - 10, grid_y + r * STEP + BOX - 3, name)
        for r, name in WEEKDAYS.items()
    )

    # legenda ancorada na direita: [menos] [] [] [] [] [] [mais]
    base_y = height - 22
    boxes_w = 4 * 16 + 11
    boxes_x = W - PAD - 34 - boxes_w
    legend = ['<text class="lg" x="%.1f" y="%.1f" text-anchor="end">menos</text>'
              % (boxes_x - 8, base_y)]
    for i in range(5):
        legend.append(
            '<rect x="%.1f" y="%.1f" width="11" height="11" rx="2.6" fill="%s"/>'
            % (boxes_x + i * 16, base_y - 9.5, color(i, t))
        )
    legend.append('<text class="lg" x="%d" y="%.1f" text-anchor="end">mais</text>'
                  % (W - PAD, base_y))

    footer = ("%s contribuições no último ano  ·  %s dias ativos  ·  "
              "maior sequência %s dias  ·  melhor dia %s"
              % (s["total"], s["active_days"], s["longest_streak"], s["best_day"]["count"]))

    return TEMPLATE.format(
        W=W, H=height, PAD=PAD, text=t["text"], muted=t["muted"], accent=t["accent"],
        rects="\n".join(rects), months="\n".join(labels), weekdays=wd,
        legend="\n".join(legend), footer=footer, footer_y=height - 22,
        title_y=TOP - 20, updated=data.get("generated_at", ""),
        user=data.get("user", ""),
    )


TEMPLATE = '''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Gráfico de contribuições">
<style>
  text {{ font-family: ui-monospace,'SFMono-Regular','JetBrains Mono',Menlo,Consolas,monospace; }}
  .ttl {{ fill:{text}; font-size:14px; font-weight:700; letter-spacing:.4px; }}
  .upd {{ fill:{muted}; font-size:11.5px; }}
  .mo  {{ fill:{muted}; font-size:11.5px; }}
  .wd  {{ fill:{muted}; font-size:11px; text-anchor:end; }}
  .lg  {{ fill:{muted}; font-size:11px; }}
  .ft  {{ fill:{muted}; font-size:12px; }}

  .c {{ opacity:0; transform-box:fill-box; transform-origin:center;
        animation: pop .5s cubic-bezier(.2,.8,.3,1.2) both; }}
  .hi {{ animation: pop .5s cubic-bezier(.2,.8,.3,1.2) both,
                    spark .9s ease-out both; }}
  @keyframes pop {{
    0%   {{ opacity:0; transform:scale(.25) translateY(-6px) }}
    70%  {{ opacity:1; transform:scale(1.12) }}
    100% {{ opacity:1; transform:scale(1) }}
  }}
  @keyframes spark {{ 0%,55% {{ filter:brightness(2.1) }} 100% {{ filter:brightness(1) }} }}

  @media (prefers-reduced-motion: reduce) {{
    .c, .hi {{ opacity:1 !important; animation:none !important; }}
  }}
</style>

<text class="ttl" x="{PAD}" y="{title_y}">{user}@github ~ $ git log --graph --all</text>
<text class="upd" x="{W}" y="{title_y}" text-anchor="end" transform="translate(-{PAD} 0)">atualizado em {updated}</text>

{months}
{weekdays}
{rects}
{legend}
<text class="ft" x="{PAD}" y="{footer_y}">{footer}</text>
</svg>
'''


def main() -> None:
    data = json.loads((ROOT / "data" / "contributions.json").read_text(encoding="utf-8"))
    assets = ROOT / "assets"
    assets.mkdir(exist_ok=True)
    for theme in THEMES:
        out = assets / ("contrib-%s.svg" % theme)
        out.write_text(build(data, theme), encoding="utf-8")
        print("ok: %s (%.0f KB)" % (out.relative_to(ROOT), out.stat().st_size / 1024))


if __name__ == "__main__":
    main()
