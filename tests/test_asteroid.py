"""Tests for Asteroid."""

# pylint: disable=missing-function-docstring,unused-argument,protected-access

from collections.abc import Generator

import pygame
import pytest

from core.asteroid import Asteroid
from core.constants import ASTEROID_MIN_RADIUS


@pytest.fixture()
def group() -> Generator[pygame.sprite.Group, None, None]:
    """Sprite group that automatically receives new Asteroid instances."""
    g: pygame.sprite.Group = pygame.sprite.Group()
    Asteroid.containers = (g,)  # type: ignore[attr-defined]
    yield g
    del Asteroid.containers  # type: ignore[attr-defined]


def test_split_kills_original(group: pygame.sprite.Group) -> None:
    asteroid = Asteroid(
        100,
        100,
        ASTEROID_MIN_RADIUS * 2,
    )
    asteroid.velocity = pygame.Vector2(1, 0)
    asteroid.split()
    assert not asteroid.alive()


def test_split_large_creates_two_children(group: pygame.sprite.Group) -> None:
    asteroid = Asteroid(
        100,
        100,
        ASTEROID_MIN_RADIUS * 2,
    )
    asteroid.velocity = pygame.Vector2(1, 0)
    before = len(group)
    asteroid.split()
    assert len(group) == before - 1 + 2


def test_split_small_creates_no_children(group: pygame.sprite.Group) -> None:
    asteroid = Asteroid(
        100,
        100,
        ASTEROID_MIN_RADIUS,
    )
    asteroid.velocity = pygame.Vector2(1, 0)
    before = len(group)
    asteroid.split()
    assert len(group) == before - 1


def test_child_radius_is_smaller(group: pygame.sprite.Group) -> None:
    parent_radius = ASTEROID_MIN_RADIUS * 2
    asteroid = Asteroid(
        0,
        0,
        parent_radius,
    )
    asteroid.velocity = pygame.Vector2(1, 0)
    asteroid.split()
    for child in group:
        assert child.radius < parent_radius


def test_child_velocities_are_faster(group: pygame.sprite.Group) -> None:
    asteroid = Asteroid(
        0,
        0,
        ASTEROID_MIN_RADIUS * 2,
    )
    asteroid.velocity = pygame.Vector2(50, 0)
    original_speed = asteroid.velocity.length()
    asteroid.split()
    for child in group:
        assert child.velocity.length() > original_speed


def test_update_moves_position_by_velocity_times_dt() -> None:
    asteroid = Asteroid(
        0,
        0,
        ASTEROID_MIN_RADIUS,
    )
    asteroid.velocity = pygame.Vector2(10, 20)
    asteroid.update(0.5)
    assert asteroid.position.x == pytest.approx(5.0)
    assert asteroid.position.y == pytest.approx(10.0)


def test_asteroid_has_rotation_speed() -> None:
    asteroid = Asteroid(0, 0, ASTEROID_MIN_RADIUS)
    assert isinstance(asteroid.rotation_speed, float)


def test_update_advances_rotation_by_rotation_speed_times_dt() -> None:
    asteroid = Asteroid(0, 0, ASTEROID_MIN_RADIUS)
    asteroid.rotation = 0.0
    speed = asteroid.rotation_speed
    asteroid.update(1.0)
    assert asteroid.rotation == pytest.approx(speed * 1.0)


def test_world_points_count_matches_vertices() -> None:
    asteroid = Asteroid(0, 0, ASTEROID_MIN_RADIUS * 2)
    assert len(asteroid._world_points()) == len(asteroid._vertices)
