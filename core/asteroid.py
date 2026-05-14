"""Asteroid objects."""

import random

import pygame

from core.circle_shape import CircleShape
from core.constants import ASTEROID_MIN_RADIUS


class Asteroid(CircleShape):
    """Define Asteroid."""

    def __init__(
        self,
        x: float,
        y: float,
        radius: float,
    ) -> None:
        """Initialise an Asteroid at the given position with the given radius.

        Args:
            x (float): Horizontal centre in pixels.
            y (float): Vertical centre in pixels.
            radius (float): Circle radius in pixels.
        """
        super().__init__(x, y, radius)
        self.position = pygame.Vector2(x, y)
        self.rotation: float = 0.0

    def draw(self, screen: pygame.Surface) -> None:
        """Draw the asteroid as a white circle outline.

        Args:
            screen (pygame.Surface): The surface to draw on.
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
            dt (float): Duration in seconds since last frame.
        """
        self.position += self.velocity * dt

    def split(self) -> None:
        """Destroy this asteroid and spawn two smaller ones.

        If the radius is already at or below ``ASTEROID_MIN_RADIUS`` the
        asteroid is simply destroyed with no children spawned.  Otherwise two
        children are created at the same position with velocities rotated
        ±20–50 ° from the parent and scaled up by 1.2×.
        """
        self.kill()
        if self.radius <= ASTEROID_MIN_RADIUS:
            return

        random_angle = random.uniform(20, 50)
        v1 = self.velocity.rotate(random_angle)
        v2 = self.velocity.rotate(-1 * random_angle)
        new_radius = self.radius - ASTEROID_MIN_RADIUS
        a1 = Asteroid(
            self.position.x,
            self.position.y,
            new_radius,
        )
        a1.velocity = v1 * 1.2
        a2 = Asteroid(
            self.position.x,
            self.position.y,
            new_radius,
        )
        a2.velocity = v2 * 1.2
