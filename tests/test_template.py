# -*- coding: utf-8 -*-
"""Testy powloki HTML: klucze interfejsu i elementy sterujace w szablonie.

Szablon jest zwyklym tekstem az do budowy, wiec sprawdzamy go tekstem.
Najwazniejszy jest test kluczy: literowka w U.cosTam nie wywala strony,
tylko cicho wypisuje "undefined" w interfejsie.
"""
import os
import re
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "src"))

import i18n  # noqa: E402

TEMPLATE = os.path.join(os.path.dirname(HERE), "src", "template.html")


@pytest.fixture(scope="module")
def szablon():
    with open(TEMPLATE, "r", encoding="utf-8") as f:
        return f.read()


def test_szablon_siega_tylko_po_istniejace_klucze_interfejsu(szablon):
    uzyte = set(re.findall(r"\bU\.([A-Za-z_][A-Za-z0-9_]*)", szablon))
    assert uzyte, "nie znaleziono ani jednego odwolania U.<klucz>"
    brakujace = sorted(k for k in uzyte if k not in i18n.UI["pl"])
    assert brakujace == []


def test_szablon_startuje_na_koncu_osi(szablon):
    """Wejscie na strone ma pokazywac najnowsze wydania, bez animacji."""
    assert re.search(r"sc\.scrollLeft\s*=\s*sc\.scrollWidth", szablon)


def test_szablon_ma_przycisk_i_naklad_tabeli(szablon):
    assert 'id="tglTable"' in szablon
    assert 'id="tblWrap"' in szablon


def test_szablon_linkuje_do_strony_glownej(szablon):
    assert "https://lukaszpodgorski.pl" in szablon
