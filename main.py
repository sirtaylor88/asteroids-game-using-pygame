"""Main program."""

import random

import pygame

from core.asteroid import Asteroid
from core.asteroid_field import AsteroidField
from core.constants import (
    ASTEROID_MIN_RADIUS,
    HUD_FONT_SIZE,
    HUD_MARGIN,
    PLAYER_HP_DAMAGE_LARGE,
    PLAYER_HP_DAMAGE_SMALL,
    PLAYER_MAX_HP,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
)
from core.player import Player, Shot


def _draw_stars(screen: pygame.Surface, stars: list[tuple[int, int, int]]) -> None:
    """Blit the static starfield onto *screen*.

    Args:
        screen (pygame.Surface): The surface to draw on.
        stars (list[tuple[int, int, int]]): Pre-computed (x, y, size) triples.
    """
    for sx, sy, sz in stars:
        brightness = 100 + sz * 45
        if sz == 1:
            screen.set_at((sx, sy), (brightness, brightness, brightness))
        else:
            pygame.draw.circle(
                screen, (brightness, brightness, brightness), (sx, sy), 1
            )


def _render_hud(  # pylint: disable=too-many-locals
    screen: pygame.Surface,
    font: pygame.font.Font,
    survival_time: float,
    destroyed: int,
    hp: int,
) -> None:
    """Blit the survival timer, destroyed counter, and HP bar onto the screen.

    Args:
        screen (pygame.Surface): The surface to draw on.
        font (pygame.font.Font): Font used to render the text.
        survival_time (float): Elapsed seconds since the game started.
        destroyed (int): Number of asteroids destroyed so far.
        hp (int): Current player hit points.
    """
    minutes, seconds = divmod(int(survival_time), 60)
    time_surf = font.render(f"Time  {minutes:02d}:{seconds:02d}", True, (255, 255, 255))
    dest_surf = font.render(f"Destroyed  {destroyed}", True, (255, 255, 255))
    screen.blit(time_surf, (HUD_MARGIN, HUD_MARGIN))
    screen.blit(
        dest_surf, (SCREEN_WIDTH - dest_surf.get_width() - HUD_MARGIN, HUD_MARGIN)
    )

    # HP bar — top-centre
    bar_w, bar_h = 120, 12
    bar_x = (SCREEN_WIDTH - bar_w) // 2
    bar_y = HUD_MARGIN + 2
    fill = max(0, int(bar_w * hp / PLAYER_MAX_HP))
    if hp * 10 > PLAYER_MAX_HP * 6:
        bar_color: tuple[int, int, int] = (0, 210, 80)
    elif hp * 10 > PLAYER_MAX_HP * 3:
        bar_color = (255, 200, 0)
    else:
        bar_color = (255, 60, 60)
    pygame.draw.rect(screen, (45, 45, 45), (bar_x, bar_y, bar_w, bar_h))
    if fill > 0:
        pygame.draw.rect(screen, bar_color, (bar_x, bar_y, fill, bar_h))
    pygame.draw.rect(screen, (160, 160, 160), (bar_x, bar_y, bar_w, bar_h), 1)
    hp_label = font.render(f"HP  {hp}/{PLAYER_MAX_HP}", True, bar_color)
    screen.blit(
        hp_label, hp_label.get_rect(centerx=SCREEN_WIDTH // 2, top=bar_y + bar_h + 3)
    )


def _game_over_screen(  # pylint: disable=too-many-arguments,too-many-positional-arguments,too-many-locals
    screen: pygame.Surface,
    clock: pygame.time.Clock,
    stars: list[tuple[int, int, int]],
    pos: pygame.Vector2,
    survival_time: float,
    destroyed: int,
) -> None:
    """Run the post-death screen: explosion rings then game-over overlay.

    Args:
        screen (pygame.Surface): The surface to draw on.
        clock (pygame.time.Clock): Game clock (used to tick at 60 FPS).
        stars (list[tuple[int, int, int]]): Static starfield data.
        pos (pygame.Vector2): Position where the explosion originates.
        survival_time (float): Final survival time in seconds.
        destroyed (int): Final destroyed-asteroid count.
    """
    big_font = pygame.font.Font(None, 90)
    sub_font = pygame.font.Font(None, 36)
    elapsed = 0.0

    # Three expanding rings: (start_delay_s, max_radius, RGB, line_width)
    rings = [
        (0.00, 200, (255, 230, 80), 3),
        (0.12, 150, (255, 110, 30), 2),
        (0.28, 100, (200, 40, 0), 2),
    ]

    while True:
        dt = clock.tick(60) / 1000
        elapsed += dt

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN and elapsed > 1.0:
                return

        screen.fill((0, 0, 0))
        _draw_stars(screen, stars)

        # Explosion animation (first 1.5 s)
        if elapsed < 1.5:
            for delay, max_r, color, lw in rings:
                t = (elapsed - delay) / 1.5
                if t <= 0:
                    continue
                radius = int(t * max_r)
                alpha = max(0, int(255 * (1.0 - t)))
                sz = radius * 2 + 6
                surf = pygame.Surface((sz, sz), pygame.SRCALPHA)
                pygame.draw.circle(
                    surf, color + (alpha,), (sz // 2, sz // 2), radius, lw
                )
                screen.blit(surf, (int(pos.x) - sz // 2, int(pos.y) - sz // 2))

        # "GAME OVER" heading
        go_surf = big_font.render("GAME OVER", True, (255, 50, 50))
        screen.blit(
            go_surf,
            go_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 55)),
        )

        # Final stats
        minutes, seconds = divmod(int(survival_time), 60)
        stats_surf = sub_font.render(
            f"Time: {minutes:02d}:{seconds:02d}    Destroyed: {destroyed}",
            True,
            (200, 200, 200),
        )
        screen.blit(
            stats_surf,
            stats_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 15)),
        )

        # "Press any key" hint (appears after 1 s)
        if elapsed > 1.0:
            hint_surf = sub_font.render("Press any key to exit", True, (120, 120, 120))
            screen.blit(
                hint_surf,
                hint_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 65)),
            )

        pygame.display.flip()


def main() -> None:  # pylint: disable=too-many-locals
    """Run the Asteroids game loop until the player quits or is destroyed."""
    print("Starting Asteroids")
    print("Screen width:", SCREEN_WIDTH)
    print("Screen height", SCREEN_HEIGHT)

    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    # Define groups
    updatable: pygame.sprite.Group = pygame.sprite.Group()
    drawable: pygame.sprite.Group = pygame.sprite.Group()
    asteroids: pygame.sprite.Group = pygame.sprite.Group()
    shots: pygame.sprite.Group = pygame.sprite.Group()

    # Link objects to groups
    Player.containers = (updatable, drawable)  # type: ignore[attr-defined]
    Asteroid.containers = (updatable, drawable, asteroids)  # type: ignore[attr-defined]
    AsteroidField.containers = (updatable,)  # type: ignore[attr-defined]
    Shot.containers = (updatable, drawable, shots)  # type: ignore[attr-defined]

    #  Create objects
    player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
    AsteroidField()

    rng = random.Random(0)
    stars = [
        (rng.randint(0, SCREEN_WIDTH), rng.randint(0, SCREEN_HEIGHT), rng.randint(1, 3))
        for _ in range(180)
    ]

    clock = pygame.time.Clock()
    dt: float = 0.0
    survival_time: float = 0.0
    destroyed: int = 0
    font = pygame.font.Font(None, HUD_FONT_SIZE)

    while True:
        dt = clock.tick(60) / 1000
        survival_time += dt
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

        screen.fill(pygame.Color(0, 0, 0))
        _draw_stars(screen, stars)

        # Draw objects
        for item in drawable:
            item.draw(screen)

        # Update objects
        for item in updatable:
            item.update(dt)

        # Check collision
        for asteroid in asteroids:
            if asteroid.check_collision(player):
                damage = (
                    PLAYER_HP_DAMAGE_LARGE
                    if asteroid.radius > ASTEROID_MIN_RADIUS
                    else PLAYER_HP_DAMAGE_SMALL
                )
                player.take_damage(damage)
                if player.hp <= 0:
                    _game_over_screen(
                        screen,
                        clock,
                        stars,
                        player.position,
                        survival_time,
                        destroyed,
                    )
                    return
            for shot in shots:
                if asteroid.check_collision(shot):
                    shot.kill()
                    asteroid.split()
                    destroyed += 1
                    break

        _render_hud(screen, font, survival_time, destroyed, hp=player.hp)

        # Rendering
        pygame.display.flip()


if __name__ == "__main__":
    main()
