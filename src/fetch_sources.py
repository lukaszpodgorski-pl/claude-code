# -*- coding: utf-8 -*-
"""Pobiera zrodla osi czasu: changelog z GitHuba i daty wydan z rejestru npm.

Oba zrodla sa publiczne, wiec automat nie zalezy od tego, czy ktos zaktualizowal
lokalna instalacje Claude Code. Kazde pobranie zostawia kopie w katalogu cache;
gdy siec padnie, czytamy kopie zamiast wywracac cala budowe.
"""
import json
import os
import urllib.request

CHANGELOG_URL = "https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md"
NPM_URL = "https://registry.npmjs.org/@anthropic-ai/claude-code"

CHANGELOG_FILE = "changelog.md"
NPM_FILE = "npm_times.json"

_UA = "claude-code-timeline (+https://lukaszpodgorski.pl/claude-code)"


def _get(url, timeout=30):
    """Surowe pobranie. Wydzielone, zeby testy mogly je podmienic."""
    req = urllib.request.Request(url, headers={"User-Agent": _UA})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def _write_atomic(path, text):
    """Zapis przez plik tymczasowy: przerwanie nie zostawia uszkodzonej kopii."""
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    os.replace(tmp, path)


def _cached(path):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return None


def fetch_changelog(cache_dir, url=CHANGELOG_URL):
    """Tekst changelogu. Przy bledzie sieci zwraca ostatnia kopie z cache."""
    os.makedirs(cache_dir, exist_ok=True)
    path = os.path.join(cache_dir, CHANGELOG_FILE)
    try:
        text = _get(url).decode("utf-8")
    except Exception:
        fallback = _cached(path)
        if fallback is None:
            raise
        return fallback
    _write_atomic(path, text)
    return text


def fetch_npm_times(cache_dir, url=NPM_URL):
    """Mapa wersja -> data publikacji (YYYY-MM-DD), bez kluczy sluzbowych rejestru."""
    os.makedirs(cache_dir, exist_ok=True)
    path = os.path.join(cache_dir, NPM_FILE)
    try:
        raw = json.loads(_get(url).decode("utf-8"))
    except Exception:
        fallback = _cached(path)
        if fallback is None:
            raise
        return json.loads(fallback)
    times = {v: t[:10] for v, t in raw.get("time", {}).items()
             if v not in ("created", "modified")}
    _write_atomic(path, json.dumps(times, ensure_ascii=False, indent=1, sort_keys=True))
    return times


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    cache = os.path.join(os.path.dirname(here), ".cache")
    ch = fetch_changelog(cache)
    tm = fetch_npm_times(cache)
    print("changelog: %d znakow | wersji w npm: %d" % (len(ch), len(tm)))
