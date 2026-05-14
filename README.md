# 🚀 Asteroids Game

> A clone of the classic Asteroids arcade game built with **Python 3.13** and **pygame**.

![Python](https://img.shields.io/badge/python-3.13-blue?logo=python&logoColor=white)
![pygame](https://img.shields.io/badge/pygame-2.6.1-green?logo=python)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

---

## Table of Contents

- [Getting Started](#getting-started)
- [Docker](#docker)
- [Controls](#controls)
- [Gameplay](#gameplay)
- [Development](#development)
- [Documentation](#documentation)

---

## Getting Started

Requires **Python 3.13** and [uv](https://docs.astral.sh/uv/).

```bash
# Install dependencies
uv sync --all-groups

# Run the game
uv run main.py
```

---

## Docker

Requires Docker. The image sets `SDL_AUDIODRIVER=dummy` automatically; you must
forward your X11 display so pygame can open a window.

```bash
# Build
docker build -t asteroids .

# Run (Linux with X11)
xhost +local:docker
docker run --rm \
  -e DISPLAY=$DISPLAY \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  asteroids
```

> **macOS / Windows** — install [XQuartz](https://www.xquartz.org/) (macOS) or
> [VcXsrv](https://sourceforge.net/projects/vcxsrv/) (Windows), start it, then
> set `DISPLAY` accordingly before running the command above.

---

## Controls

| Key | Action |
|-----|--------|
| `W` / `↑` | Thrust forward |
| `S` / `↓` | Thrust backward |
| `A` / `←` | Rotate left |
| `D` / `→` | Rotate right |
| `Space` | Shoot |

---

## Gameplay

- Asteroids spawn continuously from the screen edges and drift inward.
- Shoot an asteroid to split it into two smaller, faster ones.
- Small asteroids (minimum radius) are destroyed outright when shot.
- The game ends when an asteroid collides with your ship.

---

## Development

### Code quality

```bash
uv run ruff check .          # lint (includes import sorting)
uv run ruff format --check . # formatting
uv run pylint *.py           # extended lint
uv run mypy .                # type checking
uv run bandit -r .           # security scan
```

### Tests

```bash
uv run pytest                              # all tests
uv run pytest tests/test_asteroid.py      # single module
uv run pytest --cov                        # with coverage report
```

### Documentation

```bash
make -C docs html                                        # one-shot build
uv run sphinx-autobuild docs/source docs/_build          # live-reload at http://127.0.0.1:8000
```

---

## Documentation

Full API reference and architecture notes are in the [`docs/`](docs/) directory.
Build and open `docs/_build/index.html` in a browser after running `sphinx-build`.

---

## License

[MIT](LICENSE) © 2024 Nhat Tai NGUYEN
