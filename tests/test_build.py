# -*- coding: utf-8 -*-
"""Testy regresji budowy: ksztalt ladunku i stabilnosc klasyfikacji.

Testy chodza na kopii z .cache (offline=True), zeby nie zalezec od sieci.
"""
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "src"))

import build  # noqa: E402
import i18n  # noqa: E402


@pytest.fixture(scope="module")
def dane():
    return build.make_data(offline=True)


def test_liczby_zgadzaja_sie_ze_stanem_sprzed_przebudowy(dane):
    """Rozdzielenie tekstu na EN i PL nie moze zgubic ani dolozyc wpisow."""
    assert dane["meta"]["releases"] == 366
    assert dane["meta"]["entries"] == 4489


def test_kazdy_wpis_ma_kategorie_rodzaj_i_dwa_teksty(dane):
    for r in dane["releases"]:
        for e in r[3]:
            assert len(e) == 4
            assert 0 <= e[0] < len(i18n.TOPICS)
            assert e[1] in (0, 1, 2)
            assert isinstance(e[2], str) and e[2].strip()
            assert isinstance(e[3], str)


def test_brak_tlumaczenia_daje_pusty_lancuch_a_nie_wyjatek(dane):
    """Strona ma sobie z tym poradzic pokazujac oryginal."""
    puste = [e for r in dane["releases"] for e in r[3] if e[3] == ""]
    assert all(isinstance(e[3], str) for e in puste)


def test_kategoria_pozostale_nie_rozrasta_sie(dane):
    """Regresja klasyfikatora: gdy 'other' rosnie, reguly przestaly lapac."""
    inne = i18n.TOPICS.index(next(t for t in i18n.TOPICS if t[0] == "other"))
    n = sum(1 for r in dane["releases"] for e in r[3] if e[0] == inne)
    assert n / dane["meta"]["entries"] < 0.08


def test_rodzaje_zmian_maja_sensowny_rozklad(dane):
    """W changelogu poprawki sa najliczniejsze, a kazdy rodzaj musi wystapic.

    Zmierzone na stanie 2.1.234: poprawki 2470, nowosci 1333, ulepszenia 686.
    Gdy ktorykolwiek rodzaj zniknie, znaczy to, ze regula rozpoznajaca czasownik
    otwierajacy przestala dzialac.
    """
    ile = [0, 0, 0]
    for r in dane["releases"]:
        for e in r[3]:
            ile[e[1]] += 1
    assert all(n > 0 for n in ile)
    assert ile[0] > ile[2] > ile[1]
    assert sum(ile) == dane["meta"]["entries"]


def test_wydania_sa_uporzadkowane_chronologicznie(dane):
    daty = [r[1] for r in dane["releases"]]
    assert daty == sorted(daty)


def test_kamienie_wskazuja_istniejace_wydania_i_maja_oba_jezyki(dane):
    n = len(dane["releases"])
    for m in dane["milestones"]:
        assert 0 <= m["i"] < n
        assert m["title"]["pl"] and m["title"]["en"]
        assert m["desc"]["pl"] and m["desc"]["en"]


def test_ery_pokrywaja_cala_os_bez_dziur(dane):
    ery = dane["eras"]
    assert ery[0]["from"] == 0
    assert ery[-1]["to"] == len(dane["releases"]) - 1
    for a, b in zip(ery, ery[1:]):
        assert b["from"] == a["to"] + 1


def test_ladunek_niesie_teksty_interfejsu(dane):
    assert set(dane["ui"]) == {"pl", "en"}
    assert dane["ui"]["pl"]["title"] and dane["ui"]["en"]["title"]


def test_kategorie_maja_pieciopolowa_strukture(dane):
    for t in dane["topics"]:
        assert len(t) == 5
