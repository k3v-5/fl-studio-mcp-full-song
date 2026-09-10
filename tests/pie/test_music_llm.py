import pytest
from unittest.mock import patch, MagicMock
from fl_studio_mcp.pie.music_llm import get_external_music_connector
import requests

def test_external_music_model_fallback():
    connector = get_external_music_connector()

    # Test unsupported model
    err = connector.fetch_advanced_midi("invalid_model", "test")
    assert "error" in err

    # Test network failure / unreachable endpoint (triggers fallback)
    with patch("requests.post") as mock_post:
        mock_post.side_effect = requests.exceptions.ConnectionError("Unreachable")
        res = connector.fetch_advanced_midi("melody", "jazz")

        assert res.get("status") == "fallback"
        assert len(res["notes"]) > 0
        assert "midi" in res["notes"][0]

def test_external_music_model_success():
    connector = get_external_music_connector()
    connector.set_api_key("fake_key")

    with patch("requests.post") as mock_post:
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "notes": [{"midi": 72, "time": 0.0, "duration": 1.0, "velocity": 1.0}]
        }
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        res = connector.fetch_advanced_midi("drum", "house beat")

        assert res.get("status") == "success"
        assert len(res["notes"]) == 1
        assert res["notes"][0]["midi"] == 72

        # Verify Auth header was passed
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert "Authorization" in kwargs["headers"]
        assert kwargs["headers"]["Authorization"] == "Bearer fake_key"
