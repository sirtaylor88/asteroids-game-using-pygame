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
