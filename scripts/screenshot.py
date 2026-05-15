"""Render a fixed number of frames and save a screenshot.

Usage:
    uv run scripts/screenshot.py [output_path]

Output defaults to docs/source/_static/screenshot.png.
"""

# pylint: disable=wrong-import-position,too-many-locals,too-many-statements

import os
import random
import sys

# Ensure repo root is on the path when run as a script from any directory.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame  # noqa: E402

from core.asteroid import Asteroid
from core.asteroid_field import AsteroidField
from core.constants import (
    HUD_FONT_SIZE,
    PLAYER_MAX_HP,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
)
from core.player import Player, Shot

OUTPUT = sys.argv[1] if len(sys.argv) > 1 else "docs/source/_static/screenshot.png"
FRAMES = 360  # ~6 seconds at 60 FPS — enough for asteroids to fill the screen


def main() -> None:
    """Render FRAMES frames of gameplay and save to OUTPUT."""
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    updatable: pygame.sprite.Group = pygame.sprite.Group()
    drawable: pygame.sprite.Group = pygame.sprite.Group()
    asteroids: pygame.sprite.Group = pygame.sprite.Group()
    shots: pygame.sprite.Group = pygame.sprite.Group()

    Player.containers = (updatable, drawable)  # type: ignore[attr-defined]
    Asteroid.containers = (updatable, drawable, asteroids)  # type: ignore[attr-defined]
    AsteroidField.containers = (updatable,)  # type: ignore[attr-defined]
    Shot.containers = (updatable, drawable, shots)  # type: ignore[attr-defined]

    player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
    player.rotation = -30.0
    player.hp = 4  # show yellow HP bar (damaged state)
    AsteroidField()

    rng = random.Random(0)
    stars = [
        (rng.randint(0, SCREEN_WIDTH), rng.randint(0, SCREEN_HEIGHT), rng.randint(1, 3))
        for _ in range(180)
    ]

    font = pygame.font.Font(None, HUD_FONT_SIZE)
    clock = pygame.time.Clock()
    survival_time = 0.0
    destroyed = 3

    for frame in range(FRAMES):
        dt = clock.tick(60) / 1000
        survival_time += dt
        if frame % 20 == 0:
            player.shoot()

        # Update before draw so we can override thrusting for the flame
        for item in updatable:
            item.update(dt)
        player.thrusting = True  # force flame visible in draw

        screen.fill((0, 0, 0))

        for sx, sy, sz in stars:
            brightness = 100 + sz * 45
            if sz == 1:
                screen.set_at((sx, sy), (brightness, brightness, brightness))
            else:
                pygame.draw.circle(
                    screen, (brightness, brightness, brightness), (sx, sy), 1
                )

        for item in drawable:
            item.draw(screen)

        # HUD
        hp = player.hp
        minutes, seconds = divmod(int(survival_time), 60)
        time_surf = font.render(
            f"Time  {minutes:02d}:{seconds:02d}", True, (255, 255, 255)
        )
        dest_surf = font.render(f"Destroyed  {destroyed}", True, (255, 255, 255))
        screen.blit(time_surf, (10, 10))
        screen.blit(dest_surf, (SCREEN_WIDTH - dest_surf.get_width() - 10, 10))
        bar_w, bar_h = 120, 12
        bar_x = (SCREEN_WIDTH - bar_w) // 2
        bar_y = 12
        fill = int(bar_w * hp / PLAYER_MAX_HP)
        bar_color = (255, 200, 0) if hp * 10 <= PLAYER_MAX_HP * 6 else (0, 210, 80)
        pygame.draw.rect(screen, (45, 45, 45), (bar_x, bar_y, bar_w, bar_h))
        pygame.draw.rect(screen, bar_color, (bar_x, bar_y, fill, bar_h))
        pygame.draw.rect(screen, (160, 160, 160), (bar_x, bar_y, bar_w, bar_h), 1)
        hp_label = font.render(f"HP  {hp}/{PLAYER_MAX_HP}", True, bar_color)
        screen.blit(
            hp_label,
            hp_label.get_rect(centerx=SCREEN_WIDTH // 2, top=bar_y + bar_h + 3),
        )

        pygame.display.flip()

    pygame.image.save(screen, OUTPUT)
    print(f"Screenshot saved to {OUTPUT}")
    pygame.quit()


if __name__ == "__main__":
    main()
