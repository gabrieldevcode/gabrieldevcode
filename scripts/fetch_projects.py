"""Coleta os dados dos projetos em destaque -> data/projects.json.

O que e curado aqui (titulo, resumo e badges) fica no codigo de proposito: a
descricao do repositorio e longa demais para caber num card, e `topics` esta
vazio na maioria deles. O que e medido - linguagens, estrelas, ultimo push -
vem da API.

Uso:  python scripts/fetch_projects.py [usuario]
"""
from __future__ import annotations

import json
import os
import sys
from datetime import date, datetime, timezone
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
USER = "gabrieldevcode"
API = "https://api.github.com"

# ordem = ordem de exibicao no README
FEATURED = [
    # o resumo tem que caber em duas linhas de 36 caracteres no card
    dict(repo="synapsis", letter="S", title="Synapsis",
         blurb="Estudos por repetição espaçada no terminal, sem dependências.",
         badges=["Python", "CLI", "Algoritmos"]),
    dict(repo="claude-usage", letter="C", title="Claude Usage Stick",
         blurb="Medidor de uso da API portado para a CYD ESP32-2432S028.",
         badges=["C", "ESP32", "LVGL"]),
    dict(repo="Amigo_Rotineiro", letter="A", title="Amigo Rotineiro",
         blurb="Assistente com IA ligado ao Google Calendar, pelo terminal.",
         badges=["Python", "Gemini", "Calendar"]),
    dict(repo="Automacao_Dimob_2.0", letter="D", title="Automação DIMOB 2.0",
         blurb="Robô que preenche a DIMOB na Receita Federal sozinho.",
         badges=["Python", "RPA", "Visão"]),
    dict(repo="Automacao_Encaminhamento_Exame", letter="E", title="Encaminhamento ASO",
         blurb="LLM lê a mensagem do cliente e gera a guia médica em Word.",
         badges=["Python", "LLM", "docx"]),
    dict(repo="Automacao-Imposto-de-Renda", letter="I", title="Automação do IR",
         blurb="Preenche declarações de IR. Em produção num escritório.",
         badges=["Python", "RPA", "Produção"]),
]


def session() -> requests.Session:
    s = requests.Session()
    s.headers["Accept"] = "application/vnd.github+json"
    s.headers["User-Agent"] = "profile-readme-bot"
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if token:
        s.headers["Authorization"] = "Bearer %s" % token
    return s


def ago(iso: str) -> str:
    d = (datetime.now(timezone.utc) - datetime.fromisoformat(iso.replace("Z", "+00:00"))).days
    if d < 1:
        return "hoje"
    if d < 30:
        return "há %d dia%s" % (d, "s" if d > 1 else "")
    if d < 365:
        m = d // 30
        return "há %d meses" % m if m > 1 else "há 1 mês"
    y = d // 365
    return "há %d ano%s" % (y, "s" if y > 1 else "")


def main() -> None:
    user = sys.argv[1] if len(sys.argv) > 1 else USER
    s = session()

    out = []
    for spec in FEATURED:
        r = s.get("%s/repos/%s/%s" % (API, user, spec["repo"]), timeout=30)
        if r.status_code != 200:
            print("aviso: %s indisponível (%s), pulando" % (spec["repo"], r.status_code))
            continue
        meta = r.json()

        lr = s.get(meta["languages_url"], timeout=30)
        sizes = lr.json() if lr.status_code == 200 else {}
        total = sum(sizes.values()) or 1
        langs = [{"name": n, "share": round(100 * b / total, 1)}
                 for n, b in sorted(sizes.items(), key=lambda kv: -kv[1])[:3]]

        out.append(dict(
            spec,
            url=meta["html_url"],
            stars=meta.get("stargazers_count", 0),
            updated=ago(meta["pushed_at"]),
            languages=langs,
        ))

    data = {"user": user, "generated_at": date.today().isoformat(), "projects": out}
    p = ROOT / "data" / "projects.json"
    p.parent.mkdir(exist_ok=True)
    p.write_text(json.dumps(data, indent=1, ensure_ascii=False), encoding="utf-8")
    print("ok: %s (%d projetos)" % (p.relative_to(ROOT), len(out)))


if __name__ == "__main__":
    main()
