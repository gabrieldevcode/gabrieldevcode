"""Coleta os numeros do perfil e o volume por linguagem -> data/stats.json.

Sem servico de terceiros: fala direto com a API publica do GitHub. Se existir um
token no ambiente (GH_TOKEN ou GITHUB_TOKEN) ele e usado apenas para levantar o
limite de requisicoes; com um PAT pessoal de escopo `repo` os repositorios
privados tambem entram na contagem de linguagens.

Uso:  python scripts/fetch_stats.py [usuario]
"""
from __future__ import annotations

import json
import os
import sys
from datetime import date
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
USER = "gabrieldevcode"
API = "https://api.github.com"

# Linguagens que nao dizem nada sobre o que a pessoa constroi.
IGNORE = {"Makefile", "Dockerfile", "Shell", "Batchfile", "PowerShell", "Procfile"}

# Repos que distorcem a conta: templates de site e rascunhos. O `Site` sozinho
# tem 1,4 MB de CSS de template e enterraria tudo que foi escrito de fato.
IGNORE_REPOS = {"Site", "site-tenis", "teste"}


def session() -> requests.Session:
    s = requests.Session()
    s.headers["Accept"] = "application/vnd.github+json"
    s.headers["User-Agent"] = "profile-readme-bot"
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if token:
        s.headers["Authorization"] = "Bearer %s" % token
    return s


def all_repos(s: requests.Session, user: str) -> list:
    """Repos do usuario. Com um PAT pessoal /user/repos traz tambem os privados."""
    for url, params in (
        ("%s/user/repos" % API, {"per_page": 100, "affiliation": "owner"}),
        ("%s/users/%s/repos" % (API, user), {"per_page": 100, "type": "owner"}),
    ):
        repos, page = [], 1
        while True:
            r = s.get(url, params=dict(params, page=page), timeout=30)
            if r.status_code != 200:
                break
            batch = r.json()
            repos += batch
            if len(batch) < 100:
                break
            page += 1
        # /user/repos so responde com um PAT pessoal; senao caimos no endpoint publico
        owned = [r for r in repos if r.get("owner", {}).get("login") == user]
        if owned:
            return owned
    raise SystemExit("nao consegui listar os repositorios de %s" % user)


def main() -> None:
    user = sys.argv[1] if len(sys.argv) > 1 else USER
    s = session()

    me = s.get("%s/users/%s" % (API, user), timeout=30)
    me.raise_for_status()
    me = me.json()

    repos = [r for r in all_repos(s, user)
             if not r.get("fork") and r["name"] not in IGNORE_REPOS]

    # Peso por repositorio, nao por bytes totais: cada repo distribui 1 ponto
    # entre as suas linguagens. Somar bytes faria um unico projeto grande
    # decidir sozinho o grafico inteiro.
    langs: dict = {}
    repo_count: dict = {}
    counted = 0
    stars = 0
    for r in repos:
        stars += r.get("stargazers_count", 0)
        lr = s.get(r["languages_url"], timeout=30)
        if lr.status_code != 200:
            continue
        sizes = {k: v for k, v in lr.json().items() if k not in IGNORE}
        total_r = sum(sizes.values())
        if not total_r:
            continue
        counted += 1
        for name, size in sizes.items():
            langs[name] = langs.get(name, 0) + size / total_r
            repo_count[name] = repo_count.get(name, 0) + 1

    total = sum(langs.values()) or 1
    ranked = sorted(langs.items(), key=lambda kv: -kv[1])
    private = sum(1 for r in repos if r.get("private"))

    data = {
        "user": user,
        "generated_at": date.today().isoformat(),
        "counts": {
            "repos": len(repos),
            "repos_with_code": counted,
            "public_repos": len(repos) - private,
            "private_repos": private,
            "stars": stars,
            "followers": me.get("followers", 0),
            "since": me.get("created_at", "")[:4],
        },
        "languages": [
            {"name": n, "share": round(100 * w / total, 2), "repos": repo_count[n]}
            for n, w in ranked
        ],
        "metric": "media das distribuicoes por repositorio",
    }

    out = ROOT / "data" / "stats.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(data, indent=1), encoding="utf-8")
    top = ", ".join("%s %.0f%%" % (l["name"], l["share"]) for l in data["languages"][:5])
    print("ok: %s" % out.relative_to(ROOT))
    print("   %s repos (%s privados) | %s estrelas | %s" % (
        len(repos), private, stars, top))


if __name__ == "__main__":
    main()
