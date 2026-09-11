import pytest
from unittest.mock import patch, MagicMock
from fl_studio_mcp.pie.midi_adapter import MIDIAdapter

def test_midi_adapter_queueing():
    adapter = MIDIAdapter()
    assert len(adapter.queue) == 0

    dummy_notes = [{"midi": 60, "duration": 1.0, "time": 0.0, "velocity": 0.8}]
    adapter.queue_notes(1, dummy_notes)

    assert len(adapter.queue) == 1
    assert adapter.queue[0]["channel_id"] == 1
    assert adapter.queue[0]["notes"] == dummy_notes

@patch("fl_studio_mcp.pie.delivery.get_bridge")
@patch("time.sleep")
def test_midi_adapter_flush(mock_sleep, mock_get_bridge):
    from fl_studio_mcp import protocol
    adapter = MIDIAdapter()

    mock_bridge = MagicMock()
    mock_bridge.call.return_value = {"ok": True}
    mock_bridge.apply_notes.return_value = {"ok": True, "count": 1, "triggered": True}
    mock_get_bridge.return_value = mock_bridge

    dummy_notes_1 = [{"midi": 60, "duration": 1.0, "time": 0.0, "velocity": 0.8}]
    dummy_notes_2 = [{"midi": 64, "duration": 1.0, "time": 0.0, "velocity": 0.8}]

    adapter.queue_notes(1, dummy_notes_1)
    adapter.queue_notes(2, dummy_notes_2)

    res = adapter.flush()

    assert res["status"] == "success"
    assert len(res["executed_tasks"]) == 2
    assert len(adapter.queue) == 0

    assert mock_bridge.call.call_count == 2
    mock_bridge.call.assert_any_call(protocol.CMD_CHANNEL_SELECT, {"channel": 1})
    mock_bridge.call.assert_any_call(protocol.CMD_CHANNEL_SELECT, {"channel": 2})

    # Assert apply_notes was called twice with properly converted notes
    assert mock_bridge.apply_notes.call_count == 2
    mock_bridge.apply_notes.assert_any_call(
        [{"pitch": 60, "time_bars": 0.0, "length_bars": 0.25, "velocity": 0.8}],
        mode="append",
        trigger=True,
    )
    mock_bridge.apply_notes.assert_any_call(
        [{"pitch": 64, "time_bars": 0.0, "length_bars": 0.25, "velocity": 0.8}],
        mode="append",
        trigger=True,
    )
