Development
===========

Prerequisites
-------------

* `Python 3.13 <https://www.python.org/downloads/>`_
* `uv <https://docs.astral.sh/uv/>`_ — fast Python package and project manager

.. code-block:: bash

   uv sync --all-groups        # install all dependencies
   uv run pre-commit install   # register git hooks (one-time)

Pre-commit Hooks
----------------

All quality checks run automatically on every ``git commit`` via
`pre-commit <https://pre-commit.com/>`_.

.. list-table::
   :header-rows: 1
   :widths: 18 42 40

   * - Hook
     - Purpose
     - Docs
   * - ruff
     - Lint + auto-fix import order
     - `docs.astral.sh/ruff <https://docs.astral.sh/ruff/>`_
   * - ruff-format
     - Opinionated formatter (line length 88)
     - `ruff formatter <https://docs.astral.sh/ruff/formatter/>`_
   * - pylint
     - Extended static analysis
     - `pylint.readthedocs.io <https://pylint.readthedocs.io/>`_
   * - mypy
     - Static type checking
     - `mypy.readthedocs.io <https://mypy.readthedocs.io/>`_
   * - pydocstyle
     - Google-convention docstring style
     - `pydocstyle.org <https://www.pydocstyle.org/>`_
   * - bandit
     - Security vulnerability scan
     - `bandit.readthedocs.io <https://bandit.readthedocs.io/>`_
   * - sphinx-lint
     - RST syntax checker for docs
     - `sphinx-lint <https://github.com/sphinx-contrib/sphinx-lint>`_
   * - pytest-cov
     - Test suite with coverage report
     - `docs.pytest.org <https://docs.pytest.org/>`_

Tool configuration lives in ``pyproject.toml`` under ``[tool.ruff]``,
``[tool.pylint.*]``, ``[tool.bandit]``, ``[tool.pydocstyle]``,
``[tool.pytest.ini_options]``, and ``[tool.coverage.run]``.

Testing
-------

Tests use `pytest <https://docs.pytest.org/>`_ with a headless
`SDL <https://www.libsdl.org/>`_ driver (``SDL_VIDEODRIVER=dummy``) so no
display is required. The ``init_pygame`` fixture in ``tests/conftest.py``
initialises and tears down pygame around every test automatically.

.. code-block:: bash

   uv run pytest                         # all tests
   uv run pytest tests/test_asteroid.py  # single module
   uv run pytest -k "split"              # tests matching a keyword
   uv run pytest --cov                   # with HTML/terminal coverage

Test modules:

* ``tests/test_circleshape.py`` — collision geometry
* ``tests/test_asteroid.py`` — splitting, movement
* ``tests/test_asteroidfield.py`` — spawn timer, velocity, position
* ``tests/test_player.py`` — rotation, movement, shooting cooldown, Shot
* ``tests/test_logger.py`` — JSONL output, fps guard, max-seconds cap
* ``tests/test_utils.py`` — rendering helpers, explosion rings, game-over screen, collision logic

Documentation
-------------

Built with `Sphinx <https://www.sphinx-doc.org/>`_ using:

* `autodoc <https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html>`_
  — generates API pages from docstrings
* `Napoleon <https://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html>`_
  — parses Google-style docstrings
* `sphinx-copybutton <https://sphinx-copybutton.readthedocs.io/>`_
  — adds copy buttons to code blocks

.. code-block:: bash

   make -C docs html                               # one-shot build
   uv run sphinx-autobuild docs/source docs/_build # live-reload

Packaging
---------

Standalone executables are produced with
`PyInstaller <https://pyinstaller.org/>`_ using the ``asteroids.spec``
spec file at the repository root.

.. list-table::
   :header-rows: 1
   :widths: 20 30 50

   * - Platform
     - Artifact name
     - Output path
   * - Windows
     - ``asteroids-windows``
     - ``dist/asteroids.exe``
   * - macOS
     - ``asteroids-macos``
     - ``dist/asteroids``
   * - Linux
     - ``asteroids-linux``
     - ``dist/asteroids``

**Local build** (any platform, requires Python 3.13 and uv):

.. code-block:: bash

   bash scripts/build_exe.sh

The script installs ``libsdl2-dev`` automatically on Linux if it is not
already present, syncs dependencies, and runs PyInstaller.

**CI build** — the ``release`` workflow
(``.github/workflows/release.yml``) runs three parallel jobs (one per
platform) on every ``v*`` tag push and uploads each binary as a workflow
artifact and a GitHub release asset.  It can also be triggered manually
from the *Actions* tab via ``workflow_dispatch``.

Scripts
-------

The ``scripts/`` directory contains two helper scripts:

.. list-table::
   :header-rows: 1
   :widths: 35 65

   * - Script
     - Purpose
   * - ``scripts/build_exe.sh``
     - Build a standalone executable locally on any platform.
       Installs ``libsdl2-dev`` on Linux if absent, syncs dependencies,
       then runs PyInstaller.
   * - ``scripts/screenshot.py``
     - Render 360 frames of gameplay and save the result to
       ``docs/source/_static/screenshot.png`` (used as the README
       preview image).  Accepts an optional output path argument.

.. code-block:: bash

   bash scripts/build_exe.sh                    # build executable
   uv run scripts/screenshot.py                 # regenerate screenshot
   uv run scripts/screenshot.py path/to/out.png # custom output path
