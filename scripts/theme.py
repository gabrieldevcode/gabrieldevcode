"""Paleta unica usada por todos os geradores de asset do perfil.

Regra que vale a pena manter: o retrato tem um matiz (violeta) diferente do
cromo da interface (ciano). Se os dois forem da mesma cor, o rosto se dissolve
na propria moldura.
"""

W = 1000            # todos os assets tem a mesma largura, entao as bordas alinham

DARK = dict(
    name="dark",
    bg="#0A101F",
    panel="#0C1426",
    panel2="#0B1222",
    stroke="#1B2942",
    line="rgba(34,211,238,0.28)",
    chrome="#22D3EE",      # ciano: molduras, titulos, prompts
    ink="#A78BFA",         # violeta: o retrato
    accent="#10B981",      # verde: destaques pontuais
    warn="#F59E0B",
    text="#F8FAFC",
    muted="#94A3B8",
    faint="#475569",
    empty="#161B22",
)

LIGHT = dict(
    name="light",
    bg="#FFFFFF",
    panel="#F8FAFC",
    panel2="#F1F5F9",
    stroke="#CBD5E1",
    line="rgba(8,145,178,0.35)",
    chrome="#0891B2",
    ink="#7C3AED",
    accent="#059669",
    warn="#B45309",
    text="#0F172A",
    muted="#475569",
    faint="#94A3B8",
    empty="#EBEDF0",
)

THEMES = {"dark": DARK, "light": LIGHT}

MONO = ("ui-monospace,'SFMono-Regular','JetBrains Mono',Menlo,Consolas,"
        "'Liberation Mono',monospace")

# rampa do heatmap, do vazio ao mais forte
HEAT = {
    "dark": ["#161B22", "#164E63", "#0E7490", "#22D3EE", "#A5F3FC"],
    "light": ["#EBEDF0", "#CFFAFE", "#67E8F9", "#0891B2", "#0E5D73"],
}

# cores do linguist, com ajuste onde a cor original some no fundo
LANG_COLORS = {
    "Python": "#3572A5", "TypeScript": "#3178C6", "JavaScript": "#F1E05A",
    "C": "#8C97A3", "C++": "#F34B7D", "HTML": "#E34C26", "CSS": "#A78BFA",
    "PLpgSQL": "#22D3EE", "Java": "#B07219", "Go": "#00ADD8", "Rust": "#DEA584",
    "Dart": "#00B4AB", "Kotlin": "#A97BFF", "Swift": "#F05138", "Shell": "#89E051",
    "CMake": "#DA3434", "Jupyter Notebook": "#DA5B0B",
}
LANG_LIGHT_OVERRIDE = {"C": "#4A5561", "JavaScript": "#C9AE00", "CSS": "#7C3AED"}
LANG_FALLBACK = ["#22D3EE", "#A78BFA", "#10B981", "#F59E0B", "#F34B7D"]


def lang_color(name, i, theme):
    if theme == "light" and name in LANG_LIGHT_OVERRIDE:
        return LANG_LIGHT_OVERRIDE[name]
    return LANG_COLORS.get(name, LANG_FALLBACK[i % len(LANG_FALLBACK)])
