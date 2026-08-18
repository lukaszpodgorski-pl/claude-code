# -*- coding: utf-8 -*-
"""Testy pobierania zrodel: changelog z GitHuba i daty wydan z npm."""
import json
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "src"))

import fetch_sources  # noqa: E402


CHANGELOG_SAMPLE = "# Changelog\n\n## 2.1.234\n\n- Added a thing\n"
NPM_SAMPLE = json.dumps({
    "time": {
        "created": "2025-02-24T00:00:00.000Z",
        "modified": "2026-08-17T00:00:00.000Z",
        "1.0.0": "2025-05-22T18:00:00.000Z",
        "2.1.234": "2026-08-17T09:30:00.000Z",
    }
}).encode("utf-8")


def test_pobiera_changelog_i_zapisuje_kopie(tmp_path, monkeypatch):
    monkeypatch.setattr(fetch_sources, "_get", lambda url, timeout=30: CHANGELOG_SAMPLE.encode("utf-8"))
    text = fetch_sources.fetch_changelog(str(tmp_path))
    assert text.startswith("# Changelog")
    assert (tmp_path / "changelog.md").read_text(encoding="utf-8") == CHANGELOG_SAMPLE


def test_wraca_do_kopii_gdy_siec_padnie(tmp_path, monkeypatch):
    (tmp_path / "changelog.md").write_text(CHANGELOG_SAMPLE, encoding="utf-8")

    def boom(url, timeout=30):
        raise OSError("brak sieci")

    monkeypatch.setattr(fetch_sources, "_get", boom)
    assert fetch_sources.fetch_changelog(str(tmp_path)) == CHANGELOG_SAMPLE


def test_bez_sieci_i_bez_kopii_rzuca(tmp_path, monkeypatch):
    def boom(url, timeout=30):
        raise OSError("brak sieci")

    monkeypatch.setattr(fetch_sources, "_get", boom)
    with pytest.raises(OSError):
        fetch_sources.fetch_changelog(str(tmp_path))


def test_daty_npm_bez_kluczy_sluzbowych(tmp_path, monkeypatch):
    monkeypatch.setattr(fetch_sources, "_get", lambda url, timeout=30: NPM_SAMPLE)
    times = fetch_sources.fetch_npm_times(str(tmp_path))
    assert times == {"1.0.0": "2025-05-22", "2.1.234": "2026-08-17"}
    assert "created" not in times and "modified" not in times


def test_daty_npm_wracaja_do_kopii(tmp_path, monkeypatch):
    monkeypatch.setattr(fetch_sources, "_get", lambda url, timeout=30: NPM_SAMPLE)
    fetch_sources.fetch_npm_times(str(tmp_path))

    def boom(url, timeout=30):
        raise OSError("brak sieci")

    monkeypatch.setattr(fetch_sources, "_get", boom)
    assert fetch_sources.fetch_npm_times(str(tmp_path))["1.0.0"] == "2025-05-22"


def test_zapis_jest_atomowy(tmp_path, monkeypatch):
    """Przerwany zapis nie zostawia uszkodzonej kopii ani smieci .tmp."""
    monkeypatch.setattr(fetch_sources, "_get", lambda url, timeout=30: CHANGELOG_SAMPLE.encode("utf-8"))
    fetch_sources.fetch_changelog(str(tmp_path))
    assert [p.name for p in tmp_path.iterdir()] == ["changelog.md"]
