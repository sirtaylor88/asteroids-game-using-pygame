"""Player objects."""

import pygame

from circleshape import CircleShape
from constants import PLAYER_RADIUS, PLAYER_SPEED, PLAYER_TURN_SPEED


class Player(CircleShape):
    """Define Player."""

    def __init__(self, x, y) -> None:
        """Inits Player instance."""
        super().__init__(x, y, PLAYER_RADIUS)
        self.position = pygame.Vector2(x, y)
        self.rotation = 0

    def triangle(self) -> list[pygame.Vector2]:
        """Draws a triangle.

        Returns a list of 3 points of the triangle.
        """
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        right = pygame.Vector2(0, 1).rotate(self.rotation + 90) * self.radius / 1.5
        a = self.position + forward * self.radius
        b = self.position - forward * self.radius - right
        c = self.position - forward * self.radius + right
        return [a, b, c]

    def draw(self, screen: pygame.Surface) -> None:
        """Draws the player starship hitbox.

        Args:
            screen: A pygame.Surface instance.
        """
        pygame.draw.polygon(
            screen,
            pygame.Color(255, 255, 255),  # white
            self.triangle(),
            2,
        )

    def rotate(self, dt: float) -> None:
        """Rotates the player starship.

        Args:
            dt: Duration in seconds.
        """
        self.rotation += dt * PLAYER_TURN_SPEED

    def update(self, dt: float) -> None:
        """Update the rotation of player starship.

        Args:
            dt: Duration in seconds.
        """
        keys = pygame.key.get_pressed()

        if keys[pygame.K_w]:
            self.move(dt)
        if keys[pygame.K_s]:
            self.move(-1 * dt)
        if keys[pygame.K_a]:
            self.rotate(dt)
        if keys[pygame.K_d]:
            self.rotate(-1 * dt)

    def move(self, dt: float) -> None:
        """Moves the player starship.

        Args:
            dt: Duration in seconds.
        """
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        self.position += forward * PLAYER_SPEED * dt
