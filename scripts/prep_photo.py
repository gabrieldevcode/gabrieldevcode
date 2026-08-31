"""Prepara a foto de origem para o retrato pontilhado.

1. Recorta cabeca + ombros.
2. Remove o fundo com rembg (mascara do sujeito).
3. Aplica CLAHE para dar relevo real ao rosto (foto plana vira borrao ao ser
   pontilhada).
4. Grava dois arquivos em build/:
     prepped-gray.png  -> imagem em tons de cinza ja com contraste
     prepped-mask.png  -> mascara do sujeito (255 = sujeito)

Uso:  python scripts/prep_photo.py [source-photo.jpg]
"""
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageOps

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "build"

# Recorte cabeca+ombros em coordenadas da foto original (esquerda, topo, direita, base).
CROP = (470, 250, 1760, 1720)
GRID_W, GRID_H = 300, 340


def main(src: str = "source-photo.jpg") -> None:
    BUILD.mkdir(exist_ok=True)
    img = Image.open(ROOT / src).convert("RGB").crop(CROP)

    # --- mascara do sujeito -------------------------------------------------
    from rembg import remove

    cut = remove(img)  # RGBA
    mask = np.array(cut.split()[-1])
    mask = (mask > 128).astype(np.uint8) * 255
    # fecha buracos e mantem apenas o maior componente
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
    n, lab, stats, _ = cv2.connectedComponentsWithStats(mask, 8)
    if n > 1:
        keep = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
        mask = np.where(lab == keep, 255, 0).astype(np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))

    # --- tons de cinza com contraste local ---------------------------------
    gray = np.array(ImageOps.grayscale(img))
    clahe = cv2.createCLAHE(clipLimit=2.1, tileGridSize=(8, 8))
    gray = clahe.apply(gray)

    g = Image.fromarray(gray)
    g = ImageOps.autocontrast(g, cutoff=1)
    g = ImageEnhance.Contrast(g).enhance(1.22)
    g = g.filter(ImageFilter.UnsharpMask(radius=3, percent=140, threshold=2))

    g = g.resize((GRID_W, GRID_H), Image.LANCZOS)
    m = Image.fromarray(mask).resize((GRID_W, GRID_H), Image.LANCZOS)

    g.save(BUILD / "prepped-gray.png")
    m.save(BUILD / "prepped-mask.png")
    cov = (np.array(m) > 128).mean()
    print(f"ok: build/prepped-gray.png  build/prepped-mask.png  (sujeito ocupa {cov:.1%})")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "source-photo.jpg")
