"""
Unit tests for Typer CLI commands (version, list, capture, send).
"""

from unittest.mock import AsyncMock, patch

from typer.testing import CliRunner

from librechat_tmux_bridge.cli import app
from librechat_tmux_bridge.core.models import TmuxSession
from librechat_tmux_bridge.infrastructure.taps import DiagnosticTap, format_agent_feedback_envelope

runner = CliRunner()


def test_cli_version():
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "LibreChatTmuxBridge v0.1.0" in result.stdout


def test_cli_list_sessions():
    with patch(
        "librechat_tmux_bridge.cli.TmuxDriver.list_sessions",
        new=AsyncMock(
            return_value=[
                TmuxSession(
                    name="work", windows=2, created=1700000000, attached=True, active_window="agy"
                )
            ]
        ),
    ):
        result = runner.invoke(app, ["list"])
        assert result.exit_code == 0
        assert "Found 1 active session" in result.stdout
        assert "work" in result.stdout

    with patch(
        "librechat_tmux_bridge.cli.TmuxDriver.list_sessions", new=AsyncMock(return_value=[])
    ):
        res_empty = runner.invoke(app, ["list"])
        assert res_empty.exit_code == 0
        assert "No active tmux sessions found" in res_empty.stdout


def test_cli_capture():
    with patch(
        "librechat_tmux_bridge.cli.TmuxDriver.capture_pane",
        new=AsyncMock(return_value="\x1b[32mhello terminal\x1b[0m"),
    ):
        res = runner.invoke(app, ["capture", "work", "--lines", "20"])
        assert res.exit_code == 0
        assert "hello terminal" in res.stdout

        res_raw = runner.invoke(app, ["capture", "work", "--raw"])
        assert res_raw.exit_code == 0
        assert "\x1b[32m" in res_raw.stdout

    with patch(
        "librechat_tmux_bridge.cli.TmuxDriver.capture_pane",
        new=AsyncMock(side_effect=Exception("Pane fail")),
    ):
        res_fail = runner.invoke(app, ["capture", "work"])
        assert res_fail.exit_code == 1
        assert "Error: Pane fail" in res_fail.output


def test_cli_send():
    with patch("librechat_tmux_bridge.cli.TmuxDriver.send_keys", new=AsyncMock(return_value=True)):
        res = runner.invoke(app, ["send", "work", "ls -l"])
        assert res.exit_code == 0
        assert "Successfully sent to 'work'" in res.stdout

        res_no_enter = runner.invoke(app, ["send", "work", "q", "--no-enter"])
        assert res_no_enter.exit_code == 0

    with patch(
        "librechat_tmux_bridge.cli.TmuxDriver.send_keys",
        new=AsyncMock(side_effect=Exception("Send fail")),
    ):
        res_fail = runner.invoke(app, ["send", "work", "ls"])
        assert res_fail.exit_code == 1
        assert "Error: Send fail" in res_fail.output


def test_diagnostic_tap_operations():
    tap = DiagnosticTap(capacity=5)
    tap.record_event("request", {"session": "s1"})
    tap.record_event("error", {"err": "test"})
    assert tap.request_count == 1
    assert tap.error_count == 1
    assert len(tap.get_recent_events()) == 2

    stats = tap.stats()
    assert stats["total_requests"] == 1
    assert stats["total_errors"] == 1
    assert stats["buffer_depth"] == 2

    tap.clear()
    assert tap.request_count == 0
    assert len(tap.get_recent_events()) == 0

    envelope_json = format_agent_feedback_envelope(
        test_name="sample_test",
        inputs={"a": 1},
        assumptions=["true"],
        active_settings=None,
        action_history=[],
        output_delta={},
        captured_logs=[],
        reproduction_command="pytest",
    )
    assert "sample_test" in envelope_json
    assert "FAILED" in envelope_json
