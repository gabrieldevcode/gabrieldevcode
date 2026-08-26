#!/usr/bin/env python3
"""
scan_portrait.py — transforma uma foto num retrato "digitalizado" (SVG animado)
para usar no README de perfil do GitHub.

Uso:
    python tools/scan_portrait.py foto.jpg assets/scan.svg
    python tools/scan_portrait.py --demo assets/scan.svg      # gera silhueta placeholder

Saída: SVG autocontido, sem JavaScript, com animação CSS (scanline + fade dos blocos).
Funciona dentro de <img> no README do GitHub.
"""

import sys
import math

W_CELLS = 44          # colunas do mosaico
H_CELLS = 52          # linhas do mosaico
CELL = 7              # tamanho da célula em px
GAP = 1               # respiro entre células
PAD = 22

BG = "#070B10"
EDGE = "#1E2E3A"
RAMP = ["#0B141B", "#12303A", "#186B66", "#22A899", "#2DD4BF", "#7FF2E2"]
ACCENT = "#F5A524"


def load_matrix(path):
    from PIL import Image, ImageOps
    img = Image.open(path).convert("L")
    img = ImageOps.autocontrast(img, cutoff=2)
    img = ImageOps.fit(img, (W_CELLS, H_CELLS), method=Image.LANCZOS, centering=(0.5, 0.35))
    px = img.load()
    return [[px[x, y] / 255.0 for x in range(W_CELLS)] for y in range(H_CELLS)]


def demo_matrix():
    """Silhueta de busto gerada proceduralmente (placeholder até você rodar com a foto)."""
    m = [[0.0] * W_CELLS for _ in range(H_CELLS)]
    cx = W_CELLS / 2 - 0.5
    for y in range(H_CELLS):
        for x in range(W_CELLS):
            v = 0.0
            # cabeça (elipse)
            hy, hx = (y - 17) / 13.5, (x - cx) / 9.5
            d = hx * hx + hy * hy
            if d < 1.0:
                v = 0.55 + 0.45 * (1 - d) - 0.25 * abs(hx)
            # ombros
            sy = y - 36
            if sy > 0:
                half = 6 + sy * 2.3
                if abs(x - cx) < half:
                    v = max(v, 0.42 + 0.25 * (1 - abs(x - cx) / half) - 0.02 * sy)
            # pescoço
            if 29 <= y <= 37 and abs(x - cx) < 3.5:
                v = max(v, 0.5)
            v += 0.05 * math.sin(x * 0.9 + y * 0.5)
            m[y][x] = max(0.0, min(1.0, v))
    return m


def to_svg(m):
    w = PAD * 2 + W_CELLS * CELL
    h = PAD * 2 + H_CELLS * CELL + 34
    cells = []
    for y in range(H_CELLS):
        for x in range(W_CELLS):
            v = m[y][x]
            if v < 0.14:
                continue
            idx = min(len(RAMP) - 1, int(v * len(RAMP)))
            size = CELL - GAP if v > 0.45 else max(2, int((CELL - GAP) * 0.55))
            off = (CELL - GAP - size) / 2
            px = PAD + x * CELL + off
            py = PAD + y * CELL + off
            delay = round(y * 0.045 + x * 0.006, 3)
            cells.append(
                f'<rect x="{px:.1f}" y="{py:.1f}" width="{size}" height="{size}" rx="1" '
                f'fill="{RAMP[idx]}" class="c" style="animation-delay:{delay}s"/>'
            )
    body = "\n    ".join(cells)
    scan_h = H_CELLS * CELL + PAD
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="retrato digitalizado">
  <defs>
    <linearGradient id="beam" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#2DD4BF" stop-opacity="0"/>
      <stop offset="50%" stop-color="#2DD4BF" stop-opacity="0.35"/>
      <stop offset="100%" stop-color="#2DD4BF" stop-opacity="0"/>
    </linearGradient>
    <clipPath id="clip"><rect x="0" y="0" width="{w}" height="{h}" rx="10"/></clipPath>
    <style>
      .c {{ opacity:1; animation: reveal 6s ease-out infinite; }}
      @keyframes reveal {{ 0%{{opacity:0; transform:translateY(-2px)}} 12%{{opacity:1; transform:translateY(0)}} 88%{{opacity:1}} 100%{{opacity:.15}} }}
      .beam {{ animation: sweep 6s linear infinite; }}
      @keyframes sweep {{ 0%{{transform:translateY(-40px)}} 100%{{transform:translateY({scan_h}px)}} }}
      .blink {{ animation: bl 1.1s steps(1) infinite; }}
      @keyframes bl {{ 0%,55%{{opacity:1}} 56%,100%{{opacity:.2}} }}
      .mono {{ font-family:"SFMono-Regular","JetBrains Mono","Consolas",monospace; }}
    </style>
  </defs>
  <g clip-path="url(#clip)">
    <rect width="{w}" height="{h}" fill="{BG}"/>
    {body}
    <rect x="0" y="0" width="{w}" height="34" fill="url(#beam)" class="beam"/>
    <g class="mono" font-size="9" letter-spacing="2">
      <text x="{PAD}" y="{h - 14}" fill="#4C5C6B">SUBJECT_ID // GABRIEL</text>
      <text x="{w - PAD}" y="{h - 14}" fill="{ACCENT}" text-anchor="end" class="blink">SCAN OK</text>
    </g>
    <g fill="none" stroke="#2DD4BF" stroke-opacity="0.5" stroke-width="1.5">
      <path d="M10 26V10H26M{w-26} 10H{w-10}V26M10 {h-26}V{h-10}H26M{w-26} {h-10}H{w-10}V{h-26}"/>
    </g>
    <rect x="0.5" y="0.5" width="{w-1}" height="{h-1}" rx="10" fill="none" stroke="{EDGE}"/>
  </g>
</svg>
"""


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return 1
    if args[0] == "--demo":
        out = args[1] if len(args) > 1 else "assets/scan.svg"
        m = demo_matrix()
    else:
        src, out = args[0], (args[1] if len(args) > 1 else "assets/scan.svg")
        m = load_matrix(src)
    with open(out, "w", encoding="utf-8") as f:
        f.write(to_svg(m))
    print(f"gerado: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
