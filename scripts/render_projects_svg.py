"""Desenha um card SVG por projeto em destaque.

Um arquivo por projeto, e nao um SVG unico com a grade inteira, por um motivo
so: link. O GitHub renderiza o SVG do README dentro de um <img>, e dentro de um
<img> nenhum <a> do SVG funciona. Com um arquivo por card da para embrulhar cada
um num link do proprio markdown, e ai o card inteiro fica clicavel.

Uso:  python scripts/render_projects_svg.py
"""
from __future__ import annotations

import json
from pathlib import Path

from theme import MONO, THEMES, lang_color

ROOT = Path(__file__).resolve().parents[1]

CW, CH = 490, 178       # duas colunas de 490 + 20 de gap = 1000
HEAD = 28
PAD = 18
DESC_CHARS = 36         # onde quebrar a linha do resumo
RING_R = 26


def wrap(text: str, width: int, lines: int) -> list:
    out, cur = [], ""
    for word in text.split():
        if len(cur) + len(word) + 1 > width:
            out.append(cur)
            cur = word
            if len(out) == lines:
                break
        else:
            cur = (cur + " " + word).strip()
    if len(out) < lines and cur:
        out.append(cur)
    if len(out) == lines and cur and out[-1] != cur:
        out[-1] = out[-1][:width - 1].rstrip() + "…"
    return out[:lines]


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def card(p: dict, user: str, theme_name: str, idx: int) -> str:
    t = THEMES[theme_name]
    gid = "g%d%s" % (idx, theme_name)

    # --- badges de tecnologia ------------------------------------------------
    badges, bx = [], PAD + 52
    for b in p["badges"]:
        w = 9 + len(b) * 6.6
        badges.append(
            '<g><rect x="%.1f" y="118" width="%.1f" height="19" rx="9.5" '
            'fill="none" stroke="%s" stroke-width="1" opacity=".55"/>'
            '<text class="bg" x="%.1f" y="131.5">%s</text></g>'
            % (bx, w, t["ink"], bx + w / 2, esc(b)))
        bx += w + 7

    # --- linguagens do repo --------------------------------------------------
    langs = []
    for i, l in enumerate(p["languages"]):
        y = 62 + i * 20
        langs.append(
            '<g><circle cx="308" cy="%.1f" r="3.6" fill="%s"/>'
            '<text class="lg" x="319" y="%.1f">%s %s%%</text></g>'
            % (y - 4, lang_color(l["name"], i, theme_name), y,
               esc(l["name"]), l["share"]))

    top = p["languages"][0]["share"] if p["languages"] else 0
    circ = 2 * 3.14159265 * RING_R
    dash = circ * top / 100.0

    desc = wrap(p["blurb"], DESC_CHARS, 2)
    desc_svg = "\n".join('<text class="ds" x="%d" y="%d">%s</text>'
                         % (PAD + 52, 84 + i * 17, esc(d))
                         for i, d in enumerate(desc))

    return TEMPLATE.format(
        CW=CW, CH=CH, MONO=MONO, gid=gid, PAD=PAD, HEAD=HEAD,
        bg=t["bg"], panel=t["panel"], panel2=t["panel2"], stroke=t["stroke"],
        chrome=t["chrome"], ink=t["ink"], accent=t["accent"],
        text=t["text"], muted=t["muted"], faint=t["faint"], empty=t["empty"],
        CWm1=CW - 1, CHm1=CH - 1, CWm=CW - PAD, head_w=CW - 25,
        repo=esc("%s/%s" % (user, p["repo"])), title=esc(p["title"]),
        letter=esc(p["letter"]), desc=desc_svg, badges="\n".join(badges),
        langs="\n".join(langs), stars=p["stars"], updated=esc(p["updated"]),
        ring_cx=CW - 58, ring_cy=96, RING_R=RING_R,
        circ="%.1f" % circ, dash="%.1f" % dash, top="%.0f" % top,
    )


TEMPLATE = '''<svg xmlns="http://www.w3.org/2000/svg" width="{CW}" height="{CH}" viewBox="0 0 {CW} {CH}" role="img" aria-label="{title}">
<title>{repo}</title>
<defs>
  <linearGradient id="{gid}" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="{chrome}"/>
    <stop offset="1" stop-color="{ink}"/>
  </linearGradient>
</defs>
<style>
  text {{ font-family: {MONO}; }}
  .rp {{ fill:{muted}; font-size:11px; }}
  .ti {{ fill:{text}; font-size:17px; font-weight:700; letter-spacing:.2px; }}
  .ds {{ fill:{muted}; font-size:11.5px; }}
  .bg {{ fill:{ink}; font-size:10px; text-anchor:middle; }}
  .lg {{ fill:{muted}; font-size:10.5px; }}
  .mt {{ fill:{faint}; font-size:10.5px; }}
  .pc {{ fill:{text}; font-size:15px; font-weight:700; text-anchor:middle; }}
  .il {{ fill:{text}; font-size:19px; font-weight:700; text-anchor:middle; }}

  .in {{ opacity:0; animation: fade .6s ease-out both; }}
  .a1 {{ animation-delay:.15s }} .a2 {{ animation-delay:.3s }}
  .a3 {{ animation-delay:.45s }} .a4 {{ animation-delay:.6s }}
  @keyframes fade {{ from {{ opacity:0; transform:translateY(8px) }} to {{ opacity:1; transform:none }} }}

  .rg {{ animation: sweep 1.3s cubic-bezier(.2,.8,.25,1) .5s both; }}
  @keyframes sweep {{ from {{ stroke-dasharray:0 {circ} }} to {{ stroke-dasharray:{dash} {circ} }} }}

  @media (prefers-reduced-motion: reduce) {{
    .in {{ opacity:1 !important; animation:none !important; }}
    .rg {{ animation:none !important; stroke-dasharray:{dash} {circ}; }}
  }}
</style>

<rect x=".5" y=".5" width="{CWm1}" height="{CHm1}" rx="12" fill="{panel}" stroke="{stroke}">
  <animate attributeName="stroke" values="{stroke};{chrome};{stroke}" dur="5s" repeatCount="indefinite"/>
</rect>
<path d="M12.5 .5h{head_w}a12 12 0 0 1 12 12V{HEAD}H.5V12.5A12 12 0 0 1 12.5 .5z" fill="{panel2}" opacity=".85"/>
<line x1="0" y1="{HEAD}" x2="{CW}" y2="{HEAD}" stroke="{stroke}"/>
<circle cx="{PAD}" cy="14.5" r="3.2" fill="{chrome}"/>
<text class="rp" x="30" y="18">{repo}</text>
<circle cx="{CWm}" cy="14.5" r="3.2" fill="{accent}">
  <animate attributeName="opacity" values="1;.25;1" dur="2.6s" repeatCount="indefinite"/>
</circle>

<g class="in a1">
  <rect x="{PAD}" y="48" width="40" height="40" rx="11" fill="url(#{gid})" opacity=".18"/>
  <rect x="{PAD}.5" y="48.5" width="39" height="39" rx="11" fill="none" stroke="url(#{gid})"/>
  <text class="il" x="38" y="74">{letter}</text>
</g>

<text class="ti in a1" x="70" y="64">{title}</text>
<g class="in a2">{desc}</g>
<g class="in a3">{badges}</g>

<g class="in a2">
  <path d="M0 0 3.1 6.3 10 7.3 5 12.2l1.2 6.9L0 15.8l-6.2 3.3L-5 12.2-10 7.3l6.9-1L0 0z"
        transform="translate({PAD}.5 152) scale(.62)" fill="{ink}"/>
  <text class="mt" x="32" y="157">{stars}</text>
  <text class="mt" x="52" y="157">atualizado {updated}</text>
</g>

<g class="in a2">{langs}</g>

<g class="in a3">
  <circle cx="{ring_cx}" cy="{ring_cy}" r="{RING_R}" fill="none" stroke="{empty}" stroke-width="7"/>
  <circle class="rg" cx="{ring_cx}" cy="{ring_cy}" r="{RING_R}" fill="none"
          stroke="url(#{gid})" stroke-width="7" stroke-linecap="round"
          transform="rotate(-90 {ring_cx} {ring_cy})"/>
  <text class="pc" x="{ring_cx}" y="{ring_cy}" dy="5">{top}%</text>
</g>
</svg>
'''


def main() -> None:
    data = json.loads((ROOT / "data" / "projects.json").read_text(encoding="utf-8"))
    out = ROOT / "assets" / "projects"
    out.mkdir(parents=True, exist_ok=True)
    for i, p in enumerate(data["projects"]):
        for theme in THEMES:
            f = out / ("%s-%s.svg" % (p["repo"], theme))
            f.write_text(card(p, data["user"], theme, i), encoding="utf-8")
    print("ok: %d cards em %s" % (len(data["projects"]) * 2, out.relative_to(ROOT)))


if __name__ == "__main__":
    main()
