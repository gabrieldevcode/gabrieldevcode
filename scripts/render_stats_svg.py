"""Desenha data/stats.json como dois paineis: numeros e linguagens.

Substitui o github-readme-stats. A instancia publica dele vive respondendo
"API rate limit exceeded" e a alternativa oficial e manter uma instancia no
Vercel; aqui o SVG e gerado junto com os outros assets e commitado no repo,
entao carrega instantaneo e nunca cai.

Uso:  python scripts/render_stats_svg.py
"""
from __future__ import annotations

import json
from pathlib import Path

from theme import MONO, THEMES, W, lang_color

ROOT = Path(__file__).resolve().parents[1]

GAP = 20
PANEL = (W - GAP) / 2
PAD = 22
TOP_N = 8

# Icones desenhados com primitivas: um <path> complexo vira borrao a 14px.
def icon(kind: str, x: float, y: float, c: str) -> str:
    g = 'stroke="%s" fill="none" stroke-width="1.5" stroke-linecap="round" ' \
        'stroke-linejoin="round"' % c
    if kind == "star":
        pts = "8,1.5 10,5.9 14.8,6.5 11.3,9.9 12.2,14.7 8,12.4 3.8,14.7 " \
              "4.7,9.9 1.2,6.5 6,5.9"
        return '<polygon points="%s" %s transform="translate(%.1f %.1f)"/>' % (pts, g, x, y)
    if kind == "clock":
        return ('<g %s transform="translate(%.1f %.1f)"><circle cx="8" cy="8" r="6.6"/>'
                '<path d="M8 4.2V8l2.6 1.8"/></g>' % (g, x, y))
    if kind == "pr":
        return ('<g %s transform="translate(%.1f %.1f)"><circle cx="4" cy="3.6" r="2.1"/>'
                '<circle cx="4" cy="12.4" r="2.1"/><circle cx="12.4" cy="12.4" r="2.1"/>'
                '<path d="M4 5.7v4.6M12.4 10.3V7.4a2.4 2.4 0 0 0-2.4-2.4H6.6"/>'
                '<path d="M8.4 3.2 6.4 5l2 1.8"/></g>' % (g, x, y))
    if kind == "issue":
        return ('<g %s transform="translate(%.1f %.1f)"><circle cx="8" cy="8" r="6.6"/>'
                '<path d="M8 4.6v4.2"/><circle cx="8" cy="11.5" r=".9" fill="%s" '
                'stroke="none"/></g>' % (g, x, y, c))
    # repo
    return ('<g %s transform="translate(%.1f %.1f)"><rect x="1.4" y="2" width="13.2" '
            'height="12" rx="2"/><path d="M4.4 2v12M1.4 6.6h3"/></g>' % (g, x, y))


def stat_rows(c: dict) -> list:
    rows = [("star", "Estrelas recebidas", c["stars"])]
    if c.get("commits") is not None:
        rows.append(("clock", "Commits totais", c["commits"]))
    if c.get("prs") is not None:
        rows.append(("pr", "Pull requests", c["prs"]))
    if c.get("issues") is not None:
        rows.append(("issue", "Issues abertas", c["issues"]))
    rows.append(("repo", "Repositórios",
                 "%s  (%s públicos)" % (c["repos"], c["public_repos"])))
    return rows


def build(data: dict, theme_name: str) -> str:
    t = THEMES[theme_name]
    c = data["counts"]
    langs = data["languages"][:TOP_N]

    rows = stat_rows(c)
    row_h = 26
    body_top = 62
    height = int(max(body_top + len(rows) * row_h + 18,
                     body_top + 30 + ((len(langs) + 1) // 2) * 26 + 18))

    # --- painel da esquerda: numeros ----------------------------------------
    left = []
    for i, (kind, label, value) in enumerate(rows):
        y = body_top + i * row_h
        left.append(
            '<g class="rw" style="animation-delay:%.2fs">%s'
            '<text class="lb" x="%.0f" y="%.0f">%s</text>'
            '<text class="vl" x="%.0f" y="%.0f">%s</text></g>'
            % (0.25 + i * 0.11, icon(kind, PAD, y - 12, t["ink"]),
               PAD + 26, y, label, PANEL - PAD, y, value)
        )

    # --- painel da direita: linguagens --------------------------------------
    ox = PANEL + GAP
    bar_x, bar_w = ox + PAD, PANEL - 2 * PAD
    bar_y, bar_h = body_top - 14, 13
    segs, x = [], float(bar_x)
    for i, l in enumerate(langs):
        w = bar_w * l["share"] / 100.0
        segs.append(
            '<rect class="sg" x="%.2f" y="%.1f" width="%.2f" height="%d" fill="%s" '
            'style="animation-delay:%.2fs"><title>%s: %.1f%% em %s repos</title></rect>'
            % (x, bar_y, w, bar_h, lang_color(l["name"], i, theme_name),
               0.3 + i * 0.09, l["name"], l["share"], l["repos"]))
        x += w
    rest = bar_w - (x - bar_x)
    if rest > 3:
        segs.append('<rect class="sg" x="%.2f" y="%.1f" width="%.2f" height="%d" '
                    'fill="%s" style="animation-delay:%.2fs"/>'
                    % (x, bar_y, rest, bar_h, t["faint"], 0.3 + len(langs) * 0.09))

    items, col_w = [], bar_w / 2
    for i, l in enumerate(langs):
        lx = bar_x + (i % 2) * col_w
        ly = bar_y + 40 + (i // 2) * 26
        items.append(
            '<g class="rw" style="animation-delay:%.2fs">'
            '<circle cx="%.1f" cy="%.1f" r="4.4" fill="%s"/>'
            '<text class="lg" x="%.1f" y="%.1f">%s</text>'
            '<text class="pc" x="%.1f" y="%.1f">%.1f%%</text></g>'
            % (0.6 + i * 0.06, lx + 4.4, ly - 4, lang_color(l["name"], i, theme_name),
               lx + 16, ly, l["name"], lx + col_w - 16, ly, l["share"]))

    return TEMPLATE.format(
        W=W, H=height, MONO=MONO, PANEL=PANEL, GAP=GAP, PAD=PAD, ox=ox,
        bg=t["bg"], panel=t["panel"], stroke=t["stroke"], chrome=t["chrome"],
        text=t["text"], muted=t["muted"], accent=t["accent"], faint=t["faint"],
        left="\n".join(left), segs="\n".join(segs), items="\n".join(items),
        Hm1=height - 1, PANELm1=PANEL - 1, ox_half=ox + 0.5,
        hd2_x=ox + PAD, rule_x2=PANEL - PAD, rule2_x2=W - PAD,
        note="peso por repositório, não por bytes",
        note_y=height - 9, updated=data.get("generated_at", ""),
    )


TEMPLATE = '''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Numeros e linguagens">
<style>
  text {{ font-family: {MONO}; }}
  .hd {{ fill:{chrome}; font-size:15px; font-weight:700; letter-spacing:.3px; }}
  .lb {{ fill:{muted}; font-size:13px; }}
  .vl {{ fill:{text}; font-size:13px; font-weight:700; text-anchor:end; }}
  .lg {{ fill:{text}; font-size:12.5px; }}
  .pc {{ fill:{muted}; font-size:12.5px; text-anchor:end; }}
  .nt {{ fill:{faint}; font-size:10.5px; text-anchor:end; }}

  .rw {{ opacity:0; animation: fade .55s ease-out both; }}
  @keyframes fade {{ from {{ opacity:0; transform:translateY(7px) }} to {{ opacity:1; transform:none }} }}
  .sg {{ transform-box:fill-box; transform-origin:left center;
         animation: grow .9s cubic-bezier(.2,.8,.25,1) both; }}
  @keyframes grow {{ from {{ transform:scaleX(0) }} to {{ transform:scaleX(1) }} }}

  @media (prefers-reduced-motion: reduce) {{
    .rw, .sg {{ opacity:1 !important; animation:none !important; transform:none !important; }}
  }}
</style>

<rect x=".5" y=".5" width="{PANELm1}" height="{Hm1}" rx="12" fill="{panel}" stroke="{stroke}">
  <animate attributeName="stroke" values="{stroke};{chrome};{stroke}" dur="6s" begin="1s" repeatCount="indefinite"/>
</rect>
<rect x="{ox_half}" y=".5" width="{PANELm1}" height="{Hm1}" rx="12" fill="{panel}" stroke="{stroke}">
  <animate attributeName="stroke" values="{stroke};{chrome};{stroke}" dur="6s" begin="3s" repeatCount="indefinite"/>
</rect>

<text class="hd" x="{PAD}" y="34">Números do GitHub</text>
<line x1="{PAD}" y1="46" x2="{rule_x2}" y2="46" stroke="{chrome}" stroke-width="1.5" opacity=".3"/>
{left}

<text class="hd" x="{hd2_x}" y="34">Linguagens mais usadas</text>
<line x1="{hd2_x}" y1="46" x2="{rule2_x2}" y2="46" stroke="{chrome}" stroke-width="1.5" opacity=".3"/>
{segs}
{items}
<text class="nt" x="{W}" y="{note_y}" transform="translate(-{PAD} 0)">{note}</text>
</svg>
'''


def main() -> None:
    data = json.loads((ROOT / "data" / "stats.json").read_text(encoding="utf-8"))
    assets = ROOT / "assets"
    assets.mkdir(exist_ok=True)
    for theme in THEMES:
        out = assets / ("stats-%s.svg" % theme)
        out.write_text(build(data, theme), encoding="utf-8")
        print("ok: %s (%.1f KB)" % (out.relative_to(ROOT), out.stat().st_size / 1024))


if __name__ == "__main__":
    main()
