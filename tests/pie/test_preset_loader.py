"""Tests for PresetLoaderEngine."""

import pytest
from fl_studio_mcp.pie.preset_loader import PresetLoaderEngine, get_preset_loader


def test_get_preset_loader_singleton():
    l1 = get_preset_loader()
    l2 = get_preset_loader()
    assert l1 is l2


def test_scan_installed_generators():
    loader = PresetLoaderEngine()
    res = loader.scan_installed_generators()
    assert res["ok"]
    assert "categories" in res
    assert res["total_found"] >= 0


def test_scaffold_genre_rack_dubstep():
    loader = PresetLoaderEngine()
    res = loader.scaffold_genre_rack("dubstep")
    assert res["ok"]
    assert res["genre"] == "dubstep"
    assert res["instruments_scaffolded"] >= 5
    roles = [ch["role"] for ch in res["channels"]]
    assert "Kick" in roles
    assert "SubBass" in roles or "GrowlBass" in roles


def test_scaffold_genre_rack_trap():
    loader = PresetLoaderEngine()
    res = loader.scaffold_genre_rack("trap")
    assert res["ok"]
    roles = [ch["role"] for ch in res["channels"]]
    assert "Kick" in roles
    assert "808_Slide_Bass" in roles
