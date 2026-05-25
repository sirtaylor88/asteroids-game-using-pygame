"""Tests for logger module."""

import inspect
import json
from pathlib import Path
from types import SimpleNamespace

import pygame
import pytest

import logger as log_module
from core.asteroid import Asteroid
from core.constants import ASTEROID_MIN_RADIUS
from logger import _group_to_entry, _scan_locals, _sprite_to_dict, log_event, log_state


@pytest.fixture(autouse=True)
def reset_logger(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Reset all logger globals and redirect file writes to tmp_path."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(log_module, "_frame_count", 0)
    monkeypatch.setattr(log_module, "_state_log_initialized", False)
    monkeypatch.setattr(log_module, "_event_log_initialized", False)


def test_log_event_creates_jsonl_file(tmp_path: Path) -> None:
    """log_event() creates game_events.jsonl on first call."""
    log_event("fired")
    assert (tmp_path / "game_events.jsonl").exists()


def test_log_event_record_has_type_and_details(tmp_path: Path) -> None:
    """log_event() writes the event type and extra keyword arguments."""
    log_event("collision", x=50.0, y=75.0)
    record = json.loads((tmp_path / "game_events.jsonl").read_text(encoding="utf-8"))
    assert record["type"] == "collision"
    assert record["x"] == pytest.approx(50.0)
    assert record["y"] == pytest.approx(75.0)


def test_log_event_successive_calls_append(tmp_path: Path) -> None:
    """log_event() appends each new record as a separate JSONL line."""
    log_event("first")
    log_event("second")
    lines = (tmp_path / "game_events.jsonl").read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2
    assert json.loads(lines[1])["type"] == "second"


def test_log_state_does_not_write_before_fps_frames(tmp_path: Path) -> None:
    """log_state() skips writing until a full FPS interval has elapsed."""
    log_state()  # frame 1 of 60 — threshold not yet reached
    assert not (tmp_path / "game_state.jsonl").exists()


def test_log_state_writes_at_fps_interval(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """log_state() writes a snapshot exactly once per FPS interval."""
    monkeypatch.setattr(log_module, "_FPS", 1)
    log_state()  # frame 1, 1 % 1 == 0 → writes
    assert (tmp_path / "game_state.jsonl").exists()


def test_log_state_record_is_valid_json(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """log_state() writes valid JSON with timestamp and frame fields."""
    monkeypatch.setattr(log_module, "_FPS", 1)
    log_state()
    record = json.loads((tmp_path / "game_state.jsonl").read_text(encoding="utf-8"))
    assert "timestamp" in record
    assert "frame" in record
    assert record["frame"] == 1


def test_log_state_stops_after_max_seconds(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """log_state() stops writing after _MAX_SECONDS * _FPS frames."""
    monkeypatch.setattr(log_module, "_FPS", 1)
    monkeypatch.setattr(log_module, "_MAX_SECONDS", 1)
    for _ in range(10):
        log_state()
    lines = (tmp_path / "game_state.jsonl").read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2  # only frames 1 and 2 pass the guard


# ---------------------------------------------------------------------------
# _sprite_to_dict
# ---------------------------------------------------------------------------


def test_sprite_to_dict_includes_all_attributes() -> None:
    """_sprite_to_dict() captures position, velocity, radius, and rotation."""
    sprite = SimpleNamespace(
        position=pygame.Vector2(1.5, 2.5),
        velocity=pygame.Vector2(3.0, 4.0),
        radius=10.0,
        rotation=45.0,
    )
    result = _sprite_to_dict(sprite)
    assert result["pos"] == [1.5, 2.5]
    assert result["vel"] == [3.0, 4.0]
    assert result["rad"] == pytest.approx(10.0)
    assert result["rot"] == pytest.approx(45.0)


def test_sprite_to_dict_omits_missing_attributes() -> None:
    """_sprite_to_dict() only includes keys for attributes the sprite has."""
    sprite = SimpleNamespace()
    result = _sprite_to_dict(sprite)
    assert "pos" not in result
    assert "vel" not in result
    assert "rad" not in result
    assert "rot" not in result


# ---------------------------------------------------------------------------
# _group_to_entry
# ---------------------------------------------------------------------------


def test_group_to_entry_serialises_sprites() -> None:
    """_group_to_entry() returns count and a sprites list for a non-empty group."""
    group: pygame.sprite.Group = pygame.sprite.Group()
    Asteroid.containers = (group,)  # type: ignore[attr-defined]
    Asteroid(50, 50, ASTEROID_MIN_RADIUS)
    del Asteroid.containers  # type: ignore[attr-defined]

    entry = _group_to_entry(group)
    assert entry["count"] == 1
    assert len(entry["sprites"]) == 1
    assert "pos" in entry["sprites"][0]


def test_group_to_entry_respects_sample_limit(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """_group_to_entry() stops sampling once _SPRITE_SAMPLE_LIMIT is reached."""
    monkeypatch.setattr(log_module, "_SPRITE_SAMPLE_LIMIT", 1)
    group: pygame.sprite.Group = pygame.sprite.Group()
    Asteroid.containers = (group,)  # type: ignore[attr-defined]
    Asteroid(10, 10, ASTEROID_MIN_RADIUS)
    Asteroid(20, 20, ASTEROID_MIN_RADIUS)
    del Asteroid.containers  # type: ignore[attr-defined]

    entry = _group_to_entry(group)
    assert entry["count"] == 2
    assert len(entry["sprites"]) == 1  # capped at limit


# ---------------------------------------------------------------------------
# _scan_locals
# ---------------------------------------------------------------------------


def test_scan_locals_detects_surface() -> None:
    """_scan_locals() extracts screen_size from a pygame Surface value."""
    screen = pygame.display.set_mode((120, 80))
    size, _ = _scan_locals({"screen": screen})
    assert size == [120, 80]


def test_scan_locals_detects_group() -> None:
    """_scan_locals() serialises a sprite Group found among the locals."""
    group: pygame.sprite.Group = pygame.sprite.Group()
    Asteroid.containers = (group,)  # type: ignore[attr-defined]
    Asteroid(0, 0, ASTEROID_MIN_RADIUS)
    del Asteroid.containers  # type: ignore[attr-defined]

    _, game_state = _scan_locals({"group": group})
    assert "group" in game_state
    assert game_state["group"]["count"] == 1


def test_scan_locals_detects_single_sprite() -> None:
    """_scan_locals() captures a lone sprite with a position when no group exists."""
    sprite = SimpleNamespace(position=pygame.Vector2(5, 10))
    _, game_state = _scan_locals({"sprite": sprite})
    assert "sprite" in game_state
    assert game_state["sprite"]["pos"] == [5.0, 10.0]


# ---------------------------------------------------------------------------
# log_state early-return guards
# ---------------------------------------------------------------------------


def test_log_state_returns_when_frame_is_none(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """log_state() exits silently when inspect.currentframe() returns None."""
    monkeypatch.setattr(log_module, "_FPS", 1)

    def _no_frame() -> None:
        return None

    monkeypatch.setattr(inspect, "currentframe", _no_frame)
    log_state()
    assert not (tmp_path / "game_state.jsonl").exists()


def test_log_state_returns_when_frame_back_is_none(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """log_state() exits silently when the caller frame has no parent."""
    monkeypatch.setattr(log_module, "_FPS", 1)

    class _Frame:
        f_back = None

    def _fake_frame() -> _Frame:
        return _Frame()

    monkeypatch.setattr(inspect, "currentframe", _fake_frame)
    log_state()
    assert not (tmp_path / "game_state.jsonl").exists()
