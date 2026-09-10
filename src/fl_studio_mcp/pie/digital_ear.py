"""Digital Ear Engine for FL Studio MCP (PIE).

Real DSP architecture for Phase 5 (Mix), Phase 6 (Master), and Phase 7 (Forensics).
Receives audio via UDP from the VST Interceptor.
"""

from __future__ import annotations

import socket
import threading
import numpy as np
import librosa
import pyloudnorm as pyln
from typing import Any

class DigitalEarEngine:
    def __init__(self, port: int = 9878) -> None:
        self.port = port
        self.is_capturing = False
        self.audio_buffer: list[float] = []
        self.sock: socket.socket | None = None
        self.sample_rate = 44100
        self.listener_thread: threading.Thread | None = None

    def _init_socket(self) -> None:
        """Bind socket lazily to avoid crash on import if port is busy."""
        if not self.sock:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.bind(("127.0.0.1", self.port))
            self.sock.settimeout(1.0)

            self.listener_thread = threading.Thread(target=self._listen_for_audio, daemon=True)
            self.listener_thread.start()

    def _listen_for_audio(self):
        """Background thread to listen for UDP packets containing float32 audio."""
        while True:
            if not self.sock:
                break

            if not self.is_capturing:
                # Just drain the socket if not capturing to prevent buffer bloat
                try:
                    self.sock.recv(4096)
                except socket.timeout:
                    pass
                continue

            try:
                data, _ = self.sock.recvfrom(4096)
                # Convert binary float32 to numpy array
                chunk = np.frombuffer(data, dtype=np.float32)
                self.audio_buffer.extend(chunk.tolist())
            except socket.timeout:
                pass

    def start_capture(self) -> str:
        """Start capturing audio from the VST Interceptor."""
        self._init_socket()
        self.audio_buffer.clear()
        self.is_capturing = True
        return "Audio capture started."

    def stop_capture(self) -> str:
        """Stop capturing and return the number of samples captured."""
        self.is_capturing = False
        return f"Captured {len(self.audio_buffer)} samples."

    def get_audio_array(self) -> np.ndarray:
        return np.array(self.audio_buffer, dtype=np.float32)

    # Phase 5: Mix
    def analyze_masking(self, audio_a: np.ndarray, audio_b: np.ndarray) -> dict[str, Any]:
        """Real DSP analysis for frequency masking using librosa FFTs."""
        if len(audio_a) == 0 or len(audio_b) == 0:
            return {"error": "Missing audio data."}

        # Compute Short-Time Fourier Transform
        stft_a = np.abs(librosa.stft(audio_a))
        stft_b = np.abs(librosa.stft(audio_b))

        # Simple overlap detection
        overlap = np.minimum(stft_a, stft_b)
        mean_overlap = np.mean(overlap, axis=1)
        peak_freq_bin = int(np.argmax(mean_overlap))

        # Convert bin to Hz
        freqs = librosa.fft_frequencies(sr=self.sample_rate)
        conflict_hz = float(freqs[peak_freq_bin])

        masking = float(np.max(mean_overlap)) > 0.1 # Arbitrary threshold

        return {
            "masking_detected": masking,
            "conflict_zone_hz": [conflict_hz - 10, conflict_hz + 10]
        }

    # Phase 6: Mastering
    def measure_readiness(self, target_lufs: float = -9.0, target_true_peak: float = -1.0) -> dict[str, Any]:
        """Real LUFS measurement using pyloudnorm, accepting AI-provided targets."""
        audio = self.get_audio_array()
        if len(audio) == 0:
            return {"error": "No audio captured in buffer."}

        # Pyloudnorm expects (samples, channels). Assuming mono for now.
        meter = pyln.Meter(self.sample_rate)
        try:
            lufs = meter.integrated_loudness(audio)
            true_peak = float(np.max(np.abs(audio)))
            # Convert true peak to dB
            true_peak_db = 20 * np.log10(true_peak) if true_peak > 0 else -100.0

            return {
                "current_lufs": float(lufs),
                "current_true_peak": float(true_peak_db),
                "target_lufs": target_lufs,
                "target_true_peak": target_true_peak,
                "status": "NEEDS_LIMITING" if lufs < target_lufs else "READY"
            }
        except ValueError:
            return {"error": "Audio segment too short for LUFS measurement (needs >= 400ms)."}

    # Phase 7: Forensics
    def generate_forensics_report(self, dc_offset_threshold: float = 0.05, clipping_threshold_db: float = 0.0) -> dict[str, Any]:
        """Real low-level DSP anomaly detection based on AI thresholds."""
        audio = self.get_audio_array()
        if len(audio) == 0:
            return {"error": "No audio captured."}

        dc_offset = float(np.mean(audio))
        true_peak = float(np.max(np.abs(audio)))
        true_peak_db = 20 * np.log10(true_peak) if true_peak > 0 else -100.0

        has_dc = abs(dc_offset) > dc_offset_threshold
        has_clipping = true_peak_db > clipping_threshold_db

        return {
            "dc_offset_value": dc_offset,
            "dc_offset_detected": has_dc,
            "true_peak_db": true_peak_db,
            "clipping_detected": has_clipping,
            "verdict": "Audio requires fixing." if (has_dc or has_clipping) else "Audio is mathematically clean."
        }

# Singleton instance
_digital_ear_engine = DigitalEarEngine()

def get_digital_ear_engine() -> DigitalEarEngine:
    return _digital_ear_engine
