"""Debug loggers that write game state and events to JSONL files."""

# pylint: disable=invalid-name,global-statement

import inspect
import json
import math
from datetime import datetime
from typing import Any

__all__ = ["log_state", "log_event"]

_FPS = 60
_MAX_SECONDS = 16
_SPRITE_SAMPLE_LIMIT = 10  # Maximum number of sprites to log per group

_frame_count = 0
_state_log_initialized = False
_event_log_initialized = False
_start_time = datetime.now()


def _sprite_to_dict(sprite: Any) -> dict[str, Any]:
    """Serialise a single sprite's observable attributes to a plain dict.

    Args:
        sprite (Any): Any object that may carry ``position``, ``velocity``,
            ``radius``, or ``rotation`` attributes.

    Returns:
        dict[str, Any]: Mapping of attribute name to rounded value.
    """
    info: dict[str, Any] = {"type": sprite.__class__.__name__}
    if hasattr(sprite, "position"):
        info["pos"] = [round(sprite.position.x, 2), round(sprite.position.y, 2)]
    if hasattr(sprite, "velocity"):
        info["vel"] = [round(sprite.velocity.x, 2), round(sprite.velocity.y, 2)]
    if hasattr(sprite, "radius"):
        info["rad"] = sprite.radius
    if hasattr(sprite, "rotation"):
        info["rot"] = round(sprite.rotation, 2)
    return info


def _group_to_entry(group: Any) -> dict[str, Any]:
    """Serialise a sprite Group into a count + sampled sprites list.

    Args:
        group (Any): A pygame sprite Group (or compatible iterable).

    Returns:
        dict[str, Any]: ``{"count": int, "sprites": list}`` entry.
    """
    sprites_data = []
    for i, sprite in enumerate(group):
        if i >= _SPRITE_SAMPLE_LIMIT:
            break
        sprites_data.append(_sprite_to_dict(sprite))
    return {"count": len(group), "sprites": sprites_data}


def _scan_locals(
    local_vars: dict[str, Any],
) -> tuple[list[Any], dict[str, Any]]:
    """Extract screen size and sprite data from a caller's local variables.

    Args:
        local_vars (dict[str, Any]): A copy of ``frame.f_back.f_locals``.

    Returns:
        tuple[list[Any], dict[str, Any]]: ``(screen_size, game_state)`` where
        ``screen_size`` is ``[w, h]`` if a Surface was found (else ``[]``) and
        ``game_state`` maps variable names to serialised sprite data.
    """
    screen_size: list[Any] = []
    game_state: dict[str, Any] = {}
    for key, value in local_vars.items():
        if "pygame" in str(type(value)) and hasattr(value, "get_size"):
            screen_size = list(value.get_size())
        if hasattr(value, "__class__") and "Group" in value.__class__.__name__:
            game_state[key] = _group_to_entry(value)
        if len(game_state) == 0 and hasattr(value, "position"):
            game_state[key] = _sprite_to_dict(value)
    return screen_size, game_state


def log_state() -> None:
    """Snapshot caller's game state to ``game_state.jsonl`` once per second.

    Inspects the caller's local variables for pygame sprite Groups and
    individual sprites that carry ``position``, ``velocity``, ``radius``, or
    ``rotation`` attributes.  Stops logging after ``_MAX_SECONDS`` seconds.
    Must be called from inside the game loop (uses ``inspect.currentframe``).
    """
    global _frame_count, _state_log_initialized

    if _frame_count > _FPS * _MAX_SECONDS:
        return

    _frame_count += 1
    if _frame_count % _FPS != 0:
        return

    now = datetime.now()

    frame = inspect.currentframe()
    if frame is None:
        return

    frame_back = frame.f_back
    if frame_back is None:
        return

    screen_size, game_state = _scan_locals(frame_back.f_locals.copy())

    entry = {
        "timestamp": now.strftime("%H:%M:%S.%f")[:-3],
        "elapsed_s": math.floor((now - _start_time).total_seconds()),
        "frame": _frame_count,
        "screen_size": screen_size,
        **game_state,
    }

    mode = "w" if not _state_log_initialized else "a"
    with open("game_state.jsonl", mode, encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

    _state_log_initialized = True


def log_event(event_type: str, **details: Any) -> None:
    """Append a structured event record to ``game_events.jsonl``.

    Args:
        event_type (str): Label for the event (e.g. ``"shot_fired"``, ``"collision"``).
        **details (Any): Arbitrary keyword arguments merged into the event record.
    """
    global _event_log_initialized

    now = datetime.now()

    event = {
        "timestamp": now.strftime("%H:%M:%S.%f")[:-3],
        "elapsed_s": math.floor((now - _start_time).total_seconds()),
        "frame": _frame_count,
        "type": event_type,
        **details,
    }

    mode = "w" if not _event_log_initialized else "a"
    with open("game_events.jsonl", mode, encoding="utf-8") as f:
        f.write(json.dumps(event) + "\n")

    _event_log_initialized = True
