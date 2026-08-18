# -*- coding: utf-8 -*-
"""Naprawa tłumaczeń, które wróciły od modelu bez znaków diakrytycznych.

Model potrafi oddać poprawną polszczyznę pozbawioną ogonków i robi to całymi
wsadami. Ten skrypt znajduje takie wpisy, usuwa je z pamięci i tłumaczy ponownie
poprawionym promptem. Jest idempotentny: uruchomiony ponownie nie ma co robić.

Uruchomienie:  python src/repair_translations.py [--dry-run]
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import translate  # noqa: E402
import translations  # noqa: E402
from parse_changelog import load  # noqa: E402

SKLEP = os.path.join(HERE, "data", "translations.json")


def podejrzane(entries, store):
    """Teksty angielskie, ktorych polskie tlumaczenie jest okaleczone z ogonkow."""
    out, widziane = [], set()
    for en in entries:
        k = translations.key(en)
        pl = store.get(k)
        if not pl or k in widziane:
            continue
        if translate.kaleka(pl):
            widziane.add(k)
            out.append(en)
    return out


def main():
    sucho = "--dry-run" in sys.argv
    rel = load(offline=True)
    wpisy = [e for r in rel for e in r["entries"]]
    store = translations.load(SKLEP)

    do_naprawy = podejrzane(wpisy, store)
    print("tlumaczen w pamieci: %d" % len(store))
    print("do naprawy (zawieraja forme, ktora zawsze ma ogonek): %d" % len(do_naprawy))
    if not do_naprawy:
        print("nie ma czego naprawiac")
        return 0
    for przyklad in do_naprawy[:3]:
        print("  przyklad: %s" % store[translations.key(przyklad)][:90])
    if sucho:
        return 0

    for en in do_naprawy:
        store.pop(translations.key(en), None)
    translations.save(SKLEP, store)
    print("usunieto z pamieci, tlumacze ponownie...")

    dodane = translate.translate_missing(
        wpisy, SKLEP, workers=4,
        progress=lambda g, w, d, c: print("  wsad %d/%d, dopisane %d/%d" % (g, w, d, c), flush=True))

    store = translations.load(SKLEP)
    zostalo = podejrzane(wpisy, store)
    print("dopisano %d | nadal bez ogonkow: %d" % (dodane, len(zostalo)))
    mam, ile = translations.coverage(wpisy, store)
    print("pokrycie: %d/%d (%.1f%%)" % (mam, ile, 100.0 * mam / max(ile, 1)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
