"""Tests for Player and Shot."""

# pylint: disable=missing-function-docstring

import pygame
import pytest

from constants import PLAYER_SHOOT_COOLDOWN, PLAYER_SPEED, PLAYER_TURN_SPEED
from player import Player, Shot


@pytest.fixture()
def player() -> Player:
    return Player(100.0, 100.0)


# ---------------------------------------------------------------------------
# Player
# ---------------------------------------------------------------------------


def test_triangle_returns_three_vector2_points(player: Player) -> None:
    points = player.triangle()
    assert len(points) == 3
    for p in points:
        assert isinstance(p, pygame.Vector2)


def test_rotate_increases_rotation_by_turn_speed_times_dt(player: Player) -> None:
    player.rotation = 0.0
    player.rotate(1.0)
    assert player.rotation == pytest.approx(PLAYER_TURN_SPEED)


def test_rotate_by_zero_does_not_change_rotation(player: Player) -> None:
    player.rotation = 45.0
    player.rotate(0.0)
    assert player.rotation == pytest.approx(45.0)


def test_move_forward_increases_y(player: Player) -> None:
    # rotation=0 → forward vector is (0, 1)
    player.rotation = 0.0
    initial_y = player.position.y
    player.move(1.0)
    assert player.position.y == pytest.approx(initial_y + PLAYER_SPEED)


def test_move_backward_decreases_y(player: Player) -> None:
    player.rotation = 0.0
    initial_y = player.position.y
    player.move(-1.0)
    assert player.position.y == pytest.approx(initial_y - PLAYER_SPEED)


def test_shoot_sets_cooldown(player: Player) -> None:
    player.cooldown = 0.0
    player.shoot()
    assert player.cooldown == pytest.approx(PLAYER_SHOOT_COOLDOWN)


def test_shoot_blocked_when_cooldown_active(player: Player) -> None:
    player.cooldown = 1.0
    player.shoot()
    assert player.cooldown == pytest.approx(1.0)


# ---------------------------------------------------------------------------
# Shot
# ---------------------------------------------------------------------------


def test_shot_update_moves_position_by_velocity_times_dt() -> None:
    shot = Shot(0.0, 0.0)
    shot.velocity = pygame.Vector2(100.0, 200.0)
    shot.update(0.1)
    assert shot.position.x == pytest.approx(10.0)
    assert shot.position.y == pytest.approx(20.0)


def test_shot_initial_position_matches_constructor() -> None:
    shot = Shot(50.0, 75.0)
    assert shot.position.x == pytest.approx(50.0)
    assert shot.position.y == pytest.approx(75.0)
