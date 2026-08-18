# -*- coding: utf-8 -*-
"""Tlumaczenie wpisow changelogu na polski przez Claude Code w trybie headless.

Model dostaje wsad ponumerowanych wpisow i oddaje obiekt JSON numer -> tlumaczenie.
Numeracja zamiast pelnych tekstow w odpowiedzi oszczedza tokeny i usuwa klase
bledow, w ktorej model odsyla lekko zmieniony oryginal jako klucz.

Pamiec tlumaczen jest zapisywana po kazdym wsadzie, wiec przerwanie dlugiego
przebiegu kosztuje najwyzej jeden wsad.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import threading
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import translations  # noqa: E402

MODEL = "sonnet"
BATCH = 40
TIMEOUT = 300

# Terminy, ktore w polskim tekscie technicznym funkcjonuja w oryginale albo maja
# utarta forme. Bez tego kolejne wsady rozjezdzaja sie terminologicznie.
GLOSSARY = """\
- nie tlumacz nazw wlasnych i identyfikatorow: Claude Code, MCP, SDK, API, CLI,
  Bedrock, Vertex, VS Code, JetBrains, nazw narzedzi (Bash, Grep, WebFetch),
  nazw komend (/model, /config), flag (--print), zmiennych (ANTHROPIC_API_KEY)
  i nazw plikow (CLAUDE.md, settings.json)
- utarte formy: hook -> hook, hooks -> hooki, skill -> skill, skills -> skille,
  plugin -> plugin, subagent -> subagent, sandbox -> sandbox, prompt -> prompt,
  token -> token, plan mode -> tryb planowania, thinking -> rozumowanie,
  checkpoint -> punkt kontrolny, statusline -> pasek stanu, transcript -> zapis rozmowy
- czasownik otwierajacy w formie bezosobowej dokonanej: Added -> Dodano,
  Fixed -> Poprawiono, Improved -> Ulepszono, Removed -> Usunieto,
  Changed -> Zmieniono, Reverted -> Cofnieto
- zachowaj znaczniki markdown z oryginalu (`kod`, **pogrubienie**)
- bez emoji, bez myslnika jako separatora zdania"""

PROMPT = """Przetlumacz na polski wpisy z changelogu Claude Code.

Zasady:
{glossary}

Zwroc WYLACZNIE obiekt JSON: klucz to numer wpisu jako tekst, wartosc to
tlumaczenie. Bez komentarza przed ani po, bez bloku kodu, wszystkie {n} pozycji.

Wpisy:
{items}"""

_lock = threading.Lock()


def build_prompt(texts):
    items = "\n".join('"%d": %s' % (i, json.dumps(t, ensure_ascii=False))
                      for i, t in enumerate(texts))
    return PROMPT.format(glossary=GLOSSARY, n=len(texts), items=items)


def _claude_exe():
    return shutil.which("claude") or "claude"


def _run_claude(prompt, model, timeout):
    """Jedno wywolanie headless. Wydzielone, zeby testy mogly je podmienic.

    Prompt idzie przez stdin, nie przez argv. Sprawdzone: przekazany jako
    argument wiersza polecen gubi tresc (model widzi instrukcje, ale nie widzi
    wsadu i odpowiada, ze czeka na dane). Stdin dziala i jest szybszy.
    """
    cmd = [_claude_exe(), "-p", "--model", model,
           "--disallowedTools", "Bash,Edit,Write,Read,Task,WebFetch,WebSearch"]
    out = subprocess.run(cmd, input=prompt, capture_output=True, text=True,
                         encoding="utf-8", errors="replace", timeout=timeout)
    if out.returncode != 0:
        raise RuntimeError("claude -p zwrocil %d: %s" % (out.returncode, (out.stderr or "")[:300]))
    return out.stdout


def parse_reply(reply):
    """Wyluskuje obiekt JSON z odpowiedzi. Toleruje blok kodu i tekst dookola."""
    if not reply:
        return None
    m = re.search(r"\{.*\}", reply, re.S)
    if not m:
        return None
    try:
        data = json.loads(m.group(0))
    except ValueError:
        return None
    return data if isinstance(data, dict) else None


def translate_batch(texts, model=MODEL, timeout=TIMEOUT):
    """Slownik oryginal -> tlumaczenie. Jedno ponowienie, potem pusty wynik."""
    prompt = build_prompt(texts)
    for proba in range(2):
        try:
            data = parse_reply(_run_claude(prompt, model, timeout))
        except Exception:
            data = None
        if data is None:
            continue
        wynik = {}
        for i, oryginal in enumerate(texts):
            wartosc = data.get(str(i))
            if isinstance(wartosc, str) and wartosc.strip():
                wynik[oryginal] = wartosc.strip()
        if wynik:
            return wynik
    return {}


def translate_missing(entries, store_path, workers=4, model=MODEL, batch=BATCH, progress=None):
    """Uzupelnia pamiec o brakujace tlumaczenia. Zwraca liczbe dopisanych."""
    store = translations.load(store_path)
    braki = translations.missing(entries, store)
    if not braki:
        return 0

    wsady = [braki[i:i + batch] for i in range(0, len(braki), batch)]
    dodane = {"n": 0, "gotowe": 0}

    def zrob(wsad):
        wynik = translate_batch(wsad, model=model)
        with _lock:
            for oryginal, tlumaczenie in wynik.items():
                store[translations.key(oryginal)] = tlumaczenie
            dodane["n"] += len(wynik)
            dodane["gotowe"] += 1
            translations.save(store_path, store)
            if progress:
                progress(dodane["gotowe"], len(wsady), dodane["n"], len(braki))

    with ThreadPoolExecutor(max_workers=workers) as pool:
        list(pool.map(zrob, wsady))

    return dodane["n"]


if __name__ == "__main__":
    import argparse
    from parse_changelog import load as load_releases

    ap = argparse.ArgumentParser(description="Uzupelnia polskie tlumaczenia changelogu")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--batch", type=int, default=BATCH)
    ap.add_argument("--model", default=MODEL)
    ap.add_argument("--limit", type=int, default=0, help="tylko N pierwszych brakow (proba)")
    args = ap.parse_args()

    here = os.path.dirname(os.path.abspath(__file__))
    store_path = os.path.join(here, "data", "translations.json")
    wpisy = [e for r in load_releases() for e in r["entries"]]
    if args.limit:
        store = translations.load(store_path)
        wpisy = translations.missing(wpisy, store)[:args.limit]

    def pokaz(gotowe, wszystkie, dodane, do_zrobienia):
        print("wsad %d/%d | dopisane %d/%d" % (gotowe, wszystkie, dodane, do_zrobienia), flush=True)

    n = translate_missing(wpisy, store_path, workers=args.workers, model=args.model,
                          batch=args.batch, progress=pokaz)
    store = translations.load(store_path)
    wszystkie = [e for r in load_releases() for e in r["entries"]]
    mam, ile = translations.coverage(wszystkie, store)
    print("dopisano %d | pokrycie %d/%d (%.1f%%)" % (n, mam, ile, 100.0 * mam / max(ile, 1)))
