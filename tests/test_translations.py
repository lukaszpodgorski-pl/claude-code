# -*- coding: utf-8 -*-
"""Testy trwalej pamieci tlumaczen kluczowanej haszem oryginalu."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "src"))

import translations  # noqa: E402


def test_klucz_jest_stabilny_i_rozroznia_teksty():
    a = translations.key("Added a thing")
    assert a == translations.key("Added a thing")
    assert a != translations.key("Added another thing")
    assert len(a) == 40


def test_klucz_liczy_sie_z_bajtow_utf8():
    """Znaki spoza ASCII nie moga wywracac haszowania."""
    assert len(translations.key("Poprawiono zazolc gesla jazn")) == 40
    assert translations.key("zażółć") != translations.key("zazolc")


def test_missing_zwraca_tylko_nieprzetlumaczone_bez_powtorzen():
    store = {translations.key("Added A"): "Dodano A"}
    braki = translations.missing(["Added A", "Added B", "Added B"], store)
    assert braki == ["Added B"]


def test_zapis_i_odczyt_zachowuja_znaki_diakrytyczne(tmp_path):
    path = str(tmp_path / "t.json")
    store = {translations.key("Fixed rendering"): "Poprawiono renderowanie zażółconych gęśli"}
    translations.save(path, store)
    assert translations.load(path) == store
    assert "\\u017c" not in (tmp_path / "t.json").read_text(encoding="utf-8")


def test_odczyt_nieistniejacego_pliku_daje_pusty_slownik(tmp_path):
    assert translations.load(str(tmp_path / "nie_ma.json")) == {}


def test_zapis_sortuje_klucze_dla_czytelnych_diffow(tmp_path):
    path = str(tmp_path / "t.json")
    translations.save(path, {"ffff": "b", "0000": "a"})
    tresc = (tmp_path / "t.json").read_text(encoding="utf-8")
    assert tresc.index('"0000"') < tresc.index('"ffff"')


def test_zapis_jest_atomowy(tmp_path):
    path = str(tmp_path / "t.json")
    translations.save(path, {"a": "b"})
    assert [p.name for p in tmp_path.iterdir()] == ["t.json"]
