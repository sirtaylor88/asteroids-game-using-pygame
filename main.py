"""Main program"""

import pygame

from constants import SCREEN_HEIGHT, SCREEN_WIDTH
from player import Player


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    # Define groups
    updatable = pygame.sprite.Group()
    drawable = pygame.sprite.Group()

    # Link objects to groups
    Player.containers = (updatable, drawable)

    #  Create objects
    Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)

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
        for item in drawable:
            item.update(dt)

        # Rendering
        pygame.display.flip()


if __name__ == "__main__":
    main()
