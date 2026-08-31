"""Desenha data/stats.json como o cartao de linguagens e numeros do perfil.

Substitui o github-readme-stats: nada de instancia publica (que vive batendo em
"API rate limit exceeded") nem de Vercel para manter. O SVG e commitado no repo
e carrega instantaneo.

Uso:  python scripts/render_stats_svg.py
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

W = 1000
PAD = 20
TOP = 24
BAR_Y = 46
BAR_H = 15
COLS = 4
TOP_N = 8

# cores do linguist; C e cinza escuro demais para fundo escuro, entao tem troca
LANG_COLORS = {
    "Python": "#3572A5", "TypeScript": "#3178C6", "JavaScript": "#F1E05A",
    "C": "#8C97A3", "C++": "#F34B7D", "HTML": "#E34C26", "CSS": "#663399",
    "PLpgSQL": "#336790", "Java": "#B07219", "Go": "#00ADD8", "Rust": "#DEA584",
    "Dart": "#00B4AB", "Kotlin": "#A97BFF", "Swift": "#F05138", "Lua": "#000080",
}
LIGHT_OVERRIDE = {"C": "#4A5561", "JavaScript": "#C9AE00"}
FALLBACK = ["#2DD4BF", "#F5A524", "#A78BFA", "#F87171", "#60A5FA"]

THEMES = {
    "dark": dict(text="#E6EDF3", muted="#7D8590", faint="#4A535E", track="#161B22"),
    "light": dict(text="#101720", muted="#5B6672", faint="#8A939E", track="#EBEDF0"),
}


def color(name: str, i: int, theme: str) -> str:
    if theme == "light" and name in LIGHT_OVERRIDE:
        return LIGHT_OVERRIDE[name]
    return LANG_COLORS.get(name, FALLBACK[i % len(FALLBACK)])


def build(data: dict, theme: str) -> str:
    t = THEMES[theme]
    langs = data["languages"][:TOP_N]
    c = data["counts"]

    # o resto vira uma fatia "outras" para a barra fechar em 100%
    shown = sum(l["share"] for l in langs)
    rest = max(0.0, 100.0 - shown)

    bar_w = W - 2 * PAD
    segs = []
    x = float(PAD)
    for i, l in enumerate(langs):
        w = bar_w * l["share"] / 100.0
        segs.append(
            '<rect class="sg" x="%.2f" y="%d" width="%.2f" height="%d" fill="%s" '
            'style="animation-delay:%.2fs"><title>%s: %.1f%% (%s repos)</title></rect>'
            % (x, BAR_Y, w, BAR_H, color(l["name"], i, theme), 0.15 + i * 0.09,
               l["name"], l["share"], l["repos"])
        )
        x += w
    if rest > 0.4:
        segs.append(
            '<rect class="sg" x="%.2f" y="%d" width="%.2f" height="%d" fill="%s" '
            'style="animation-delay:%.2fs"/>'
            % (x, BAR_Y, bar_w - (x - PAD), BAR_H, t["faint"], 0.15 + len(langs) * 0.09)
        )

    rows = (len(langs) + COLS - 1) // COLS
    col_w = bar_w / COLS
    items = []
    for i, l in enumerate(langs):
        cx = PAD + (i % COLS) * col_w
        cy = BAR_Y + 46 + (i // COLS) * 30
        items.append(
            '<g class="lg" style="animation-delay:%.2fs">'
            '<rect x="%.1f" y="%.1f" width="9" height="9" rx="2.5" fill="%s"/>'
            '<text class="nm" x="%.1f" y="%.1f">%s</text>'
            '<text class="pc" x="%.1f" y="%.1f">%.1f%%</text></g>'
            % (0.55 + i * 0.06, cx, cy - 9, color(l["name"], i, theme),
               cx + 16, cy, l["name"], cx + col_w - 28, cy, l["share"])
        )

    footer_y = BAR_Y + 46 + rows * 30 + 22
    height = int(footer_y + 26)

    counters = "%s repositórios  ·  %s públicos  ·  %s estrelas  ·  no GitHub desde %s" % (
        c["repos"], c["public_repos"], c["stars"], c["since"])
    note = ("peso por repositório, não por bytes — um projeto grande sozinho "
            "não decide o gráfico")

    return TEMPLATE.format(
        W=W, H=height, PAD=PAD, TOP=TOP, BAR_Y=BAR_Y, BAR_H=BAR_H,
        text=t["text"], muted=t["muted"], faint=t["faint"], track=t["track"],
        user=data.get("user", ""), updated=data.get("generated_at", ""),
        bar_w=bar_w, segs="\n".join(segs), items="\n".join(items),
        counters=counters, note=note, footer_y=footer_y, note_y=height - 6,
        rx=BAR_H / 2,
    )


TEMPLATE = '''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Linguagens mais usadas">
<style>
  text {{ font-family: ui-monospace,'SFMono-Regular','JetBrains Mono',Menlo,Consolas,monospace; }}
  .ttl {{ fill:{text}; font-size:14px; font-weight:700; letter-spacing:.4px; }}
  .upd {{ fill:{muted}; font-size:11.5px; }}
  .nm  {{ fill:{text}; font-size:12.5px; }}
  .pc  {{ fill:{muted}; font-size:12.5px; text-anchor:end; }}
  .ft  {{ fill:{muted}; font-size:12px; }}
  .nt  {{ fill:{faint}; font-size:11px; }}

  .sg {{ transform-box:fill-box; transform-origin:left center;
         animation: grow .8s cubic-bezier(.2,.8,.25,1) both; }}
  @keyframes grow {{ from {{ transform:scaleX(0) }} to {{ transform:scaleX(1) }} }}

  .lg {{ opacity:0; animation: fade .6s ease-out both; }}
  @keyframes fade {{ from {{ opacity:0; transform:translateY(6px) }} to {{ opacity:1; transform:none }} }}

  @media (prefers-reduced-motion: reduce) {{
    .sg, .lg {{ opacity:1 !important; animation:none !important; transform:none !important; }}
  }}
</style>

<text class="ttl" x="{PAD}" y="{TOP}">{user}@github ~ $ cat languages.json</text>
<text class="upd" x="{W}" y="{TOP}" text-anchor="end" transform="translate(-{PAD} 0)">atualizado em {updated}</text>

<clipPath id="round"><rect x="{PAD}" y="{BAR_Y}" width="{bar_w}" height="{BAR_H}" rx="{rx}"/></clipPath>
<rect x="{PAD}" y="{BAR_Y}" width="{bar_w}" height="{BAR_H}" rx="{rx}" fill="{track}"/>
<g clip-path="url(#round)">
{segs}
</g>

{items}

<text class="ft" x="{PAD}" y="{footer_y}">{counters}</text>
<text class="nt" x="{W}" y="{footer_y}" text-anchor="end" transform="translate(-{PAD} 0)">{note}</text>
</svg>
'''


def main() -> None:
    data = json.loads((ROOT / "data" / "stats.json").read_text(encoding="utf-8"))
    assets = ROOT / "assets"
    assets.mkdir(exist_ok=True)
    for theme in THEMES:
        out = assets / ("langs-%s.svg" % theme)
        out.write_text(build(data, theme), encoding="utf-8")
        print("ok: %s (%.1f KB)" % (out.relative_to(ROOT), out.stat().st_size / 1024))


if __name__ == "__main__":
    main()
