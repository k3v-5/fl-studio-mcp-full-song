"""Tests for the integrated knowledge, indexer, and workflow tools."""
import asyncio
import pytest
from fastmcp import FastMCP

from fl_studio_mcp.tools import (
    knowledge_theory,
    knowledge_producers,
    knowledge_plugins,
    knowledge_mixing,
    indexer,
    knowledge_learned,
    workflows,
)


@pytest.fixture
def mcp_app():
    app = FastMCP("test-fl-studio")
    knowledge_theory.register(app)
    knowledge_producers.register(app)
    knowledge_plugins.register(app)
    knowledge_mixing.register(app)
    indexer.register(app)
    knowledge_learned.register(app)
    workflows.register(app)
    return app


def call(app: FastMCP, name: str, **kwargs):
    import json
    res = asyncio.run(app.call_tool(name, kwargs))
    if res.structured_content and "result" in res.structured_content:
        val = res.structured_content["result"]
        if isinstance(val, (dict, list)):
            return val
        if isinstance(val, str):
            try:
                return json.loads(val)
            except Exception:
                return val
    if res.content:
        text = res.content[0].text
        try:
            return json.loads(text)
        except Exception:
            return text
    return None


class TestKnowledgeTheoryTools:
    def test_suggest_scale(self, mcp_app):
        res = call(mcp_app, "fl_suggest_scale", genre="boom_bap", mood="dark")
        assert "ESCALAS RECOMENDADAS" in res
        assert "Natural" in res or "dorian" in res or "Frigia" in res

    def test_suggest_progression(self, mcp_app):
        res = call(mcp_app, "fl_suggest_progression", key="A", genre="boom_bap")
        assert "PROGRESIONES RECOMENDADAS" in res
        assert "classic_dark" in res or "Acordes:" in res

    def test_generate_scale_notes(self, mcp_app):
        res = call(mcp_app, "fl_generate_scale_notes", root="A", scale="minor_natural", octave_low=3, octave_high=4)
        assert "MIDI:" in res
        assert "Names:" in res

    def test_generate_chord_progression_raw(self, mcp_app):
        res = call(mcp_app, "fl_generate_chord_progression", progression="classic_dark", key="A", bars=4, send_to_fl=False)
        assert "Note data" in res
        assert "," in res

    def test_generate_drum_pattern_raw(self, mcp_app):
        res = call(mcp_app, "fl_generate_drum_pattern", style="boom_bap_basic", bpm=90.0, send_to_fl=False)
        assert "Drum pattern" in res
        assert "Note data" in res

    def test_generate_bassline_raw(self, mcp_app):
        res = call(mcp_app, "fl_generate_bassline", root_notes="A,A,F,G", style="root_follow", bpm=90.0, send_to_fl=False)
        assert "Bassline" in res
        assert "Note data" in res


class TestKnowledgeProducersAndPlugins:
    def test_get_producer_info(self, mcp_app):
        res = call(mcp_app, "fl_get_producer_info", producer="dj_premier")
        assert "DJ Premier" in res or "PREMIER" in res or "BPM" in res

    def test_list_producers(self, mcp_app):
        res = call(mcp_app, "fl_get_producer_info", producer="list")
        assert "dj_premier" in res
        assert "j_dilla" in res

    def test_get_ozone_mastering(self, mcp_app):
        res = call(mcp_app, "fl_get_ozone_mastering", genre="boom_bap")
        assert "Ozone" in res or "Maximizer" in res or "Equalizer" in res

    def test_get_fabfilter_eq(self, mcp_app):
        res = call(mcp_app, "fl_get_fabfilter_eq", element="vocals")
        assert "Pro-Q" in res or "Hz" in res

    def test_get_serum_patch(self, mcp_app):
        res = call(mcp_app, "fl_get_serum_patch", sound_type="808_sub")
        assert "Serum" in res or "Oscillator" in res or "Sub" in res

    def test_get_vst_module_guide(self, mcp_app):
        res = call(mcp_app, "fl_get_vst_module_guide", suite="ozone", module_or_plugin="maximizer")
        assert "Maximizer" in res or "IRC" in res
        res_overview = call(mcp_app, "fl_get_vst_module_guide", suite="rx11")
        assert "Repair" in res_overview or "Assistant" in res_overview or "spectral" in res_overview.lower()


class TestKnowledgeMixingAndWorkflows:
    def test_get_plugin_chain(self, mcp_app):
        res = call(mcp_app, "fl_get_plugin_chain", element="kick", genre="boom_bap")
        assert "Kick" in res or "EQ" in res or "Comp" in res

    def test_setup_sidechain_offline(self, mcp_app):
        res = call(mcp_app, "fl_setup_sidechain", kick_track=1, bass_track=5)
        assert "SIDECHAIN" in res
        assert "Track 1" in res
        assert "Track 5" in res

    def test_list_sample_categories(self, mcp_app):
        res = call(mcp_app, "fl_list_sample_categories")
        assert "sample_types" in res
        assert "kick" in res["sample_types"]

    def test_workflow_new_beat(self, mcp_app):
        res = call(mcp_app, "fl_workflow_new_beat", genre="boom_bap", bpm=90.0, key="A")
        assert res["workflow"] == "New Beat Blueprint"
        assert res["bpm"] == 90.0
        assert len(res["next_steps"]) >= 4
