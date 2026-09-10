import pytest
import os
from unittest.mock import patch, MagicMock
from fl_studio_mcp.pie.project_hacker import ProjectHackerEngine

def test_project_hacker_set_file():
    engine = ProjectHackerEngine()

    # Test setting non-existent file
    res = engine.set_active_project("/does/not/exist.flp")
    assert "error" in res

    # Test setting a valid file using this test file as a mock
    res = engine.set_active_project(__file__)
    assert res.get("status") == "success"
    assert engine.active_project_path == __file__

@patch("fl_studio_mcp.pie.project_hacker.pyflp.parse")
def test_project_hacker_read_structure(mock_parse):
    engine = ProjectHackerEngine()
    engine.active_project_path = "/mock/path.flp"

    # Set up mock project structure
    mock_project = MagicMock()
    mock_project.version = "21.0.0"
    mock_project.tempo = 120.0

    mock_ch = MagicMock()
    mock_ch.name = "Kick"
    mock_ch.volume = 0.8
    mock_ch.pan = 0.0
    mock_project.channels = [mock_ch]

    mock_pat = MagicMock()
    mock_pat.name = "Pattern 1"
    mock_pat.color = 0xFFFFFF
    mock_project.patterns = [mock_pat]

    mock_parse.return_value = mock_project

    res = engine.read_structure()

    assert "error" not in res
    assert res["version"] == "21.0.0"
    assert res["tempo"] == 120.0
    assert res["total_channels"] == 1
    assert res["channels"][0]["name"] == "Kick"
    assert res["total_patterns"] == 1

@patch("fl_studio_mcp.pie.project_hacker.pyflp.parse")
@patch("fl_studio_mcp.pie.project_hacker.shutil.copy2")
def test_project_hacker_inject_pattern(mock_copy, mock_parse):
    engine = ProjectHackerEngine()
    engine.active_project_path = "/mock/path.flp"

    res = engine.inject_pattern("Test Pattern", 0xFF00FF)

    assert res.get("status") == "success"
    assert res["backup_path"] == "/mock/path.flp.pie_backup"

    # Assert copy was called to create backup
    mock_copy.assert_called_once_with("/mock/path.flp", "/mock/path.flp.pie_backup")
    mock_parse.assert_called_once_with("/mock/path.flp")
