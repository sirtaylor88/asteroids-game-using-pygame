"""Main program"""

import pygame

from constants import SCREEN_HEIGHT, SCREEN_WIDTH
from player import Player


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
    clock = pygame.time.Clock()
    dt = 0

    while True:
        dt = clock.tick(60) / 1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

        # Draw objects
        screen.fill(pygame.Color(0, 0, 0))  # black
        player.draw(screen)

        # Update object positions
        player.update(dt)

        # Rendering
        pygame.display.flip()


if __name__ == "__main__":
    main()
