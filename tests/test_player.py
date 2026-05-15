"""Tests for Player and Shot."""

# pylint: disable=missing-function-docstring,protected-access

import pygame
import pytest

from core.constants import (
    PLAYER_INVINCIBILITY_DURATION,
    PLAYER_MAX_HP,
    PLAYER_SHOOT_COOLDOWN,
    PLAYER_SPEED,
    PLAYER_TURN_SPEED,
)
from core.player import Player, Shot


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


def test_ship_points_returns_five_vector2_points(player: Player) -> None:
    points = player._ship_points()
    assert len(points) == 5
    for p in points:
        assert isinstance(p, pygame.Vector2)


def test_thrusting_defaults_to_false(player: Player) -> None:
    assert player.thrusting is False


def test_hp_defaults_to_max(player: Player) -> None:
    assert player.hp == PLAYER_MAX_HP


def test_invincible_timer_defaults_to_zero(player: Player) -> None:
    assert player.invincible_timer == pytest.approx(0.0)


def test_take_damage_reduces_hp(player: Player) -> None:
    player.take_damage(3)
    assert player.hp == PLAYER_MAX_HP - 3


def test_take_damage_clamps_hp_to_zero(player: Player) -> None:
    player.take_damage(PLAYER_MAX_HP + 5)
    assert player.hp == 0


def test_take_damage_sets_invincibility(player: Player) -> None:
    player.take_damage(1)
    assert player.invincible_timer == pytest.approx(PLAYER_INVINCIBILITY_DURATION)


def test_take_damage_blocked_when_invincible(player: Player) -> None:
    player.take_damage(1)
    hp_after_first = player.hp
    player.take_damage(1)
    assert player.hp == hp_after_first


def test_update_decrements_invincible_timer(player: Player) -> None:
    player.take_damage(1)
    player.update(0.5)
    assert player.invincible_timer == pytest.approx(PLAYER_INVINCIBILITY_DURATION - 0.5)


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
