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

# Sendy stoi pod tym samym originem co strona, wiec zapis idzie zwyklym fetchem.
# Identyfikator listy jest jawny z zalozenia: siedzi w kazdym formularzu Sendy.
SENDY_ENDPOINT = "/sendy/subscribe"
SENDY_LISTA = "Ty1TI6ayPZpGzayzEajXfA"
POLITYKA = "https://lukaszpodgorski.pl/polityka-prywatnosci/"
CZTERNASCIE_DNI = r"14\s*\*\s*24\s*\*\s*60\s*\*\s*60\s*\*\s*1000"


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


def test_szablon_ma_przycisk_belke_i_modal_newslettera(szablon):
    for element in ('id="nlBtn"', 'id="nlBar"', 'id="nlModal"'):
        assert element in szablon, element


def test_szablon_wysyla_zapis_na_endpoint_sendy(szablon):
    assert SENDY_ENDPOINT in szablon
    assert SENDY_LISTA in szablon


def test_zapis_prosi_sendy_o_odpowiedz_zamiast_przekierowania(szablon):
    """Bez boolean=true Sendy przekierowuje, a fetch nie pozna wyniku zapisu."""
    assert re.search(r"boolean[\"']?\s*[:=,]\s*[\"']?true", szablon)
    assert re.search(r"subform[\"']?\s*[:=,]\s*[\"']?yes", szablon)


def test_formularz_ma_honeypot_i_zgode(szablon):
    assert 'name="hp"' in szablon
    assert 'id="nlGdpr"' in szablon


def test_belka_wysuwa_sie_po_dwudziestu_sekundach(szablon):
    assert re.search(r"\b20000\b", szablon)


def test_zamknieta_belka_spi_czternascie_dni(szablon):
    assert re.search(CZTERNASCIE_DNI, szablon)


def test_szablon_linkuje_polityke_prywatnosci(szablon):
    assert POLITYKA in szablon
