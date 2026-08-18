# -*- coding: utf-8 -*-
"""Testy kompletnosci warstwy jezykowej: teksty interfejsu, kategorie, kamienie."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "src"))

import i18n  # noqa: E402
import milestones  # noqa: E402

JEZYKI = ("pl", "en")


def test_teksty_interfejsu_kompletne_w_obu_jezykach():
    assert i18n.check() == []


def test_ten_sam_zestaw_kluczy_w_obu_jezykach():
    assert set(i18n.UI["pl"]) == set(i18n.UI["en"])


def test_listy_maja_te_sama_dlugosc_w_obu_jezykach():
    """Miesiace, rodzaje i formy mnogie musza sie zgadzac pozycja w pozycje."""
    for k, v in i18n.UI["pl"].items():
        if isinstance(v, list):
            assert len(v) == len(i18n.UI["en"][k]), "rozna dlugosc listy: " + k


def test_kategorie_maja_etykiety_i_dwa_kolory():
    for key, pl, en, dark, light in i18n.TOPICS:
        assert pl.strip() and en.strip(), key
        assert dark.startswith("#") and len(dark) == 7, key
        assert light.startswith("#") and len(light) == 7, key


def test_kategorie_sa_unikalne():
    klucze = [t[0] for t in i18n.TOPICS]
    assert len(klucze) == len(set(klucze))


def test_kazdy_kamien_ma_cztery_niepuste_teksty():
    for m in milestones.MILESTONES:
        for pole in ("title_pl", "title_en", "desc_pl", "desc_en"):
            assert m[pole].strip(), "%s: puste %s" % (m["v"], pole)


def test_kazdy_kamien_wskazuje_istniejaca_kategorie():
    klucze = {t[0] for t in i18n.TOPICS}
    for m in milestones.MILESTONES:
        assert m["topic"] in klucze, m["v"]


def test_wersje_kamieni_sa_unikalne():
    wersje = [m["v"] for m in milestones.MILESTONES]
    assert len(wersje) == len(set(wersje))


def test_ery_maja_nazwe_i_podpis_w_obu_jezykach():
    for e in milestones.ERAS:
        for pole in ("name_pl", "name_en", "sub_pl", "sub_en"):
            assert e[pole].strip(), "%s: puste %s" % (e["prefix"], pole)


def test_opisy_kamieni_nie_maja_niedomknietych_znacznikow():
    """Opisy ida do DOM jako HTML, wiec <code> musi byc sparowane."""
    for m in milestones.MILESTONES:
        for pole in ("desc_pl", "desc_en"):
            tekst = m[pole]
            assert tekst.count("<code>") == tekst.count("</code>"), "%s: %s" % (m["v"], pole)
