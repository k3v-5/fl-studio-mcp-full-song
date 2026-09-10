"""External Music Model Connector for FL Studio MCP (PIE).

Interfaces with external AI APIs (like Magenta, Suno, or specialized Audio-to-MIDI endpoints)
to extract advanced music theory and generate complex MIDI sequences beyond the base LLM's logical capabilities.
"""

from __future__ import annotations

import requests
from typing import Any

class ExternalMusicModelConnector:
    def __init__(self) -> None:
        # Mock endpoints for demonstration. In a production scenario,
        # these would point to actual Magenta/Suno/OpenAI proxy servers.
        self.endpoints = {
            "magenta_melody": "https://api.mock-magenta.local/generate/melody",
            "magenta_drum": "https://api.mock-magenta.local/generate/drums"
        }
        self.api_key: str | None = None

    def set_api_key(self, key: str) -> None:
        """Set the API key for external musical models."""
        self.api_key = key

    def fetch_advanced_midi(self, model_type: str, prompt: str, length_beats: float = 16.0) -> dict[str, Any]:
        """Request advanced MIDI sequence generation from an external model.

        Args:
            model_type: "melody" or "drum"
            prompt: Text prompt describing the musical intent (e.g., "A jazz fusion bassline in Dorian mode")
            length_beats: Length of the desired sequence.
        """
        endpoint = self.endpoints.get(f"magenta_{model_type}")
        if not endpoint:
            return {"error": f"Unsupported model type: {model_type}"}

        payload = {
            "prompt": prompt,
            "length_beats": length_beats
        }

        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        try:
            # Send request (with a timeout to prevent hanging the MCP server)
            response = requests.post(endpoint, json=payload, headers=headers, timeout=5.0)
            response.raise_for_status()

            # Assume the external API returns a JSON array of notes matching our schema:
            # [{"midi": int, "time": float, "duration": float, "velocity": float}]
            data = response.json()
            if "notes" not in data:
                 return {"error": "External API returned malformed response."}

            return {"status": "success", "notes": data["notes"]}

        except requests.exceptions.RequestException as e:
            # Provide a fallback mock response if the external server is unreachable (which it will be in this sandbox)
            return self._generate_fallback_mock(model_type, prompt)

    def _generate_fallback_mock(self, model_type: str, prompt: str) -> dict[str, Any]:
        """Generate a simulated response when the external API is unreachable."""
        notes = []
        if model_type == "melody":
            # Mock complex jazz lick
            notes = [
                {"midi": 62, "time": 0.0, "duration": 0.5, "velocity": 0.8},
                {"midi": 65, "time": 0.5, "duration": 0.25, "velocity": 0.9},
                {"midi": 69, "time": 0.75, "duration": 0.25, "velocity": 0.7},
                {"midi": 67, "time": 1.0, "duration": 1.0, "velocity": 0.85},
            ]
        elif model_type == "drum":
            # Mock complex breakbeat
            notes = [
                {"midi": 36, "time": 0.0, "duration": 0.25, "velocity": 1.0}, # Kick
                {"midi": 38, "time": 1.0, "duration": 0.25, "velocity": 0.9}, # Snare
                {"midi": 42, "time": 0.5, "duration": 0.125, "velocity": 0.7},# Hihat ghost
                {"midi": 36, "time": 1.5, "duration": 0.25, "velocity": 0.8}, # Kick syncopated
            ]

        return {
            "status": "fallback",
            "message": f"External API unreachable. Generated fallback advanced MIDI for: '{prompt}'",
            "notes": notes
        }

# Singleton instance
_external_music_connector = ExternalMusicModelConnector()

def get_external_music_connector() -> ExternalMusicModelConnector:
    return _external_music_connector
