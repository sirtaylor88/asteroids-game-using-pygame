"""Tests for CircleShape base class."""

import pygame
import pytest

from core.circle_shape import CircleShape


class _Shape(CircleShape):
    """Minimal concrete subclass for testing."""

    def draw(self, screen: pygame.Surface) -> None:
        """No-op draw implementation."""

    def update(self, dt: float) -> None:
        """No-op update implementation."""


def test_position_stored_correctly() -> None:
    """CircleShape stores the x/y constructor arguments as a Vector2 position."""
    shape = _Shape(
        3.5,
        7.2,
        10,
    )
    assert shape.position.x == pytest.approx(3.5)
    assert shape.position.y == pytest.approx(7.2)


def test_initial_velocity_is_zero() -> None:
    """CircleShape initialises velocity to the zero vector."""
    shape = _Shape(
        0,
        0,
        5,
    )
    assert shape.velocity == pygame.Vector2(0, 0)


def test_check_collision_overlapping() -> None:
    """check_collision returns True when circles overlap."""
    a = _Shape(0, 0, 10)
    b = _Shape(5, 0, 10)
    assert a.check_collision(b) is True


def test_check_collision_touching_is_not_collision() -> None:
    """check_collision returns False when circles merely touch (strict less-than)."""
    # Distance exactly equals sum of radii — strict < means no collision
    a = _Shape(0, 0, 10)
    b = _Shape(20, 0, 10)
    assert a.check_collision(b) is False


def test_check_collision_separate() -> None:
    """check_collision returns False when circles are well apart."""
    a = _Shape(
        0,
        0,
        5,
    )
    b = _Shape(
        100,
        0,
        5,
    )
    assert a.check_collision(b) is False


def test_check_collision_symmetric() -> None:
    """check_collision gives the same result regardless of which object calls it."""
    a = _Shape(
        0,
        0,
        8,
    )
    b = _Shape(
        10,
        0,
        8,
    )
    assert a.check_collision(b) == b.check_collision(a)
