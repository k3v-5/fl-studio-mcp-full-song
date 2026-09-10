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

@patch("fl_studio_mcp.pie.midi_adapter.get_connection")
@patch("fl_studio_mcp.pie.midi_adapter._write_request")
@patch("fl_studio_mcp.pie.midi_adapter.trigger_fl_studio")
@patch("time.sleep")
def test_midi_adapter_flush(mock_sleep, mock_trigger, mock_write, mock_get_connection):
    adapter = MIDIAdapter()

    mock_conn = MagicMock()
    mock_conn.send_command.return_value = {"success": True}
    mock_get_connection.return_value = mock_conn
    mock_trigger.return_value = True

    dummy_notes_1 = [{"midi": 60, "duration": 1.0, "time": 0.0, "velocity": 0.8}]
    dummy_notes_2 = [{"midi": 64, "duration": 1.0, "time": 0.0, "velocity": 0.8}]

    adapter.queue_notes(1, dummy_notes_1)
    adapter.queue_notes(2, dummy_notes_2)

    res = adapter.flush()

    assert res["status"] == "success"
    assert len(res["executed_tasks"]) == 2
    assert len(adapter.queue) == 0

    assert mock_conn.send_command.call_count == 2
    mock_conn.send_command.assert_any_call("channels.selectOne", {"index": 1})
    mock_conn.send_command.assert_any_call("channels.selectOne", {"index": 2})

    # Assert JSON file was written and hotkey was triggered twice
    assert mock_write.call_count == 2
    assert mock_trigger.call_count == 2
