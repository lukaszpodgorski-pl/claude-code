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


def test_wykrywa_okaleczona_polszczyzne():
    assert translate.kaleka("Ulepszono obsluge bledow dla /install-github-app") is True
    assert translate.kaleka("Zwiekszono domyslny interwal otel") is True
    assert translate.kaleka("ktore podkresla bledy ortograficzne") is True
    assert translate.kaleka("Ulepszono obsługę błędów dla /install-github-app") is False


def test_poprawny_tekst_bez_ogonkow_nie_jest_alarmem():
    """Polskie zdanie potrafi nie miec ani jednego ogonka i byc poprawne."""
    assert translate.kaleka(
        "Poprawiono otwieranie dodatkowych okien VS Code przy starcie w Windows") is False
    assert translate.kaleka(
        "Przeniesiono allowedTools i ignorePatterns z .claude.json do settings.json") is False
    assert translate.kaleka("Dodano nowy tryb") is False
    # slowa, ktore kusza, zeby wpisac je na liste, a sa poprawne bez ogonkow
    assert translate.kaleka("Zmniejszono zużycie pamięci o 16 MB") is False
    assert translate.kaleka("Poprawiono niepoprawny wynik") is False
    assert translate.kaleka("podkreśla błędy ortograficzne") is False


def test_kontrola_wsadu_lapie_pojedynczy_zepsuty_wpis():
    assert translate.wsad_kaleki({"a": "Dodano nowy tryb", "b": "Ulepszono obsluge"}) is True
    assert translate.wsad_kaleki({"a": "Dodano nowy tryb"}) is False
    assert translate.wsad_kaleki({}) is False


def test_okaleczony_wsad_jest_ponawiany(monkeypatch):
    """Model potrafi oddac cala partie bez ogonkow; druga proba zwykle pomaga."""
    proby = {"n": 0}
    bez = "Poprawiono nieprawidlowe wyrownanie zagniezdzonych elementow listy w terminalu"
    z = "Poprawiono nieprawidłowe wyrównanie zagnieżdżonych elementów listy w terminalu"

    def kolejno(prompt, model, timeout):
        proby["n"] += 1
        return _odpowiedz({"0": bez if proby["n"] == 1 else z})

    monkeypatch.setattr(translate, "_run_claude", kolejno)
    wynik = translate.translate_batch(["Fixed nested list alignment"])
    assert proby["n"] == 2
    assert wynik["Fixed nested list alignment"] == z


def test_gdy_obie_proby_okaleczone_bierzemy_co_jest(monkeypatch):
    """Polszczyzna bez ogonkow jest gorsza niz poprawna, ale lepsza niz brak."""
    bez = "Poprawiono nieprawidlowe wyrownanie zagniezdzonych elementow listy w terminalu"
    monkeypatch.setattr(translate, "_run_claude",
                        lambda prompt, model, timeout: _odpowiedz({"0": bez}))
    wynik = translate.translate_batch(["Fixed nested list alignment"])
    assert wynik["Fixed nested list alignment"] == bez


def test_prompt_wymaga_znakow_diakrytycznych():
    p = translate.build_prompt(["cokolwiek"])
    assert "ą" in p and "ż" in p
    assert "DIAKRYTYCZNYMI" in p
