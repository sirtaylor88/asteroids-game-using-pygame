"""Asteroid objects."""

import random

import pygame

from circleshape import CircleShape
from constants import ASTEROID_MIN_RADIUS


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

    def split(self) -> None:
        """Split an asteroid to smaller ones.

        If it is small enough, it will be destroyed instead.
        """
        self.kill()
        if self.radius <= ASTEROID_MIN_RADIUS:
            return

        random_angle = random.uniform(20, 50)
        v1 = self.velocity.rotate(random_angle)
        v2 = self.velocity.rotate(-1 * random_angle)
        new_radius = self.radius - ASTEROID_MIN_RADIUS
        a1 = Asteroid(self.position.x, self.position.y, new_radius)
        a1.velocity = v1 * 1.2
        a2 = Asteroid(self.position.x, self.position.y, new_radius)
        a2.velocity = v2 * 1.2
