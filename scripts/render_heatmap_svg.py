"""Desenha data/contributions.json como um heatmap SVG animado.

Os quadrados entram em diagonal, semana a semana. A animacao roda uma vez e
congela - nada de brilho em loop, que vira poluicao visual num README. Tudo e
CSS dentro do proprio SVG, porque o GitHub remove <script> e CSS externo do
markdown mas executa a animacao de um SVG embutido via <img>.

Uso:  python scripts/render_heatmap_svg.py
"""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from theme import HEAT, MONO, THEMES, W

ROOT = Path(__file__).resolve().parents[1]

PAD = 20
LABEL_COL = 40          # coluna dos nomes dos dias da semana
STEP = 17.4             # passo entre celulas
BOX = 14.2
RADIUS = 3.4
TOP = 44

# Ritmo da revelacao. Lento de proposito: rapido demais, o olho so ve o
# resultado, nao o desenho acontecendo.
COL_DELAY = 0.045
ROW_DELAY = 0.09
POP = 0.7

# A revelacao se repete a cada CYCLE segundos. Nao da para disparar no hover:
# o GitHub renderiza o SVG do README dentro de um <img>, e <img> nao entrega
# evento de ponteiro para dentro do documento SVG - nem :hover do CSS, nem
# begin="mouseover" do SMIL chegam la. Repetir e a unica forma de quem esta
# olhando ver a animacao de novo sem recarregar a pagina.
CYCLE = 15.0


def keyframes() -> dict:
    """Converte os tempos do pop em porcentagens do ciclo inteiro."""
    return {
        "cycle": CYCLE,
        "up": 100 * POP * 0.7 / CYCLE,      # fim do overshoot
        "settle": 100 * POP / CYCLE,        # celula assentada
        "hold": 100 * (CYCLE - 1.4) / CYCLE,  # comeca a sair
        "gone": 100 * (CYCLE - 0.5) / CYCLE,
        "spark_on": 100 * 0.45 / CYCLE,
        "spark_off": 100 * 1.6 / CYCLE,
    }

MONTHS = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
          "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
WEEKDAYS = {1: "Seg", 3: "Qua", 5: "Sex"}


def color(level: int, theme: str) -> str:
    ramp = HEAT[theme]
    return ramp[0] if level <= 0 else ramp[min(level, 4)]


def build(data: dict, theme_name: str) -> str:
    t = THEMES[theme_name]
    days = data["days"]
    s = data["stats"]

    # coluna = semana, linha = dia da semana (0 = domingo, como no GitHub)
    first = date.fromisoformat(days[0]["date"])
    offset = (first.weekday() + 1) % 7          # segunda=0 -> domingo=0
    cells = [((i + offset) // 7, (i + offset) % 7, d) for i, d in enumerate(days)]

    grid_x = PAD + LABEL_COL
    grid_y = TOP + 18
    height = int(grid_y + 7 * STEP + 46)

    rects = []
    for col, row, d in cells:
        cls = "c hi" if d["level"] >= 3 else "c"
        rects.append(
            '<rect class="%s" x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="%s" '
            'fill="%s" style="animation-delay:%.2fs"><title>%s: %s</title></rect>'
            % (cls, grid_x + col * STEP, grid_y + row * STEP, BOX, BOX, RADIUS,
               color(d["level"], theme_name), col * COL_DELAY + row * ROW_DELAY,
               d["date"], d["count"])
        )

    # rotulos de mes: primeira semana do mes, sem colar um no outro
    labels, seen, last_x = [], set(), -999.0
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

    # legenda ancorada na direita: menos [][][][][] mais
    base_y = height - 22
    boxes_x = W - PAD - 34 - (4 * 16 + 11)
    legend = ['<text class="lg" x="%.1f" y="%.1f" text-anchor="end">menos</text>'
              % (boxes_x - 8, base_y)]
    for i in range(5):
        legend.append(
            '<rect x="%.1f" y="%.1f" width="11" height="11" rx="2.6" fill="%s"/>'
            % (boxes_x + i * 16, base_y - 9.5, color(i, theme_name)))
    legend.append('<text class="lg" x="%d" y="%.1f" text-anchor="end">mais</text>'
                  % (W - PAD, base_y))

    footer = ("%s contribuições no último ano  ·  %s dias ativos  ·  "
              "maior sequência %s dias  ·  melhor dia %s"
              % (s["total"], s["active_days"], s["longest_streak"],
                 s["best_day"]["count"]))

    return TEMPLATE.format(
        W=W, H=height, PAD=PAD, MONO=MONO, POP=POP, **keyframes(),
        text=t["text"], muted=t["muted"], chrome=t["chrome"],
        rects="\n".join(rects), months="\n".join(labels), weekdays=wd,
        legend="\n".join(legend), footer=footer, footer_y=base_y,
        title_y=TOP - 20, updated=data.get("generated_at", ""),
        user=data.get("user", ""),
    )


TEMPLATE = '''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Grafico de contribuicoes">
<style>
  text {{ font-family: {MONO}; }}
  .ttl {{ fill:{chrome}; font-size:14px; font-weight:700; letter-spacing:.4px; }}
  .upd {{ fill:{muted}; font-size:11.5px; }}
  .mo  {{ fill:{muted}; font-size:11.5px; }}
  .wd  {{ fill:{muted}; font-size:11px; text-anchor:end; }}
  .lg  {{ fill:{muted}; font-size:11px; }}
  .ft  {{ fill:{muted}; font-size:12px; }}

  /* Um ciclo longo por celula, com o atraso da diagonal preservado: a grade
     se desenha, fica parada quase o ciclo inteiro e se recolhe na mesma
     diagonal, sem fim. O easing vai dentro dos keyframes porque o `linear` da
     declaracao vale para o ciclo inteiro. */
  .c {{ opacity:0; transform-box:fill-box; transform-origin:center;
        animation: pop {cycle}s linear infinite both; }}
  .hi {{ animation: pop {cycle}s linear infinite both,
                    spark {cycle}s linear infinite both; }}
  @keyframes pop {{
    0%       {{ opacity:0; transform:scale(.2) translateY(-7px);
                animation-timing-function: cubic-bezier(.2,.8,.3,1.2) }}
    {up:.2f}%    {{ opacity:1; transform:scale(1.14) }}
    {settle:.2f}%  {{ opacity:1; transform:scale(1) }}
    {hold:.2f}%  {{ opacity:1; transform:scale(1);
                animation-timing-function: cubic-bezier(.5,0,.75,0) }}
    {gone:.2f}%  {{ opacity:0; transform:scale(.7) }}
    100%     {{ opacity:0; transform:scale(.2) }}
  }}
  @keyframes spark {{
    0%,{spark_on:.2f}%   {{ filter:brightness(2.2) }}
    {spark_off:.2f}%,100% {{ filter:brightness(1) }}
  }}

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
