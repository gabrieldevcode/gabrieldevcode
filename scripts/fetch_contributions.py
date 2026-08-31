"""Baixa o calendario publico de contribuicoes e grava data/contributions.json.

Nao precisa de token nem da API GraphQL: o proprio perfil monta o calendario a
partir de https://github.com/users/<user>/contributions, que e HTML publico.

Uso:  python scripts/fetch_contributions.py [usuario]
"""
from __future__ import annotations

import json
import re
import sys
from datetime import date
from pathlib import Path

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
USER = "gabrieldevcode"
URL = "https://github.com/users/{user}/contributions"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; profile-readme-bot)",
    "X-Requested-With": "XMLHttpRequest",
}


def parse_count(text: str) -> int:
    """'12 contributions on March 3rd.' -> 12 ; 'No contributions...' -> 0."""
    m = re.search(r"([\d,]+)\s+contribution", text or "")
    return int(m.group(1).replace(",", "")) if m else 0


def fetch(user: str) -> dict:
    html = requests.get(URL.format(user=user), headers=HEADERS, timeout=30)
    html.raise_for_status()
    soup = BeautifulSoup(html.text, "html.parser")

    tips = {t.get("for"): t.get_text(strip=True) for t in soup.find_all("tool-tip")}

    days = []
    for cell in soup.select("td.ContributionCalendar-day"):
        iso = cell.get("data-date")
        if not iso:
            continue
        days.append({
            "date": iso,
            "level": int(cell.get("data-level") or 0),
            "count": parse_count(tips.get(cell.get("id"), "")),
        })
    days.sort(key=lambda d: d["date"])
    if not days:
        raise SystemExit("nenhum dia encontrado - o HTML do GitHub deve ter mudado")
    return {"user": user, "days": days}


def stats(days: list) -> dict:
    total = sum(d["count"] for d in days)
    best = max(days, key=lambda d: d["count"])

    longest = run = 0
    for d in days:
        run = run + 1 if d["count"] else 0
        longest = max(longest, run)

    # a streak atual ignora o dia de hoje ainda sem commit (o dia nao acabou)
    current = 0
    tail = list(days)
    if tail and tail[-1]["count"] == 0 and tail[-1]["date"] == date.today().isoformat():
        tail.pop()
    for d in reversed(tail):
        if d["count"] == 0:
            break
        current += 1

    active = sum(1 for d in days if d["count"])
    return {
        "total": total,
        "days_tracked": len(days),
        "active_days": active,
        "current_streak": current,
        "longest_streak": longest,
        "best_day": {"date": best["date"], "count": best["count"]},
        "first_date": days[0]["date"],
        "last_date": days[-1]["date"],
    }


def main() -> None:
    user = sys.argv[1] if len(sys.argv) > 1 else USER
    data = fetch(user)
    data["stats"] = stats(data["days"])
    data["generated_at"] = date.today().isoformat()

    out = ROOT / "data" / "contributions.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(data, indent=1), encoding="utf-8")

    s = data["stats"]
    print("ok: %s" % out.relative_to(ROOT))
    print("   %s contribuicoes | streak atual %s | maior streak %s | melhor dia %s (%s)"
          % (s["total"], s["current_streak"], s["longest_streak"],
             s["best_day"]["count"], s["best_day"]["date"]))


if __name__ == "__main__":
    main()
