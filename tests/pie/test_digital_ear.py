import pytest
import numpy as np
from fl_studio_mcp.pie.digital_ear import DigitalEarEngine

def test_digital_ear_masking():
    pytest.importorskip("librosa")
    # Use a non-default port so tests don't bind clash if running multiple times
    engine = DigitalEarEngine(port=9999)

    # Generate two 100Hz sine waves (they should mask heavily)
    sr = 44100
    t = np.linspace(0, 1.0, sr, endpoint=False)
    audio_a = 0.5 * np.sin(2 * np.pi * 100 * t).astype(np.float32)
    audio_b = 0.5 * np.sin(2 * np.pi * 100 * t).astype(np.float32)

    res = engine.analyze_masking(audio_a, audio_b)

    assert "error" not in res
    assert res["masking_detected"] is True
    # Should flag around 100Hz
    # Librosa frequency bins are not perfectly granular (they jump in chunks based on sr and n_fft).
    # 100Hz falls into a bin that covers around 107Hz, so we add a larger tolerance for this dummy test.
    assert 80 <= res["conflict_zone_hz"][0] <= 130
    assert 80 <= res["conflict_zone_hz"][1] <= 130

def test_digital_ear_lufs():
    pytest.importorskip("pyloudnorm")
    engine = DigitalEarEngine(port=9998)

    # Generate a loud 440Hz wave
    sr = 44100
    t = np.linspace(0, 1.0, sr, endpoint=False)
    # A full scale sine wave (amplitude 1.0) is roughly -3 LUFS
    audio_loud = 1.0 * np.sin(2 * np.pi * 440 * t).astype(np.float32)

    # Inject it directly into the engine's buffer
    engine.audio_buffer = audio_loud.tolist()

    res = engine.measure_readiness()

    assert "error" not in res
    assert res["current_lufs"] > -10.0 # Should be quite loud
    # True peak of a 1.0 sine wave should be roughly 0.0 dB
    assert -1.0 <= res["current_true_peak"] <= 1.0

def test_digital_ear_phase():
    engine = DigitalEarEngine(port=9997)

    sr = 44100
    t = np.linspace(0, 1.0, sr, endpoint=False)

    # Identical signals (Perfect mono compatibility)
    audio_l = np.sin(2 * np.pi * 100 * t).astype(np.float32)
    audio_r = np.sin(2 * np.pi * 100 * t).astype(np.float32)

    res_good = engine.analyze_stereo_phase(audio_l, audio_r)
    assert "error" not in res_good
    assert res_good["correlation"] > 0.9
    assert res_good["mono_compatible"] is True

    # Inverted signal (Destructive out of phase)
    audio_r_inv = -audio_l
    res_bad = engine.analyze_stereo_phase(audio_l, audio_r_inv)
    assert "error" not in res_bad
    assert res_bad["correlation"] < -0.9
    assert res_bad["mono_compatible"] is False
