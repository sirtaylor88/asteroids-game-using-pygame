# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

This project uses [uv](https://docs.astral.sh/uv/) for dependency management (Python 3.13).

```bash
# Install dependencies
uv sync --all-groups

# Run the game
uv run main.py

# Lint
uv run ruff check .
uv run ruff format --check .
uv run pylint *.py
uv run mypy .

# Security scan
uv run bandit -r .

# Tests
uv run pytest
uv run pytest tests/test_foo.py::test_bar  # single test
uv run pytest --cov                        # with coverage

# Docs (source in docs/source/, output in docs/_build/)
make -C docs html
uv run sphinx-autobuild docs/source docs/_build
```

## Architecture

All game objects inherit from `CircleShape` (`circleshape.py`), which extends `pygame.sprite.Sprite`. It holds `position` (Vector2), `velocity` (Vector2), and `radius`, and implements circle-circle collision via `check_collision`. Subclasses must implement `draw(screen)` and `update(dt)`.

**Sprite group wiring** — `main.py` assigns class-level `containers` tuples before instantiation. pygame automatically registers each new instance into those groups. Four groups exist: `updatable`, `drawable`, `asteroids`, `shots`. The game loop iterates these groups directly.

**Game loop** (`main.py:main`): fill → draw → update → collision check, at 60 FPS. `dt` is seconds per frame (float). All movement and timing is multiplied by `dt` for frame-rate independence.

**Asteroid splitting** (`asteroid.py:Asteroid.split`): on hit, the asteroid kills itself; if `radius > ASTEROID_MIN_RADIUS`, it spawns two smaller asteroids at randomized angles (±20–50°) with `radius - ASTEROID_MIN_RADIUS` and 1.2× speed.

**Shooting cooldown** (`player.py:Player`): `self.cooldown` counts down each frame; `shoot()` is a no-op while it's positive. `Shot` inherits `CircleShape` and moves purely by velocity.

**AsteroidField** (`asteroidfield.py`) is a sprite that lives only in `updatable`. It spawns one asteroid every `ASTEROID_SPAWN_RATE` seconds from a randomly chosen screen edge, directed inward with ±30° random deviation.

All tuneable values live in `constants.py`.

**Logging** (`logger.py`): `log_state()` snapshots sprite group state to `game_state.jsonl` once per second for the first 16 seconds. `log_event()` appends structured events to `game_events.jsonl`. Both files are gitignored.
