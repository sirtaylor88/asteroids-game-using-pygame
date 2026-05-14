"""Tests for AsteroidField."""

# pylint: disable=missing-function-docstring,unused-argument

from collections.abc import Generator

import pygame
import pytest

from core.asteroid import Asteroid
from core.asteroid_field import AsteroidField
from core.constants import ASTEROID_SPAWN_RATE


@pytest.fixture()
def field_setup() -> Generator[tuple[AsteroidField, pygame.sprite.Group], None, None]:
    """AsteroidField and asteroids group with containers wired."""
    updatable: pygame.sprite.Group = pygame.sprite.Group()
    asteroids: pygame.sprite.Group = pygame.sprite.Group()
    AsteroidField.containers = (updatable,)  # type: ignore[attr-defined]
    Asteroid.containers = (updatable, asteroids)  # type: ignore[attr-defined]
    af = AsteroidField()
    yield af, asteroids
    del AsteroidField.containers  # type: ignore[attr-defined]
    del Asteroid.containers  # type: ignore[attr-defined]


def test_spawn_timer_starts_at_zero(
    field_setup: tuple[AsteroidField, pygame.sprite.Group],
) -> None:
    field, _ = field_setup
    assert field.spawn_timer == pytest.approx(0.0)


def test_update_increments_spawn_timer(
    field_setup: tuple[AsteroidField, pygame.sprite.Group],
) -> None:
    field, _ = field_setup
    field.update(0.1)
    assert field.spawn_timer == pytest.approx(0.1)


def test_update_below_rate_does_not_spawn(
    field_setup: tuple[AsteroidField, pygame.sprite.Group],
) -> None:
    field, asteroids = field_setup
    before = len(asteroids)
    field.update(ASTEROID_SPAWN_RATE * 0.5)
    assert len(asteroids) == before


def test_update_above_rate_spawns_one_asteroid(
    field_setup: tuple[AsteroidField, pygame.sprite.Group],
) -> None:
    field, asteroids = field_setup
    before = len(asteroids)
    field.update(ASTEROID_SPAWN_RATE + 0.01)
    assert len(asteroids) == before + 1


def test_update_resets_timer_after_spawn(
    field_setup: tuple[AsteroidField, pygame.sprite.Group],
) -> None:
    field, _ = field_setup
    field.update(ASTEROID_SPAWN_RATE + 0.01)
    assert field.spawn_timer == pytest.approx(0.0)


def test_spawn_places_asteroid_at_given_position(
    field_setup: tuple[AsteroidField, pygame.sprite.Group],
) -> None:
    field, asteroids = field_setup
    before = len(asteroids)
    field.spawn(
        20.0,
        pygame.Vector2(100.0, 200.0),
        pygame.Vector2(1.0, 0.0),
    )
    assert len(asteroids) == before + 1
    new_asteroid = list(asteroids)[-1]
    assert new_asteroid.position.x == pytest.approx(100.0)
    assert new_asteroid.position.y == pytest.approx(200.0)


def test_spawn_sets_asteroid_velocity(
    field_setup: tuple[AsteroidField, pygame.sprite.Group],
) -> None:
    field, asteroids = field_setup
    field.spawn(
        20.0,
        pygame.Vector2(0.0, 0.0),
        pygame.Vector2(50.0, 30.0),
    )
    new_asteroid = list(asteroids)[-1]
    assert new_asteroid.velocity.x == pytest.approx(50.0)
    assert new_asteroid.velocity.y == pytest.approx(30.0)
