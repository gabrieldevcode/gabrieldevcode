"""Gera o banner animado (assets/banner-dark.svg e banner-light.svg).

Duas camadas independentes, porque qualidade de retrato e movimento por ponto
sao incompativeis numa camada so:

  1. RETRATO - dithering Floyd-Steinberg 1-bit, milhares de sequencias de pontos
     desenhadas como <path> (nunca glifos de fonte, que borram abaixo de 2px).
     Denso demais para animar ponto a ponto, entao e agrupado em faixas que
     derivam juntas.
  2. ENXAME - ~700 pontos que se transformam entre chip, </> e rede neural.
     Poucos o bastante para cada um ter a sua propria trajetoria.

A entrada revela o retrato em grupos espalhados por todo o quadro ao mesmo
tempo, nunca em varredura. Depois o loop dissolve o retrato, mostra as tres
figuras e traz o retrato de volta.

Uso:  python scripts/make_portrait_svg.py
"""
from __future__ import annotations

import random
from pathlib import Path

import numpy as np
from PIL import Image
from scipy.optimize import linear_sum_assignment

import shapes
from theme import MONO, THEMES, W

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "build"
ASSETS = ROOT / "assets"

GRID_W, GRID_H = 258, 292
DOT = 1.36
BANDS = 56           # faixas de deriva do retrato
SUBS = 13            # sub-caminhos por faixa, cada um com o seu atraso de entrada
CHUNK = 4            # quebra sequencias longas para a revelacao nao virar listra

TRAVELLERS = 700
SHAPE_SPAN = 322     # lado que cada figura ocupa, em unidades SVG

H = 500
BAR = 40
LOOP = 16.0          # duracao do ciclo
LOOP_BEGIN = 2.7     # so comeca depois que a entrada terminou

HANDLE = "gabrieldevcode"
NAME = "GABRIEL BARRETO"
LINES = [
    "Engenharia Eletrônica e de Computação · UFRJ",
    "Sistemas embarcados · IA aplicada · Automação",
    "Rio de Janeiro, Brasil",
]

# Linha do tempo do ciclo, em fracao da duracao. Os intervalos sao propositalmente
# desiguais: com quadros igualmente espacados toda fase dura o mesmo tempo e
# nenhuma figura chega a assentar.
KT = [0, 0.2125, 0.2875, 0.4125, 0.475, 0.6, 0.6625, 0.7875, 0.875, 0.90, 1]
#     0s  3.4s    4.6s    6.6s    7.6s  9.6s 10.6s   12.6s   14.0s  14.4s 16s
#     retrato --------|   chip -----|   </> ----|   rede ------|   volta -----


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
    return "".join(
        "M%s %sh%sv%sh-%sz" % (round(x * DOT, 2), round(y * DOT, 2),
                               round(n * DOT, 2), DOT, round(n * DOT, 2))
        for x, y, n in rs
    )


def ink_map(theme: dict):
    gray = np.asarray(Image.open(BUILD / "prepped-gray.png").resize(
        (GRID_W, GRID_H), Image.LANCZOS), dtype=np.float64) / 255.0
    mask = np.asarray(Image.open(BUILD / "prepped-mask.png").resize(
        (GRID_W, GRID_H), Image.LANCZOS)) > 128

    if theme["name"] == "light":
        # tinta escura desenha as partes escuras; o gamma < 1 puxa os meios-tons
        # para cima, senao o rosto some no papel
        ink = np.power(1.0 - gray, 0.82)
    else:
        # pontos claros desenham a luz do rosto. o piso mantem o polo preto como
        # silhueta; o teto segura textura nas altas luzes
        ink = 0.24 + (0.93 - 0.24) * np.power(gray, 1.08)
    ink = np.clip(ink, 0.0, 1.0)
    ink[~mask] = 0.0

    fade = np.ones(GRID_H)                  # dissolve o pe do busto
    fade[-30:] = np.linspace(1.0, 0.12, 30)
    ink *= fade[:, None]
    return ink, mask


def swarm_paths(cx: float, cy: float) -> list:
    """Trajetorias do enxame: uma nuvem por figura, ja pareadas ponto a ponto."""
    clouds = [
        shapes.sample(fn(), TRAVELLERS, seed=11 + i, span=SHAPE_SPAN, cx=cx, cy=cy)
        for i, fn in enumerate(shapes.SHAPES)
    ]
    # Cada ponto vai para a posicao mais barata na figura seguinte (transporte
    # otimo). Sem isso as trajetorias se cruzam em massa e a transicao vira ruido.
    ordered = [clouds[0]]
    for nxt in clouds[1:]:
        cost = ((ordered[-1][:, None, :] - nxt[None, :, :]) ** 2).sum(-1)
        _, col = linear_sum_assignment(cost)
        ordered.append(nxt[col])
    return ordered


def build(theme_name: str) -> str:
    t = THEMES[theme_name]
    ink, _ = ink_map(t)
    rs = runs(dither(ink))

    # sequencias longas viram pedacos de 4: uma area solida entrando inteira
    # transforma a revelacao em listras horizontais
    pieces = []
    for x, y, n in rs:
        for off in range(0, n, CHUNK):
            pieces.append((x + off, y, min(CHUNK, n - off)))

    # --- geometria -----------------------------------------------------------
    pw, ph = GRID_W * DOT, GRID_H * DOT
    fw, fh = 372, 418
    fx, fy = 26, BAR + 16
    px = fx + (fw - pw) / 2
    py = fy + (fh - ph) / 2
    cx_frame, cy_frame = fx + fw / 2, fy + fh / 2
    tx = fx + fw + 34
    cx = tx + (W - 26 - tx) / 2

    # --- faixas de deriva ----------------------------------------------------
    # A deriva e funcao linear da posicao, entao quantizar direto recria uma
    # grade quadrada e a dissolucao sai em blocos. O ruido por peca quebra isso.
    rnd = random.Random(7)
    npr = np.random.default_rng(7)
    axis = np.array([p[0] * DOT + p[1] * DOT * 0.6 for p in pieces])
    axis = axis + npr.normal(0, 5.5, len(axis))
    order = np.argsort(axis)
    band_of = np.empty(len(pieces), int)
    band_of[order] = (np.arange(len(pieces)) * BANDS) // len(pieces)

    groups = [[[] for _ in range(SUBS)] for _ in range(BANDS)]
    for i, p in enumerate(pieces):
        groups[band_of[i]][rnd.randrange(SUBS)].append(p)

    kt = ";".join(str(k) for k in KT)
    spl = ";".join([".4 0 .2 1"] * (len(KT) - 1))

    layers = []
    for b, subs in enumerate(groups):
        # cada faixa desliza na direcao do centro da moldura, onde as figuras
        # nascem, e depois volta
        frac = (b + 0.5) / BANDS - 0.5
        dx, dy = frac * 150, frac * 46
        inner = [
            '<path class="d" style="animation-delay:%.2fs" d="%s"/>'
            % (rnd.uniform(0.0, 1.35), path_for(sub))
            for sub in subs if sub
        ]
        if not inner:
            continue
        vals = ";".join(["0 0", "0 0"] + ["%.1f %.1f" % (dx, dy)] * 7 + ["0 0", "0 0"])
        layers.append(
            '<g><animateTransform attributeName="transform" type="translate" '
            'dur="%ss" begin="%ss" repeatCount="indefinite" calcMode="spline" '
            'keyTimes="%s" keySplines="%s" values="%s"/>%s</g>'
            % (LOOP, LOOP_BEGIN, kt, spl, vals, "".join(inner))
        )

    # --- enxame --------------------------------------------------------------
    a, b_, c = swarm_paths(cx_frame, cy_frame)
    spl2 = ";".join([".45 0 .2 1"] * (len(KT) - 1))
    dots = []
    for i in range(TRAVELLERS):
        seq = [a[i], a[i], a[i], a[i], b_[i], b_[i], c[i], c[i], c[i], a[i], a[i]]
        dots.append(
            '<circle r="1.15"><animateTransform attributeName="transform" '
            'type="translate" dur="%ss" begin="%ss" repeatCount="indefinite" '
            'calcMode="spline" keyTimes="%s" keySplines="%s" values="%s"/></circle>'
            % (LOOP, LOOP_BEGIN, kt, spl2,
               ";".join("%.1f %.1f" % (p[0], p[1]) for p in seq))
        )

    text_rows = "\n".join(
        '<text class="ln" x="%.0f" y="%d" style="animation-delay:%.2fs">%s</text>'
        % (cx, 250 + i * 30, 1.45 + i * 0.22, v)
        for i, v in enumerate(LINES)
    )

    return TEMPLATE.format(
        W=W, H=H, BAR=BAR, NAME=NAME, HANDLE=HANDLE, MONO=MONO,
        bg=t["bg"], panel=t["panel2"], stroke=t["stroke"], chrome=t["chrome"],
        ink=t["ink"], text=t["text"], muted=t["muted"], accent=t["accent"],
        Wm1=W - 1, Hm1=H - 1, Wm24=W - 24, BARm12=BAR - 12,
        barmid=BAR / 2, bartext=BAR / 2 + 4.5, halfW=W / 2,
        fx=fx, fy=fy, brk=34, fx2=fx + fw, fy2=fy + fh,
        px=px, py=py, cx=round(cx), layers="\n".join(layers), dots="\n".join(dots),
        text_rows=text_rows, kt=kt, LOOP=LOOP, BEGIN=LOOP_BEGIN,
        # opacidade e igual em todas as faixas, entao vai uma vez so no pai
        portrait_op="1;1;0;0;0;0;0;0;0;1;1",
        swarm_op="0;0;1;1;1;1;1;1;0;0;0",
        rule_x1=round(cx - 62), rule_x2=round(cx + 62),
        pill_y=250 + len(LINES) * 30 + 28,
    )


TEMPLATE = '''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{NAME}">
<title>{NAME} - {HANDLE}</title>
<style>
  text {{ font-family: {MONO}; }}
  .d {{ fill:{ink}; opacity:0; animation: reveal 1.2s ease-out both; }}
  @keyframes reveal {{ from {{ opacity:0 }} to {{ opacity:1 }} }}

  .bar   {{ fill:{muted}; font-size:13px; letter-spacing:.6px; }}
  .tag   {{ fill:{chrome}; font-size:9.5px; letter-spacing:2.6px; opacity:.75; }}
  .name  {{ fill:{text}; font-size:42px; font-weight:700; letter-spacing:3.5px;
            text-anchor:middle; opacity:0; animation: rise .9s cubic-bezier(.2,.7,.3,1) .9s both; }}
  .kicker{{ fill:{chrome}; font-size:12.5px; letter-spacing:5px; text-anchor:middle;
            opacity:0; animation: rise .8s ease-out .7s both; }}
  .ln    {{ fill:{muted}; font-size:14.5px; letter-spacing:.3px; text-anchor:middle;
            opacity:0; animation: rise .7s ease-out both; }}
  .pill  {{ fill:{accent}; font-size:13.5px; letter-spacing:1.2px; text-anchor:middle;
            opacity:0; animation: rise .7s ease-out 2.25s both; }}
  .rule  {{ stroke:{chrome}; stroke-width:2; opacity:0;
            animation: grow .8s cubic-bezier(.2,.7,.3,1) 1.2s both; }}
  @keyframes rise {{ from {{ opacity:0; transform:translateY(9px) }} to {{ opacity:1; transform:none }} }}
  @keyframes grow {{ from {{ opacity:0; stroke-dashoffset:124 }} to {{ opacity:1; stroke-dashoffset:0 }} }}

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
<text class="bar" x="{halfW}" y="{bartext}" text-anchor="middle">{HANDLE}@github ~ $ ./profile.sh --live</text>

<!-- moldura do retrato: so os cantos, para nao competir com os pontos -->
<g stroke="{chrome}" stroke-width="1.2" fill="none" opacity=".45">
  <path d="M{fx} {fy}h{brk}M{fx} {fy}v{brk}M{fx2} {fy}h-{brk}M{fx2} {fy}v{brk}"/>
  <path d="M{fx} {fy2}h{brk}M{fx} {fy2}v-{brk}M{fx2} {fy2}h-{brk}M{fx2} {fy2}v-{brk}"/>
</g>
<text class="tag" x="{fx}" y="{fy}" transform="translate(2 -8)">VISUAL.MAP</text>

<g transform="translate({px:.1f} {py:.1f})" shape-rendering="crispEdges">
  <animate attributeName="opacity" dur="{LOOP}s" begin="{BEGIN}s" repeatCount="indefinite"
           keyTimes="{kt}" values="{portrait_op}"/>
{layers}
</g>

<g fill="{ink}" opacity="0">
  <animate attributeName="opacity" dur="{LOOP}s" begin="{BEGIN}s" repeatCount="indefinite"
           keyTimes="{kt}" values="{swarm_op}"/>
{dots}
</g>

<text class="kicker" x="{cx}" y="140">PROFILE</text>
<text class="name" x="{cx}" y="196">{NAME}</text>
<line class="rule" x1="{rule_x1}" y1="222" x2="{rule_x2}" y2="222" stroke-dasharray="124"/>
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
        print("ok: %s  (%.0f KB)" % (out.relative_to(ROOT), len(svg.encode()) / 1024))


if __name__ == "__main__":
    main()
