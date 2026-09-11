from pathlib import Path
from fl_studio_mcp.indexer.paths import default_packs_root, default_manifest_path


class TestDefaultPacksRoot:
    def test_uses_env_var_when_set(self, monkeypatch):
        monkeypatch.setenv("FL_MCP_PACKS_ROOT", "/custom/path")
        assert default_packs_root() == Path("/custom/path")

    def test_linux_default(self, monkeypatch):
        monkeypatch.delenv("FL_MCP_PACKS_ROOT", raising=False)
        monkeypatch.setattr("sys.platform", "linux")
        monkeypatch.setenv("HOME", "/home/test")
        result = default_packs_root()
        assert ".flstudio_prefix" in str(result)
        assert "Packs" in str(result)

    def test_candidate_pack_roots(self, monkeypatch):
        from fl_studio_mcp.indexer.paths import find_all_candidate_pack_roots
        monkeypatch.setenv("FL_MCP_PACKS_ROOT", "/env/path")
        candidates = find_all_candidate_pack_roots()
        assert Path("/env/path") in candidates


class TestDefaultManifestPath:
    def test_uses_env_var_when_set(self, monkeypatch):
        monkeypatch.setenv("FL_MCP_MANIFEST_PATH", "/x/m.parquet")
        assert default_manifest_path() == Path("/x/m.parquet")

    def test_default_in_user_home(self, monkeypatch):
        monkeypatch.delenv("FL_MCP_MANIFEST_PATH", raising=False)
        monkeypatch.setenv("HOME", "/home/test")
        result = default_manifest_path()
        assert ".fl_mcp" in str(result)
        assert result.name.endswith(".parquet")
