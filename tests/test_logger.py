"""Tests for logger module."""

# pylint: disable=missing-function-docstring

import json
from pathlib import Path

import pytest

import logger as log_module
from logger import log_event, log_state


@pytest.fixture(autouse=True)
def reset_logger(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Reset all logger globals and redirect file writes to tmp_path."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(log_module, "_frame_count", 0)
    monkeypatch.setattr(log_module, "_state_log_initialized", False)
    monkeypatch.setattr(log_module, "_event_log_initialized", False)


def test_log_event_creates_jsonl_file(tmp_path: Path) -> None:
    log_event("fired")
    assert (tmp_path / "game_events.jsonl").exists()


def test_log_event_record_has_type_and_details(tmp_path: Path) -> None:
    log_event("collision", x=50.0, y=75.0)
    record = json.loads((tmp_path / "game_events.jsonl").read_text(encoding="utf-8"))
    assert record["type"] == "collision"
    assert record["x"] == pytest.approx(50.0)
    assert record["y"] == pytest.approx(75.0)


def test_log_event_successive_calls_append(tmp_path: Path) -> None:
    log_event("first")
    log_event("second")
    lines = (tmp_path / "game_events.jsonl").read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2
    assert json.loads(lines[1])["type"] == "second"


def test_log_state_does_not_write_before_fps_frames(tmp_path: Path) -> None:
    log_state()  # frame 1 of 60 — threshold not yet reached
    assert not (tmp_path / "game_state.jsonl").exists()


def test_log_state_writes_at_fps_interval(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(log_module, "_FPS", 1)
    log_state()  # frame 1, 1 % 1 == 0 → writes
    assert (tmp_path / "game_state.jsonl").exists()


def test_log_state_record_is_valid_json(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(log_module, "_FPS", 1)
    log_state()
    record = json.loads((tmp_path / "game_state.jsonl").read_text(encoding="utf-8"))
    assert "timestamp" in record
    assert "frame" in record
    assert record["frame"] == 1


def test_log_state_stops_after_max_seconds(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(log_module, "_FPS", 1)
    monkeypatch.setattr(log_module, "_MAX_SECONDS", 1)
    for _ in range(10):
        log_state()
    lines = (tmp_path / "game_state.jsonl").read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2  # only frames 1 and 2 pass the guard
