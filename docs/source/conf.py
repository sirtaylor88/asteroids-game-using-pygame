"""Sphinx configuration for the Asteroids game."""

# pylint: skip-file

import os
import sys

sys.path.insert(0, os.path.abspath("../.."))  # project root

project = "Asteroids Game"
author = "sirtaylor88"
release = "0.1.0"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx_copybutton",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "_templates"]

html_theme = "alabaster"
html_theme_options = {
    "description": "A pygame clone of the classic Asteroids arcade game.",
    "github_user": "sirtaylor88",
    "github_repo": "asteroids-game-using-pygame",
    "fixed_sidebar": True,
}

autodoc_member_order = "bysource"
autodoc_typehints = "none"
napoleon_google_docstring = True
