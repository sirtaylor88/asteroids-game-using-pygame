"""Tests for core/utils.py rendering and collision helpers."""

import pygame
import pytest

from core.asteroid import Asteroid
from core.constants import (
    ASTEROID_MIN_RADIUS,
    PLAYER_HP_DAMAGE_LARGE,
    PLAYER_HP_DAMAGE_SMALL,
    PLAYER_MAX_HP,
)
from core.player import Player, Shot
from core.utils import (
    check_collisions,
    draw_explosion_rings,
    draw_stars,
    game_over_screen,
    render_hud,
)


@pytest.fixture()
def screen() -> pygame.Surface:
    """200×200 display surface for rendering tests."""
    return pygame.display.set_mode((200, 200))


# ---------------------------------------------------------------------------
# draw_stars
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "stars",
    [
        [(10, 10, 1)],  # size-1: set_at path
        [(10, 10, 2)],  # size-2: draw.circle path
        [],  # empty: no-op
    ],
)
def test_draw_stars(screen: pygame.Surface, stars: list[tuple[int, int, int]]) -> None:
    """draw_stars() renders each star variant without raising."""
    draw_stars(screen, stars)


# ---------------------------------------------------------------------------
# render_hud
# ---------------------------------------------------------------------------


@pytest.fixture()
def hud_screen() -> pygame.Surface:
    """400×200 display surface wide enough for all HUD elements."""
    return pygame.display.set_mode((400, 200))


@pytest.fixture()
def hud_font() -> pygame.font.Font:
    """Default font for HUD tests."""
    return pygame.font.Font(None, 24)


@pytest.mark.parametrize("hp", [PLAYER_MAX_HP, 5, 1, 0])
def test_render_hud_hp_bar(
    hud_screen: pygame.Surface, hud_font: pygame.font.Font, hp: int
) -> None:
    """render_hud() draws the HP bar for every colour threshold including zero."""
    render_hud(hud_screen, hud_font, survival_time=0.0, destroyed=0, hp=hp)


def test_render_hud_formats_minutes(
    hud_screen: pygame.Surface, hud_font: pygame.font.Font
) -> None:
    """render_hud() formats survival_time >= 60 s as MM:SS."""
    render_hud(hud_screen, hud_font, survival_time=65.0, destroyed=3, hp=PLAYER_MAX_HP)


# ---------------------------------------------------------------------------
# draw_explosion_rings
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "elapsed",
    [
        1.5,  # >= threshold: early return
        0.5,  # all three rings active
        0.05,  # only first ring active; others still delayed
    ],
)
def test_draw_explosion_rings(screen: pygame.Surface, elapsed: float) -> None:
    """draw_explosion_rings() handles every elapsed-time branch without raising."""
    draw_explosion_rings(screen, pygame.Vector2(100, 100), elapsed)


# ---------------------------------------------------------------------------
# game_over_screen
# ---------------------------------------------------------------------------


class _ImmediateClock:
    def tick(self, _fps: int) -> int:
        """Return a small fixed delta so elapsed stays near zero."""
        return 16


class _FastClock:
    def tick(self, _fps: int) -> int:
        """Return 2 s per frame so elapsed > 1.0 on the first tick."""
        return 2000


class _TwoFrameClock:
    def __init__(self) -> None:
        self._calls = 0

    def tick(self, _fps: int) -> int:
        """Return 2 s on the first call (hint renders); post QUIT on the second."""
        self._calls += 1
        if self._calls == 1:
            return 2000
        pygame.event.post(pygame.event.Event(pygame.QUIT))
        return 16


def test_game_over_screen_exits_on_quit() -> None:
    """game_over_screen() returns immediately when a QUIT event is received."""
    go_screen = pygame.display.set_mode((200, 200))
    pygame.event.post(pygame.event.Event(pygame.QUIT))
    game_over_screen(
        go_screen,
        _ImmediateClock(),  # type: ignore[arg-type]
        stars=[],
        pos=pygame.Vector2(100, 100),
        survival_time=0.0,
        destroyed=0,
    )


def test_game_over_screen_exits_on_keydown_after_delay() -> None:
    """game_over_screen() returns on KEYDOWN once elapsed exceeds 1.0 s."""
    go_screen = pygame.display.set_mode((200, 200))
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE, mod=0))
    game_over_screen(
        go_screen,
        _FastClock(),  # type: ignore[arg-type]
        stars=[],
        pos=pygame.Vector2(100, 100),
        survival_time=90.0,
        destroyed=5,
    )


def test_game_over_screen_renders_hint_text() -> None:
    """game_over_screen() renders the 'Press any key' hint once elapsed > 1.0."""
    go_screen = pygame.display.set_mode((200, 200))
    game_over_screen(
        go_screen,
        _TwoFrameClock(),  # type: ignore[arg-type]
        stars=[(10, 10, 1)],
        pos=pygame.Vector2(100, 100),
        survival_time=0.0,
        destroyed=0,
    )


# ---------------------------------------------------------------------------
# check_collisions
# ---------------------------------------------------------------------------


@pytest.fixture()
def player() -> Player:
    """Player at (100, 100) with full HP and no containers set."""
    return Player(100.0, 100.0)


def test_check_collisions_empty_groups(player: Player) -> None:
    """check_collisions() returns (False, 0) when there are no asteroids."""
    dead, destroyed = check_collisions(
        pygame.sprite.Group(), pygame.sprite.Group(), player
    )
    assert dead is False
    assert destroyed == 0


def test_check_collisions_no_overlap(player: Player) -> None:
    """check_collisions() returns (False, 0) when the asteroid is far from the player."""
    asteroids: pygame.sprite.Group = pygame.sprite.Group()
    Asteroid.containers = (asteroids,)  # type: ignore[attr-defined]
    Asteroid(800, 600, ASTEROID_MIN_RADIUS)
    del Asteroid.containers  # type: ignore[attr-defined]

    dead, destroyed = check_collisions(asteroids, pygame.sprite.Group(), player)
    assert dead is False
    assert destroyed == 0


@pytest.mark.parametrize(
    "radius,expected_damage",
    [
        (ASTEROID_MIN_RADIUS, PLAYER_HP_DAMAGE_SMALL),
        (ASTEROID_MIN_RADIUS + 1, PLAYER_HP_DAMAGE_LARGE),
    ],
)
def test_check_collisions_asteroid_damage(
    player: Player, radius: int, expected_damage: int
) -> None:
    """check_collisions() applies the correct damage based on asteroid radius."""
    asteroids: pygame.sprite.Group = pygame.sprite.Group()
    Asteroid.containers = (asteroids,)  # type: ignore[attr-defined]
    Asteroid(100, 100, radius)
    del Asteroid.containers  # type: ignore[attr-defined]

    check_collisions(asteroids, pygame.sprite.Group(), player)
    assert player.hp == PLAYER_MAX_HP - expected_damage


def test_check_collisions_player_death(player: Player) -> None:
    """check_collisions() returns (True, 0) when damage reduces player HP to zero."""
    player.hp = PLAYER_HP_DAMAGE_SMALL
    asteroids: pygame.sprite.Group = pygame.sprite.Group()
    Asteroid.containers = (asteroids,)  # type: ignore[attr-defined]
    Asteroid(100, 100, ASTEROID_MIN_RADIUS)
    del Asteroid.containers  # type: ignore[attr-defined]

    dead, destroyed = check_collisions(asteroids, pygame.sprite.Group(), player)
    assert dead is True
    assert destroyed == 0


def test_check_collisions_shot_destroys_asteroid(player: Player) -> None:
    """check_collisions() increments destroyed and kills the shot on asteroid hit."""
    asteroids: pygame.sprite.Group = pygame.sprite.Group()
    Asteroid.containers = (asteroids,)  # type: ignore[attr-defined]
    Asteroid(600, 400, ASTEROID_MIN_RADIUS)
    del Asteroid.containers  # type: ignore[attr-defined]

    shots: pygame.sprite.Group = pygame.sprite.Group()
    shot = Shot(600.0, 400.0)
    shots.add(shot)

    dead, destroyed = check_collisions(asteroids, shots, player)
    assert dead is False
    assert destroyed == 1
    assert not shot.alive()
