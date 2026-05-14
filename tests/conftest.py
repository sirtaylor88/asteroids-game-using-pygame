"""Pytest configuration: initialise pygame with a headless dummy driver."""

import os
from collections.abc import Generator

import pygame
import pytest


@pytest.fixture(autouse=True)
def init_pygame() -> Generator[None, None, None]:
    """Start and stop pygame around every test."""
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
    pygame.init()
    yield
    pygame.quit()
