"""Main program."""

import pygame

from asteroid import Asteroid
from asteroidfield import AsteroidField
from constants import SCREEN_HEIGHT, SCREEN_WIDTH
from player import Player, Shot


def main():
    """Main method."""
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    # Define groups
    updatable = pygame.sprite.Group()
    drawable = pygame.sprite.Group()
    asteroids = pygame.sprite.Group()
    shots = pygame.sprite.Group()

    # Link objects to groups
    Player.containers = (updatable, drawable)
    Asteroid.containers = (updatable, drawable, asteroids)
    AsteroidField.containers = (updatable,)
    Shot.containers = (updatable, drawable, shots)

    #  Create objects
    player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
    AsteroidField()

    clock = pygame.time.Clock()
    dt = 0

    while True:
        dt = clock.tick(60) / 1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

        screen.fill(pygame.Color(0, 0, 0))  # black

        # Draw objects
        for item in drawable:
            item.draw(screen)

        # Update objects
        for item in updatable:
            item.update(dt)

        # Check collision
        for asteroid in asteroids:
            if asteroid.check_collision(player):
                print("Game over!")
                return
            for shot in shots:
                if asteroid.check_collision(shot):
                    shot.kill()
                    asteroid.split()
                    break

        # Rendering
        pygame.display.flip()


if __name__ == "__main__":
    main()
