"""Tests for Player and Shot."""

# pylint: disable=protected-access

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
    """Player instance at (100, 100) with no containers set."""
    return Player(100.0, 100.0)


# ---------------------------------------------------------------------------
# Player
# ---------------------------------------------------------------------------


def test_triangle_returns_three_vector2_points(player: Player) -> None:
    """triangle() returns exactly three pygame.Vector2 vertices."""
    points = player.triangle()
    assert len(points) == 3
    for p in points:
        assert isinstance(p, pygame.Vector2)


def test_ship_points_returns_five_vector2_points(player: Player) -> None:
    """_ship_points() returns exactly five hull vertices."""
    points = player._ship_points()
    assert len(points) == 5
    for p in points:
        assert isinstance(p, pygame.Vector2)


def test_thrusting_defaults_to_false(player: Player) -> None:
    """Player starts with thrusting set to False."""
    assert player.thrusting is False


def test_hp_defaults_to_max(player: Player) -> None:
    """Player starts at full HP."""
    assert player.hp == PLAYER_MAX_HP


def test_invincible_timer_defaults_to_zero(player: Player) -> None:
    """Player starts with no invincibility active."""
    assert player.invincible_timer == pytest.approx(0.0)


def test_take_damage_reduces_hp(player: Player) -> None:
    """take_damage() subtracts the given amount from HP."""
    player.take_damage(3)
    assert player.hp == PLAYER_MAX_HP - 3


def test_take_damage_clamps_hp_to_zero(player: Player) -> None:
    """take_damage() never reduces HP below zero."""
    player.take_damage(PLAYER_MAX_HP + 5)
    assert player.hp == 0


def test_take_damage_sets_invincibility(player: Player) -> None:
    """take_damage() starts the invincibility window."""
    player.take_damage(1)
    assert player.invincible_timer == pytest.approx(PLAYER_INVINCIBILITY_DURATION)


def test_take_damage_blocked_when_invincible(player: Player) -> None:
    """take_damage() is a no-op while the invincibility timer is active."""
    player.take_damage(1)
    hp_after_first = player.hp
    player.take_damage(1)
    assert player.hp == hp_after_first


def test_update_decrements_invincible_timer(player: Player) -> None:
    """update() ticks down invincible_timer by dt."""
    player.take_damage(1)
    player.update(0.5)
    assert player.invincible_timer == pytest.approx(PLAYER_INVINCIBILITY_DURATION - 0.5)


def test_rotate_increases_rotation_by_turn_speed_times_dt(player: Player) -> None:
    """rotate() adds PLAYER_TURN_SPEED * dt to the rotation angle."""
    player.rotation = 0.0
    player.rotate(1.0)
    assert player.rotation == pytest.approx(PLAYER_TURN_SPEED)


def test_rotate_by_zero_does_not_change_rotation(player: Player) -> None:
    """rotate(0) leaves rotation unchanged."""
    player.rotation = 45.0
    player.rotate(0.0)
    assert player.rotation == pytest.approx(45.0)


def test_move_forward_increases_y(player: Player) -> None:
    """move() with positive dt advances position in the forward direction."""
    # rotation=0 → forward vector is (0, 1)
    player.rotation = 0.0
    initial_y = player.position.y
    player.move(1.0)
    assert player.position.y == pytest.approx(initial_y + PLAYER_SPEED)


def test_move_backward_decreases_y(player: Player) -> None:
    """move() with negative dt retreats position opposite the forward direction."""
    player.rotation = 0.0
    initial_y = player.position.y
    player.move(-1.0)
    assert player.position.y == pytest.approx(initial_y - PLAYER_SPEED)


def test_shoot_sets_cooldown(player: Player) -> None:
    """shoot() resets the cooldown to PLAYER_SHOOT_COOLDOWN."""
    Shot.containers = (pygame.sprite.Group(),)  # type: ignore[attr-defined]
    player.cooldown = 0.0
    player.shoot()
    assert player.cooldown == pytest.approx(PLAYER_SHOOT_COOLDOWN)
    del Shot.containers  # type: ignore[attr-defined]


def test_shoot_blocked_when_cooldown_active(player: Player) -> None:
    """shoot() is a no-op while the cooldown timer is positive."""
    player.cooldown = 1.0
    player.shoot()
    assert player.cooldown == pytest.approx(1.0)


def test_draw_normal(player: Player) -> None:
    """draw() renders the ship hull without raising."""
    screen = pygame.display.set_mode((200, 200))
    player.draw(screen)


def test_draw_while_thrusting(player: Player) -> None:
    """draw() renders the thrust flame when thrusting is True."""
    screen = pygame.display.set_mode((200, 200))
    player.thrusting = True
    player.draw(screen)


def test_draw_returns_early_when_invincible_and_hidden(player: Player) -> None:
    """draw() skips rendering on the hidden phase of the invincibility flicker."""
    screen = pygame.display.set_mode((200, 200))
    # int(0.25 * 8) = 2; 2 % 2 == 0 → hidden frame
    player.invincible_timer = 0.25
    player.draw(screen)


def test_update_moves_forward_on_w_key(
    player: Player, monkeypatch: pytest.MonkeyPatch
) -> None:
    """update() calls move() when W is held."""

    class _Keys:
        def __getitem__(self, k: int) -> bool:
            return k == pygame.K_w

    monkeypatch.setattr(pygame.key, "get_pressed", _Keys)
    initial_y = player.position.y
    player.update(0.1)
    assert player.position.y != pytest.approx(initial_y)


def test_update_moves_backward_on_s_key(
    player: Player, monkeypatch: pytest.MonkeyPatch
) -> None:
    """update() calls move(-dt) when S is held."""

    class _Keys:
        def __getitem__(self, k: int) -> bool:
            return k == pygame.K_s

    monkeypatch.setattr(pygame.key, "get_pressed", _Keys)
    initial_y = player.position.y
    player.update(0.1)
    assert player.position.y != pytest.approx(initial_y)


def test_update_rotates_left_on_a_key(
    player: Player, monkeypatch: pytest.MonkeyPatch
) -> None:
    """update() calls rotate(dt) when A is held."""

    class _Keys:
        def __getitem__(self, k: int) -> bool:
            return k == pygame.K_a

    monkeypatch.setattr(pygame.key, "get_pressed", _Keys)
    initial_rotation = player.rotation
    player.update(0.1)
    assert player.rotation != pytest.approx(initial_rotation)


def test_update_rotates_right_on_d_key(
    player: Player, monkeypatch: pytest.MonkeyPatch
) -> None:
    """update() calls rotate(-dt) when D is held."""

    class _Keys:
        def __getitem__(self, k: int) -> bool:
            return k == pygame.K_d

    monkeypatch.setattr(pygame.key, "get_pressed", _Keys)
    initial_rotation = player.rotation
    player.update(0.1)
    assert player.rotation != pytest.approx(initial_rotation)


def test_update_shoots_on_space_key(
    player: Player, monkeypatch: pytest.MonkeyPatch
) -> None:
    """update() calls shoot() when SPACE is held."""
    Shot.containers = (pygame.sprite.Group(),)  # type: ignore[attr-defined]

    class _Keys:
        def __getitem__(self, k: int) -> bool:
            return k == pygame.K_SPACE

    monkeypatch.setattr(pygame.key, "get_pressed", _Keys)
    player.update(0.1)
    assert player.cooldown > 0
    del Shot.containers  # type: ignore[attr-defined]


# ---------------------------------------------------------------------------
# Shot
# ---------------------------------------------------------------------------


def test_shot_update_moves_position_by_velocity_times_dt() -> None:
    """Shot.update() advances position by velocity * dt."""
    shot = Shot(0.0, 0.0)
    shot.velocity = pygame.Vector2(100.0, 200.0)
    shot.update(0.1)
    assert shot.position.x == pytest.approx(10.0)
    assert shot.position.y == pytest.approx(20.0)


def test_shot_initial_position_matches_constructor() -> None:
    """Shot stores the constructor x/y as its initial position."""
    shot = Shot(50.0, 75.0)
    assert shot.position.x == pytest.approx(50.0)
    assert shot.position.y == pytest.approx(75.0)


def test_shot_draw_with_zero_velocity() -> None:
    """Shot.draw() renders the bullet circle when velocity is zero (no tail)."""
    screen = pygame.display.set_mode((200, 200))
    shot = Shot(50.0, 50.0)
    shot.velocity = pygame.Vector2(0, 0)
    shot.draw(screen)


def test_shot_draw_with_nonzero_velocity() -> None:
    """Shot.draw() renders a tail line plus the bullet circle when velocity > 0."""
    screen = pygame.display.set_mode((200, 200))
    shot = Shot(50.0, 50.0)
    shot.velocity = pygame.Vector2(100.0, 0.0)
    shot.draw(screen)
