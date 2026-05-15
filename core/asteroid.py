"""Asteroid objects."""

import math
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
        self.rotation_speed: float = random.uniform(-50, 50)
        num_points = random.randint(8, 12)
        self._vertices: list[tuple[float, float]] = []
        for i in range(num_points):
            angle = math.radians((360 / num_points) * i + random.uniform(-12, 12))
            r = self.radius * random.uniform(0.65, 1.0)
            self._vertices.append((math.cos(angle) * r, math.sin(angle) * r))

    def _world_points(self) -> list[tuple[float, float]]:
        """Return vertices transformed to world space at the current rotation.

        Returns:
            list[tuple[float, float]]: Absolute screen coordinates for each vertex.
        """
        rad = math.radians(self.rotation)
        cos_r, sin_r = math.cos(rad), math.sin(rad)
        return [
            (
                vx * cos_r - vy * sin_r + self.position.x,
                vx * sin_r + vy * cos_r + self.position.y,
            )
            for vx, vy in self._vertices
        ]

    def draw(self, screen: pygame.Surface) -> None:
        """Draw the asteroid as a jagged rock polygon.

        Args:
            screen (pygame.Surface): The surface to draw on.
        """
        points = self._world_points()
        pygame.draw.polygon(screen, (75, 70, 65), points)
        pygame.draw.polygon(screen, (155, 145, 135), points, 2)

    def update(self, dt: float) -> None:
        """Update the position and rotation of the asteroid.

        Args:
            dt (float): Duration in seconds since last frame.
        """
        self.position += self.velocity * dt
        self.rotation += self.rotation_speed * dt

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
