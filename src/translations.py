# -*- coding: utf-8 -*-
"""Trwala pamiec tlumaczen wpisow changelogu.

Klucz to sha1 oryginalu angielskiego, nie pozycja na liscie. Changelog bywa
przesortowany i przenumerowany miedzy wydaniami, a hasz na to nie reaguje:
raz przetlumaczony wpis zostaje przetlumaczony na zawsze, niezaleznie od tego,
gdzie wyladuje w pliku.
"""
import hashlib
import json
import os


def key(text):
    """Klucz wpisu: sha1 z bajtow UTF-8 oryginalu."""
    return hashlib.sha1(text.encode("utf-8")).hexdigest()


def load(path):
    """Slownik klucz -> tlumaczenie. Brak pliku to pusta pamiec, nie blad."""
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save(path, store):
    """Zapis atomowy, posortowany, bez ucieczek unicode (czytelne diffy w gicie)."""
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(store, f, ensure_ascii=False, indent=0, sort_keys=True)
        f.write("\n")
    os.replace(tmp, path)


def missing(texts, store):
    """Teksty bez tlumaczenia, bez powtorzen, w kolejnosci wystapienia."""
    braki, widziane = [], set()
    for t in texts:
        k = key(t)
        if k in store or k in widziane:
            continue
        widziane.add(k)
        braki.append(t)
    return braki


def coverage(texts, store):
    """(przetlumaczone, wszystkie_unikalne) — do raportowania postepu."""
    unikalne = {key(t) for t in texts}
    return sum(1 for k in unikalne if k in store), len(unikalne)
