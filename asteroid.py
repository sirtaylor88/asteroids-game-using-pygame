"""Asteroid objects."""

import pygame

from circleshape import CircleShape


class Asteroid(CircleShape):
    """Define Asteroid."""

    def __init__(self, x: float, y: float, radius: float) -> None:
        """Inits Asteroid instance."""
        super().__init__(x, y, radius)
        self.position = pygame.Vector2(x, y)
        self.rotation = 0

    def draw(self, screen: pygame.Surface) -> None:
        """Draws the asteroid hitbox.

        Args:
            screen: A pygame.Surface instance.
        """
        pygame.draw.circle(
            screen,
            pygame.Color(255, 255, 255),  # white
            self.position,
            self.radius,
            2,
        )

    def update(self, dt: float) -> None:
        """Update the position of the asteroid.

        Args:
            velocity: Speed.
            dt: Duration in seconds.
        """
        self.position += self.velocity * dt
