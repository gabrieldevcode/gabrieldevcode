"""As tres figuras entre as quais o enxame de pontos se transforma.

Eletronica -> Software -> Inteligencia, que e a mesma frase que fecha o README.
Sao desenhadas como bitmap e depois amostradas em pontos, em vez de tracadas a
mao em SVG: assim a densidade de pontos fica uniforme, que e o que faz a
transicao parecer um enxame e nao um contorno.
"""
from __future__ import annotations

import numpy as np
from PIL import Image, ImageDraw

SIZE = 420          # resolucao do bitmap de cada figura


def _canvas():
    im = Image.new("L", (SIZE, SIZE), 0)
    return im, ImageDraw.Draw(im)


def chip() -> Image.Image:
    """Microcontrolador: corpo, nucleo e pinos. A eletronica."""
    im, d = _canvas()
    s = SIZE
    body = (s * 0.24, s * 0.24, s * 0.76, s * 0.76)
    d.rounded_rectangle(body, radius=s * 0.045, outline=255, width=int(s * 0.035))
    core = (s * 0.38, s * 0.38, s * 0.62, s * 0.62)
    d.rounded_rectangle(core, radius=s * 0.02, outline=255, width=int(s * 0.028))

    pin_w = int(s * 0.028)
    for i in range(4):
        t = 0.34 + i * 0.11
        # cima e baixo
        d.line([(s * t, s * 0.13), (s * t, s * 0.24)], fill=255, width=pin_w)
        d.line([(s * t, s * 0.76), (s * t, s * 0.87)], fill=255, width=pin_w)
        # esquerda e direita
        d.line([(s * 0.13, s * t), (s * 0.24, s * t)], fill=255, width=pin_w)
        d.line([(s * 0.76, s * t), (s * 0.87, s * t)], fill=255, width=pin_w)
    return im


def code() -> Image.Image:
    """O glifo </>. O software."""
    im, d = _canvas()
    s = SIZE
    w = int(s * 0.05)
    # <
    d.line([(s * 0.34, s * 0.30), (s * 0.16, s * 0.50), (s * 0.34, s * 0.70)],
           fill=255, width=w, joint="curve")
    # >
    d.line([(s * 0.66, s * 0.30), (s * 0.84, s * 0.50), (s * 0.66, s * 0.70)],
           fill=255, width=w, joint="curve")
    # /
    d.line([(s * 0.58, s * 0.22), (s * 0.42, s * 0.78)], fill=255, width=w)
    return im


def neural() -> Image.Image:
    """Rede de tres camadas. A inteligencia.

    Os nos sao aneis grossos e as ligacoes sao finas de proposito: a amostragem
    e proporcional a area, entao no com pouca area vira um emaranhado de linhas
    em vez de uma rede.
    """
    im, d = _canvas()
    s = SIZE
    layers = [
        [(0.20, 0.28), (0.20, 0.50), (0.20, 0.72)],
        [(0.50, 0.22), (0.50, 0.41), (0.50, 0.59), (0.50, 0.78)],
        [(0.80, 0.36), (0.80, 0.64)],
    ]
    # so as duas ligacoes mais curtas por no: todas contra todas vira malha
    for a, b in zip(layers, layers[1:]):
        for p in a:
            for q in sorted(b, key=lambda q: abs(q[1] - p[1]))[:2]:
                d.line([(s * p[0], s * p[1]), (s * q[0], s * q[1])],
                       fill=255, width=max(2, int(s * 0.009)))
    r = s * 0.062
    for layer in layers:
        for p in layer:
            cx, cy = s * p[0], s * p[1]
            d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=255,
                      width=int(s * 0.034))
    return im


def sample(img: Image.Image, n: int, seed: int, span: float,
           cx: float, cy: float) -> np.ndarray:
    """Escolhe n pontos dentro da figura, ja no sistema de coordenadas do SVG.

    Os candidatos sao embaralhados e depois filtrados por distancia minima, o
    que aproxima um ruido azul: sem isso os pontos se amontoam e a figura fica
    com manchas.
    """
    ys, xs = np.nonzero(np.asarray(img) > 96)
    rnd = np.random.default_rng(seed)
    order = rnd.permutation(len(xs))
    xs, ys = xs[order], ys[order]

    scale = span / SIZE
    px = (xs - SIZE / 2) * scale + cx
    py = (ys - SIZE / 2) * scale + cy

    # grade de ocupacao: um ponto por celula, o que espalha sem custo alto
    cell = span / np.sqrt(n * 1.9)
    taken = set()
    keep = []
    for i in range(len(px)):
        key = (int(px[i] / cell), int(py[i] / cell))
        if key in taken:
            continue
        taken.add(key)
        keep.append(i)
        if len(keep) == n:
            break
    if len(keep) < n:                       # figura fina demais: completa sorteando
        extra = rnd.choice(len(px), n - len(keep))
        keep += list(extra)
    idx = np.array(keep[:n])
    return np.stack([px[idx], py[idx]], axis=1)


SHAPES = [chip, code, neural]
