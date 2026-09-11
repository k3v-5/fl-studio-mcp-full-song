"""Test for Ralphie Choo style song generation."""

import os
from scripts.produce_maquina_culona import compose_maquina_culona


def test_compose_maquina_culona():
    res = compose_maquina_culona()
    assert res["ok"]
    assert res["tracks"] == 7
    assert res["total_notes"] > 500
    assert os.path.exists(res["midi_path"])
    assert res["bpm"] == 100.0
