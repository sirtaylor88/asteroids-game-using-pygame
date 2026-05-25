"""Main program."""

import random

import pygame

from core.asteroid import Asteroid
from core.asteroid_field import AsteroidField
from core.constants import HUD_FONT_SIZE, SCREEN_HEIGHT, SCREEN_WIDTH
from core.player import Player, Shot
from core.utils import check_collisions, draw_stars, game_over_screen, render_hud


def main() -> None:
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
        draw_stars(screen, stars)

        # Draw objects
        for item in drawable:
            item.draw(screen)

        # Update objects
        for item in updatable:
            item.update(dt)

        dead, n_destroyed = check_collisions(asteroids, shots, player)
        destroyed += n_destroyed
        if dead:
            game_over_screen(
                screen,
                clock,
                stars=stars,
                pos=player.position,
                survival_time=survival_time,
                destroyed=destroyed,
            )
            return

        render_hud(screen, font, survival_time, destroyed, hp=player.hp)
        pygame.display.flip()


if __name__ == "__main__":
    main()
