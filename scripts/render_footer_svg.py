"""Desenha o rodape animado (assets/footer-dark.svg e footer-light.svg).

Uma linha de terminal que se digita sozinha e um traco de osciloscopio que
atravessa a largura toda em loop. Nao depende de dado nenhum, entao nao entra
no workflow diario - so e regerado quando a frase muda.

Uso:  python scripts/render_footer_svg.py
"""
from __future__ import annotations

import math
from pathlib import Path

from theme import MONO, THEMES, W

ROOT = Path(__file__).resolve().parents[1]

H = 150
PROMPT = "gabrieldevcode@github ~ $ "
LINE = 'echo "Eletrônica → Software → Inteligência"'
CHAR = 8.42            # largura de um caractere em 14px na fonte mono
TYPE_DUR = 2.6
CLOSING = "Aberto a estágio, pesquisa e projetos de engenharia."


def pulse(y: float) -> str:
    """Traco tipo ECG: base plana com um batimento no meio."""
    pts = []
    for i in range(0, W + 1, 4):
        x = i
        d = x - W / 2
        if -70 < d < 70:
            # o batimento: um vale, um pico alto, outro vale
            v = (-8 * math.exp(-((d + 26) ** 2) / 90)
                 + 30 * math.exp(-(d ** 2) / 70)
                 - 11 * math.exp(-((d - 26) ** 2) / 120))
        else:
            v = 1.6 * math.sin(x / 26.0) * math.exp(-abs(d) / 620)
        pts.append("%d %.1f" % (x, y - v))
    return "M" + " L".join(pts)


def build(theme_name: str) -> str:
    t = THEMES[theme_name]
    full = PROMPT + LINE
    text_w = len(full) * CHAR
    x0 = (W - text_w) / 2

    # a "digitacao" e um retangulo de recorte que cresce em passos de caractere,
    # entao o texto aparece letra a letra em vez de deslizar
    steps = len(LINE)
    keys = ";".join("%.4f" % (i / steps) for i in range(steps + 1))
    widths = ";".join("%.1f" % (len(PROMPT) * CHAR + i * CHAR) for i in range(steps + 1))

    return TEMPLATE.format(
        W=W, H=H, MONO=MONO, bg=t["bg"], chrome=t["chrome"], ink=t["ink"],
        accent=t["accent"], text=t["text"], muted=t["muted"], faint=t["faint"],
        prompt=PROMPT, line=LINE.replace("&", "&amp;").replace("<", "&lt;"),
        closing=CLOSING, x0="%.1f" % x0, y=54, text_w="%.1f" % text_w,
        half_w=W // 2,
        cursor_x0="%.1f" % (x0 + len(PROMPT) * CHAR),
        cursor_keys=keys, cursor_vals=";".join(
            "%.1f" % (x0 + len(PROMPT) * CHAR + i * CHAR) for i in range(steps + 1)),
        clip_keys=keys, clip_vals=widths, clip_x="%.1f" % x0,
        TYPE=TYPE_DUR, pulse=pulse(104), pulse_len=W + 200,
    )


TEMPLATE = '''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Eletronica, Software, Inteligencia">
<style>
  text {{ font-family: {MONO}; }}
  .pr {{ fill:{muted}; font-size:14px; }}
  .ln {{ fill:{text}; font-size:14px; }}
  .cl {{ fill:{muted}; font-size:12.5px; text-anchor:middle; opacity:0;
         animation: fade .8s ease-out 3.2s both; }}
  @keyframes fade {{ from {{ opacity:0; transform:translateY(6px) }} to {{ opacity:1; transform:none }} }}
  @media (prefers-reduced-motion: reduce) {{ .cl {{ opacity:1 !important; animation:none !important; }} }}
</style>

<defs>
  <clipPath id="type">
    <rect x="{clip_x}" y="34" height="26" width="0">
      <animate attributeName="width" dur="{TYPE}s" begin="0.4s" fill="freeze"
               calcMode="discrete" keyTimes="{clip_keys}" values="{clip_vals}"/>
    </rect>
  </clipPath>
  <linearGradient id="ft" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="{chrome}" stop-opacity="0"/>
    <stop offset=".5" stop-color="{ink}"/>
    <stop offset="1" stop-color="{accent}" stop-opacity="0"/>
  </linearGradient>
</defs>

<g clip-path="url(#type)">
  <text class="pr" x="{x0}" y="{y}" textLength="{text_w}" lengthAdjust="spacingAndGlyphs">{prompt}<tspan class="ln">{line}</tspan></text>
</g>

<!-- cursor em bloco: acompanha a ponta do texto e depois fica piscando -->
<rect y="40" width="8.4" height="17" fill="{chrome}" x="{cursor_x0}">
  <animate attributeName="x" dur="{TYPE}s" begin="0.4s" fill="freeze"
           calcMode="discrete" keyTimes="{cursor_keys}" values="{cursor_vals}"/>
  <animate attributeName="opacity" values="1;1;0;0;1" dur="1.1s" begin="0s" repeatCount="indefinite"/>
</rect>

<!-- traco de osciloscopio: um segmento curto correndo sobre a linha inteira -->
<path d="{pulse}" fill="none" stroke="{faint}" stroke-width="1.3" opacity=".55"/>
<path d="{pulse}" fill="none" stroke="url(#ft)" stroke-width="2.4"
      stroke-linecap="round" stroke-dasharray="210 {pulse_len}">
  <animate attributeName="stroke-dashoffset" from="210" to="-{pulse_len}"
           dur="6s" begin="1.2s" repeatCount="indefinite"/>
</path>

<text class="cl" x="{half_w}" y="138">{closing}</text>
</svg>
'''


def main() -> None:
    assets = ROOT / "assets"
    assets.mkdir(exist_ok=True)
    for theme in THEMES:
        out = assets / ("footer-%s.svg" % theme)
        out.write_text(build(theme), encoding="utf-8")
        print("ok: %s (%.1f KB)" % (out.relative_to(ROOT), out.stat().st_size / 1024))


if __name__ == "__main__":
    main()
