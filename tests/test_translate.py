# -*- coding: utf-8 -*-
"""Testy tlumaczenia wsadowego. Wywolanie procesu jest podmieniane."""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "src"))

import translate  # noqa: E402
import translations  # noqa: E402


def _odpowiedz(mapa):
    return json.dumps(mapa, ensure_ascii=False)


def test_poprawny_json_trafia_do_slownika(monkeypatch):
    monkeypatch.setattr(translate, "_run_claude",
                        lambda prompt, model, timeout: _odpowiedz({"0": "Dodano A", "1": "Poprawiono B"}))
    wynik = translate.translate_batch(["Added A", "Fixed B"])
    assert wynik == {"Added A": "Dodano A", "Fixed B": "Poprawiono B"}


def test_odpowiedz_w_bloku_kodu_jest_akceptowana(monkeypatch):
    monkeypatch.setattr(translate, "_run_claude",
                        lambda prompt, model, timeout: "Prosze:\n```json\n{\"0\": \"Dodano A\"}\n```\n")
    assert translate.translate_batch(["Added A"]) == {"Added A": "Dodano A"}


def test_uciety_json_powoduje_jedno_ponowienie(monkeypatch):
    proby = {"n": 0}

    def kapryśny(prompt, model, timeout):
        proby["n"] += 1
        if proby["n"] == 1:
            return '{"0": "Dodano A"'
        return _odpowiedz({"0": "Dodano A"})

    monkeypatch.setattr(translate, "_run_claude", kapryśny)
    assert translate.translate_batch(["Added A"]) == {"Added A": "Dodano A"}
    assert proby["n"] == 2


def test_trwale_zepsute_wyjscie_nie_wywraca_calosci(monkeypatch):
    monkeypatch.setattr(translate, "_run_claude", lambda prompt, model, timeout: "nie ma tu json-a")
    assert translate.translate_batch(["Added A"]) == {}


def test_brakujace_pozycje_sa_pomijane_a_reszta_zostaje(monkeypatch):
    """Model oddal tylko czesc wsadu — bierzemy, co jest, bez wyjatku."""
    monkeypatch.setattr(translate, "_run_claude",
                        lambda prompt, model, timeout: _odpowiedz({"0": "Dodano A"}))
    assert translate.translate_batch(["Added A", "Fixed B"]) == {"Added A": "Dodano A"}


def test_puste_tlumaczenie_jest_odrzucane(monkeypatch):
    monkeypatch.setattr(translate, "_run_claude",
                        lambda prompt, model, timeout: _odpowiedz({"0": "   ", "1": "Poprawiono B"}))
    assert translate.translate_batch(["Added A", "Fixed B"]) == {"Fixed B": "Poprawiono B"}


def test_translate_missing_dopisuje_do_pamieci(tmp_path, monkeypatch):
    sklep = str(tmp_path / "t.json")
    translations.save(sklep, {translations.key("Added A"): "Dodano A"})
    monkeypatch.setattr(translate, "_run_claude",
                        lambda prompt, model, timeout: _odpowiedz({"0": "Poprawiono B"}))
    dodane = translate.translate_missing(["Added A", "Fixed B"], sklep, workers=1)
    assert dodane == 1
    store = translations.load(sklep)
    assert store[translations.key("Added A")] == "Dodano A"
    assert store[translations.key("Fixed B")] == "Poprawiono B"


def test_translate_missing_bez_brakow_nie_wola_modelu(tmp_path, monkeypatch):
    sklep = str(tmp_path / "t.json")
    translations.save(sklep, {translations.key("Added A"): "Dodano A"})

    def nie_wolno(prompt, model, timeout):
        raise AssertionError("model nie powinien byc wolany")

    monkeypatch.setattr(translate, "_run_claude", nie_wolno)
    assert translate.translate_missing(["Added A"], sklep, workers=1) == 0


def test_prompt_niesie_slownik_terminow_i_numeracje():
    p = translate.build_prompt(["Added MCP support"])
    assert "MCP" in p
    assert '"0"' in p or "0:" in p
    assert "Added MCP support" in p
