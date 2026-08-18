# -*- coding: utf-8 -*-
"""Parsuje changelog Claude Code + daty z npm -> data/releases.json

Zrodla sa zdalne (GitHub + rejestr npm) z kopia w .cache. Gdy siec padnie,
schodzimy do kopii, a w ostatecznosci do lokalnego cache Claude Code na dysku.
Dzieki temu ten sam kod dziala na Windowsie i w kontenerze automation.

Uruchamiane samodzielnie; build.py korzysta z tego modulu.
"""
import json
import os
import re
import sys
from datetime import date, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fetch_sources  # noqa: E402

CACHE_DIR = os.path.join(os.path.dirname(HERE), ".cache")
LOCAL_CLAUDE_CACHE = os.path.join(os.path.expanduser("~"), ".claude", "cache", "changelog.md")
SEED_TIMES = os.path.join(HERE, "data", "npm_times.json")
OUT = os.path.join(HERE, "data", "releases.json")


def vkey(v):
    parts = re.split(r"[.\-]", v)
    out = []
    for p in parts:
        out.append(int(p) if p.isdigit() else 0)
    while len(out) < 3:
        out.append(0)
    return tuple(out[:3])


def changelog_text(offline=False):
    """Tresc changelogu: siec -> kopia w .cache -> lokalny cache Claude Code."""
    if not offline:
        try:
            return fetch_sources.fetch_changelog(CACHE_DIR)
        except Exception as e:
            print("uwaga: pobranie changelogu nie powiodlo sie (%s), schodze do kopii" % e,
                  file=sys.stderr)
    for path in (os.path.join(CACHE_DIR, fetch_sources.CHANGELOG_FILE), LOCAL_CLAUDE_CACHE):
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
    raise SystemExit("Brak changelogu: nie ma sieci ani zadnej kopii na dysku")


def npm_times(offline=False):
    """Mapa wersja -> data: siec -> kopia w .cache -> zalazek w repo."""
    if not offline:
        try:
            return fetch_sources.fetch_npm_times(CACHE_DIR)
        except Exception as e:
            print("uwaga: pobranie dat z npm nie powiodlo sie (%s), schodze do kopii" % e,
                  file=sys.stderr)
    for path in (os.path.join(CACHE_DIR, fetch_sources.NPM_FILE), SEED_TIMES):
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    raise SystemExit("Brak dat wydan: nie ma sieci ani zadnej kopii na dysku")


def parse_changelog(text):
    """-> [{'version': str, 'entries': [str]}] w kolejnosci pliku (najnowsze pierwsze)"""
    lines = text.splitlines()

    releases = []
    cur = None
    buf = None
    for line in lines:
        m = re.match(r"^##\s+(?:v)?([0-9][0-9A-Za-z.\-]*)\s*$", line)
        if m:
            if cur:
                if buf:
                    cur["entries"].append(" ".join(buf).strip())
                releases.append(cur)
            cur = {"version": m.group(1), "entries": []}
            buf = None
            continue
        if cur is None:
            continue
        b = re.match(r"^\s*[-*]\s+(.*)$", line)
        if b:
            if buf:
                cur["entries"].append(" ".join(buf).strip())
            buf = [b.group(1).strip()]
        elif line.strip() == "":
            if buf:
                cur["entries"].append(" ".join(buf).strip())
                buf = None
        else:
            # kontynuacja zawinietego punktu
            if buf is not None:
                buf.append(line.strip())
    if cur:
        if buf:
            cur["entries"].append(" ".join(buf).strip())
        releases.append(cur)
    return releases


def attach_dates(releases, times):
    """Dokleja daty z npm; brakujace interpoluje z sasiadow (changelog posortowany malejaco)."""
    for r in releases:
        r["date"] = times.get(r["version"])
        r["date_exact"] = r["date"] is not None

    # interpolacja: idziemy od najstarszych (koniec listy) w gore
    n = len(releases)
    for i in range(n - 1, -1, -1):
        if releases[i]["date"]:
            continue
        prev_d = None  # starsze wydanie (nizej w liscie)
        for j in range(i + 1, n):
            if releases[j]["date"]:
                prev_d = date.fromisoformat(releases[j]["date"])
                break
        next_d = None  # nowsze wydanie (wyzej w liscie)
        for j in range(i - 1, -1, -1):
            if releases[j]["date"]:
                next_d = date.fromisoformat(releases[j]["date"])
                break
        if prev_d and next_d:
            guess = prev_d + (next_d - prev_d) / 2
        elif prev_d:
            guess = prev_d + timedelta(days=1)
        elif next_d:
            guess = next_d - timedelta(days=1)
        else:
            guess = date(2025, 2, 24)
        releases[i]["date"] = guess.isoformat()

    return releases


def load(offline=False):
    rel = attach_dates(parse_changelog(changelog_text(offline)), npm_times(offline))
    # chronologicznie rosnaco: data, potem wersja
    rel.sort(key=lambda r: (r["date"], vkey(r["version"])))
    return rel


if __name__ == "__main__":
    rel = load()
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(rel, f, ensure_ascii=False, indent=1)
    total = sum(len(r["entries"]) for r in rel)
    approx = sum(1 for r in rel if not r["date_exact"])
    print("wydan: %d | wpisow: %d | dat szacowanych: %d" % (len(rel), total, approx))
    print("zakres: %s -> %s" % (rel[0]["date"], rel[-1]["date"]))
    print("pierwsze: %s  ostatnie: %s" % (rel[0]["version"], rel[-1]["version"]))
