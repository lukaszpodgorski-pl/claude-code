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
- PISZ POPRAWNĄ POLSZCZYZNĄ Z PEŁNYMI ZNAKAMI DIAKRYTYCZNYMI: ą, ć, ę, ł, ń, ó, ś, ź, ż.
  Tekst bez ogonków („ktore podkresla bledy") jest błędem, a nie uproszczeniem.
- nie tłumacz nazw własnych i identyfikatorów: Claude Code, MCP, SDK, API, CLI,
  Bedrock, Vertex, VS Code, JetBrains, nazw narzędzi (Bash, Grep, WebFetch),
  nazw komend (/model, /config), flag (--print), zmiennych (ANTHROPIC_API_KEY)
  i nazw plików (CLAUDE.md, settings.json)
- utarte formy: hook -> hook, hooks -> hooki, skill -> skill, skills -> skille,
  plugin -> plugin, subagent -> subagent, sandbox -> sandbox, prompt -> prompt,
  token -> token, plan mode -> tryb planowania, thinking -> rozumowanie,
  checkpoint -> punkt kontrolny, statusline -> pasek stanu, transcript -> zapis rozmowy
- czasownik otwierający w formie bezosobowej dokonanej: Added -> Dodano,
  Fixed -> Poprawiono, Improved -> Ulepszono, Removed -> Usunięto,
  Changed -> Zmieniono, Reverted -> Cofnięto
- zachowaj znaczniki markdown z oryginału (`kod`, **pogrubienie**)
- bez emoji, bez myślnika jako separatora zdania"""

PROMPT = """Przetłumacz na polski wpisy z changelogu Claude Code.

Zasady:
{glossary}

Zwróć WYŁĄCZNIE obiekt JSON: klucz to numer wpisu jako tekst, wartość to
tłumaczenie. Bez komentarza przed ani po, bez bloku kodu, wszystkie {n} pozycji.

Wpisy:
{items}"""

# Zaobserwowane 2026-08-18: model potrafi oddać poprawną polszczyznę pozbawioną
# znaków diakrytycznych i robi to całymi wsadami.
#
# Wykrywanie po „braku jakiegokolwiek ogonka" nie działa: poprawne zdanie
# potrafi nie mieć ani jednego („Poprawiono otwieranie dodatkowych okien VS Code
# przy starcie w Windows"). Dlatego szukamy form, które bez znaku diakrytycznego
# NIE SĄ polskim słowem — „obsluge", „bledow", „ktore", „domyslny". Zero
# fałszywych trafień jest tu ważniejsze niż złapanie każdego przypadku.
KALEKIE = re.compile(r"""\b(
    sie|ktor[aey]|ktorego|ktorej|ktorych|ktorym|moze|mozna|mozliw\w*|jesli|wiecej|
    rozn\w*|blad|bled\w*|polaczen\w*|polaczy\w*|nastepn\w*|wlacz\w*|wylacz\w*|zmienic|
    dziala\w*|uzytk\w*|uzywa\w*|uzycie|dlugosc\w*|wiadomosc\w*|kolejnosc\w*|obslug\w*|
    narzedzi\w*|bedzie|beda|wyswietl\w*|domysln\w*|rowniez|zrodl\w*|sciezk\w*|
    glebokosc\w*|wyrownan\w*|zagniezdz\w*|uniewazni\w*|podkresl\w*|
    elementow|miedzy|wzgledem|usuniet\w*|zwiekszon\w*|wiekszosc|czesc|
    czesci|opoznien\w*|zaleznosc\w*|wlasciw\w*|przegladark\w*|wyjatk\w*|blednie
    )\b""", re.I | re.X)

# Uwaga na przyszlosc przy rozszerzaniu listy: „zmniejszono", „ortograficzne"
# i „niepoprawny" NIE maja ogonkow i sa poprawne. Wpisanie ich tutaj powodowalo
# ponowne tlumaczenie 36 dobrych wpisow w kolko.

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


def kaleka(tekst):
    """True, gdy tekst zawiera slowo, ktore w polszczyznie zawsze ma ogonek."""
    return bool(KALEKIE.search(tekst))


def wsad_kaleki(wynik):
    """True, gdy ktorykolwiek wpis we wsadzie jest okaleczony."""
    return any(kaleka(t) for t in wynik.values())


def translate_batch(texts, model=MODEL, timeout=TIMEOUT):
    """Slownik oryginal -> tlumaczenie. Jedno ponowienie, potem pusty wynik."""
    prompt = build_prompt(texts)
    ostatni = {}
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
        if not wynik:
            continue
        if wsad_kaleki(wynik):
            # zapamietujemy jako awaryjne wyjscie i probujemy jeszcze raz:
            # polszczyzna bez ogonkow jest lepsza niz brak tlumaczenia,
            # ale gorsza niz poprawna
            ostatni = wynik
            continue
        return wynik
    return ostatni


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
