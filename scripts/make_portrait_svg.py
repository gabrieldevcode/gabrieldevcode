"""Gera o banner animado do perfil (assets/banner-dark.svg e banner-light.svg).

O retrato e um dithering Floyd-Steinberg 1-bit desenhado como <path> (nunca
glifos de fonte - eles borram abaixo de 2px). A animacao de entrada revela ~64
grupos de pontos espalhados por todo o retrato ao mesmo tempo, entao a foto
"materializa" em vez de ser varrida de cima para baixo. Depois da entrada os
grupos ficam oscilando de leve, o que mantem o retrato vivo sem duplicar dados.

Uso:  python scripts/make_portrait_svg.py
"""
from __future__ import annotations

import random
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "build"
ASSETS = ROOT / "assets"

GRID_W, GRID_H = 258, 292      # resolucao do dithering
DOT = 1.45                     # lado do ponto em unidades SVG
GROUPS = 64                    # grupos da animacao de entrada

W, H = 1000, 492               # tamanho do banner
BAR = 40                       # altura da barra de titulo
PAD = 26

HANDLE = "gabrieldevcode"
NAME = "GABRIEL BARRETO"
LINES = [
    "Engenharia Eletrônica e de Computação · UFRJ",
    "Sistemas embarcados · IA aplicada · Automação",
    "Rio de Janeiro, Brasil",
]

THEMES = {
    "dark": dict(
        bg="#0A0E14", panel="#0D1117", stroke="#1C2430", chrome="#2DD4BF",
        ink="#DCE7F2", text="#E6EDF3", muted="#7D8590", accent="#F5A524",
        invert=False, floor=0.24,
    ),
    "light": dict(
        bg="#FFFFFF", panel="#F6F8FA", stroke="#D8DEE6", chrome="#0D9488",
        ink="#141A21", text="#101720", muted="#5B6672", accent="#B45309",
        invert=True, floor=0.06,
    ),
}


def dither(ink: np.ndarray) -> np.ndarray:
    """Floyd-Steinberg 1-bit em ordem serpentina."""
    a = ink.astype(np.float64).copy()
    h, w = a.shape
    out = np.zeros((h, w), bool)
    for y in range(h):
        rng = range(w) if y % 2 == 0 else range(w - 1, -1, -1)
        fwd = 1 if y % 2 == 0 else -1
        for x in rng:
            old = a[y, x]
            new = 1.0 if old >= 0.5 else 0.0
            out[y, x] = new > 0.5
            err = old - new
            if 0 <= x + fwd < w:
                a[y, x + fwd] += err * 7 / 16
            if y + 1 < h:
                if 0 <= x - fwd < w:
                    a[y + 1, x - fwd] += err * 3 / 16
                a[y + 1, x] += err * 5 / 16
                if 0 <= x + fwd < w:
                    a[y + 1, x + fwd] += err * 1 / 16
    return out


def runs(dots: np.ndarray) -> list:
    """Sequencias horizontais de pontos ligados -> (x, y, comprimento)."""
    out = []
    h, w = dots.shape
    for y in range(h):
        x = 0
        row = dots[y]
        while x < w:
            if row[x]:
                x0 = x
                while x < w and row[x]:
                    x += 1
                out.append((x0, y, x - x0))
            else:
                x += 1
    return out


def path_for(rs: list) -> str:
    parts = []
    for x, y, n in rs:
        px = round(x * DOT, 2)
        py = round(y * DOT, 2)
        wd = round(n * DOT, 2)
        parts.append("M%s %sh%sv%sh-%sz" % (px, py, wd, DOT, wd))
    return "".join(parts)


def build(theme: str) -> str:
    t = THEMES[theme]
    gray = np.asarray(Image.open(BUILD / "prepped-gray.png").resize(
        (GRID_W, GRID_H), Image.LANCZOS), dtype=np.float64) / 255.0
    mask = np.asarray(Image.open(BUILD / "prepped-mask.png").resize(
        (GRID_W, GRID_H), Image.LANCZOS)) > 128

    if t["invert"]:
        # modo claro: tinta escura desenha as partes escuras da foto.
        # o gamma < 1 puxa os meios-tons para cima, senao o rosto some no papel.
        ink = np.power(1.0 - gray, 0.82)
    else:
        # modo escuro: pontos claros desenham a luz que bate no rosto.
        # o piso mantem o polo preto visivel como silhueta em vez de sumir;
        # o teto segura textura nas altas luzes em vez de virar bloco solido.
        ink = t["floor"] + (0.93 - t["floor"]) * np.power(gray, 1.08)
    ink = np.clip(ink, 0.0, 1.0)
    ink[~mask] = 0.0

    # dissolve a base do busto para o corte reto nao terminar em aresta dura
    fade = np.ones(GRID_H)
    tail = 30
    fade[-tail:] = np.linspace(1.0, 0.12, tail)
    ink *= fade[:, None]

    dots = dither(ink)
    dots[~mask] = False          # corta o sangramento do erro na borda da mascara

    rs = runs(dots)

    # Corta sequencias longas antes de sortear o grupo. Sem isso, uma area
    # solida (o polo preto) entra inteira de uma vez e a revelacao vira listras
    # horizontais em vez de uma nuvem de pontos.
    CHUNK = 4
    pieces = []
    for x, y, n in rs:
        for off in range(0, n, CHUNK):
            pieces.append((x + off, y, min(CHUNK, n - off)))

    rnd = random.Random(7)
    buckets = [[] for _ in range(GROUPS)]
    for r in pieces:
        buckets[rnd.randrange(GROUPS)].append(r)

    pw, ph = GRID_W * DOT, GRID_H * DOT
    px = PAD + 8
    py = BAR + 10                  # o pe do busto dissolve, entao nao precisa centralizar
    rx = px + pw + 46
    cx = rx + (W - PAD - rx) / 2   # centro da coluna de texto

    paths = []
    for b in buckets:
        if not b:
            continue
        d = rnd.uniform(0.0, 1.55)
        s = 4.6 + rnd.uniform(0.0, 3.4)
        paths.append(
            '<path class="d" style="animation-delay:%.2fs,%.2fs" d="%s"/>'
            % (d, s, path_for(b))
        )
    portrait = "\n".join(paths)

    text_rows = "\n".join(
        '<text class="ln" x="%.0f" y="%d" style="animation-delay:%.2fs">%s</text>'
        % (cx, 288 + i * 30, 1.5 + i * 0.22, v)
        for i, v in enumerate(LINES)
    )

    return TEMPLATE.format(
        W=W, H=H, BAR=BAR, NAME=NAME, HANDLE=HANDLE,
        ink=t["ink"], bg=t["bg"], panel=t["panel"], stroke=t["stroke"],
        chrome=t["chrome"], text=t["text"], muted=t["muted"], accent=t["accent"],
        Wm1=W - 1, Hm1=H - 1, Wm24=W - 24, BARm12=BAR - 12,
        barmid=BAR / 2, bartext=BAR / 2 + 4.5, halfW=W / 2,
        px=px, py=py, cx=round(cx), portrait=portrait, text_rows=text_rows,
        rule_x1=round(cx - 60), rule_x2=round(cx + 60),
        pill_y=288 + len(LINES) * 30 + 26,
    )


TEMPLATE = '''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{NAME}">
<title>{NAME} - {HANDLE}</title>
<style>
  .d {{ fill:{ink}; opacity:0;
        animation: reveal 1.5s ease-out both, breathe 7s ease-in-out infinite; }}
  @keyframes reveal {{ from {{ opacity:0 }} to {{ opacity:1 }} }}
  @keyframes breathe {{ 0%,100% {{ opacity:1 }} 50% {{ opacity:.82 }} }}

  text {{ font-family: ui-monospace,'SFMono-Regular','JetBrains Mono',Menlo,Consolas,monospace; }}
  .bar   {{ fill:{muted}; font-size:13px; letter-spacing:.6px; }}
  .name  {{ fill:{text}; font-size:42px; font-weight:700; letter-spacing:3.5px;
            text-anchor:middle; opacity:0; animation: rise .9s cubic-bezier(.2,.7,.3,1) .95s both; }}
  .kicker{{ fill:{chrome}; font-size:13px; letter-spacing:5px; text-anchor:middle;
            opacity:0; animation: rise .8s ease-out .75s both; }}
  .ln    {{ fill:{muted}; font-size:14.5px; letter-spacing:.3px; text-anchor:middle;
            opacity:0; animation: rise .7s ease-out both; }}
  .pill  {{ fill:{accent}; font-size:13.5px; letter-spacing:1.2px; text-anchor:middle;
            opacity:0; animation: rise .7s ease-out 2.3s both; }}
  .rule  {{ stroke:{chrome}; stroke-width:2; opacity:0;
            animation: grow .8s cubic-bezier(.2,.7,.3,1) 1.25s both; }}
  @keyframes rise {{ from {{ opacity:0; transform:translateY(9px) }} to {{ opacity:1; transform:none }} }}
  @keyframes grow {{ from {{ opacity:0; stroke-dashoffset:120 }} to {{ opacity:1; stroke-dashoffset:0 }} }}

  @media (prefers-reduced-motion: reduce) {{
    .d, .name, .kicker, .ln, .pill, .rule {{ opacity:1 !important; animation:none !important; }}
  }}
</style>

<rect width="{W}" height="{H}" rx="12" fill="{bg}"/>
<path d="M12 0h{Wm24}a12 12 0 0 1 12 12v{BARm12}H0V12A12 12 0 0 1 12 0z" fill="{panel}"/>
<line x1="0" y1="{BAR}" x2="{W}" y2="{BAR}" stroke="{stroke}"/>
<circle cx="24" cy="{barmid}" r="5.5" fill="#FF5F57"/>
<circle cx="44" cy="{barmid}" r="5.5" fill="#FEBC2E"/>
<circle cx="64" cy="{barmid}" r="5.5" fill="#28C840"/>
<text class="bar" x="{halfW}" y="{bartext}" text-anchor="middle">{HANDLE}@github ~ $ ./profile.sh</text>

<g transform="translate({px:.1f} {py:.1f})" shape-rendering="crispEdges">
{portrait}
</g>

<text class="kicker" x="{cx}" y="176">PROFILE</text>
<text class="name" x="{cx}" y="230">{NAME}</text>
<line class="rule" x1="{rule_x1}" y1="256" x2="{rule_x2}" y2="256" stroke-dasharray="120"/>
{text_rows}
<text class="pill" x="{cx}" y="{pill_y}">@{HANDLE}</text>

<rect x=".5" y=".5" width="{Wm1}" height="{Hm1}" rx="12" fill="none" stroke="{stroke}"/>
</svg>
'''


def main() -> None:
    ASSETS.mkdir(exist_ok=True)
    for theme in THEMES:
        svg = build(theme)
        out = ASSETS / ("banner-%s.svg" % theme)
        out.write_text(svg, encoding="utf-8")
        print("ok: %s  (%.0f KB)" % (out.relative_to(ROOT), len(svg) / 1024))


if __name__ == "__main__":
    main()
