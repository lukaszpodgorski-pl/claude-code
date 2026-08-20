# -*- coding: utf-8 -*-
"""Testy strony wejsciowej /claude-code/.

Ta strona jest pisana recznie, nie generowana z szablonu, wiec ma wlasny
slownik S.pl / S.en. Dlatego sprawdzamy ja osobno: te same elementy
newslettera co na osi czasu i teksty obecne w obu jezykach.
"""
import os
import re

import pytest

from test_template import CZTERNASCIE_DNI, POLITYKA, SENDY_ENDPOINT, SENDY_LISTA

HERE = os.path.dirname(os.path.abspath(__file__))
STRONA = os.path.join(os.path.dirname(HERE), "public", "claude-code", "index.html")

KLUCZE_NL = ("nlBtn", "nlBarText", "nlTitle", "nlConsent", "nlSubmit", "nlOkText")


@pytest.fixture(scope="module")
def strona():
    with open(STRONA, "r", encoding="utf-8") as f:
        return f.read()


def test_strona_ma_przycisk_belke_i_modal_newslettera(strona):
    for element in ('id="nlBtn"', 'id="nlBar"', 'id="nlModal"'):
        assert element in strona, element


def test_strona_wysyla_zapis_na_endpoint_sendy(strona):
    assert SENDY_ENDPOINT in strona
    assert SENDY_LISTA in strona


def test_formularz_ma_honeypot_i_zgode(strona):
    assert 'name="hp"' in strona
    assert 'id="nlGdpr"' in strona


def test_belka_wysuwa_sie_po_dwudziestu_sekundach(strona):
    assert re.search(r"\b20000\b", strona)


def test_zamknieta_belka_spi_czternascie_dni(strona):
    assert re.search(CZTERNASCIE_DNI, strona)


def test_strona_linkuje_polityke_prywatnosci(strona):
    assert POLITYKA in strona


def test_teksty_newslettera_sa_w_obu_jezykach(strona):
    """Slownik S ma dwie galezie; kazdy klucz newslettera musi byc w obu."""
    podzial = re.search(r"\n  en: \{", strona)
    assert podzial, "nie znaleziono galezi en w slowniku S"
    czesc_pl, czesc_en = strona[:podzial.start()], strona[podzial.start():]
    for klucz in KLUCZE_NL:
        assert klucz + ":" in czesc_pl, "brak %s w S.pl" % klucz
        assert klucz + ":" in czesc_en, "brak %s w S.en" % klucz
