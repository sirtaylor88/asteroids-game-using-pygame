"""Player objects."""

import pygame

from core.circle_shape import CircleShape
from core.constants import (
    PLAYER_RADIUS,
    PLAYER_SHOOT_COOLDOWN,
    PLAYER_SHOOT_SPEED,
    PLAYER_SPEED,
    PLAYER_TURN_SPEED,
    SHOT_RADIUS,
)


class Player(CircleShape):
    """Define Player."""

    def __init__(self, x: float, y: float) -> None:
        """Initialise the player ship at the given position.

        Args:
            x (float): Horizontal centre in pixels.
            y (float): Vertical centre in pixels.
        """
        super().__init__(x, y, PLAYER_RADIUS)
        self.position = pygame.Vector2(x, y)
        self.rotation: float = 0.0
        self.cooldown: float = 0.0

    def triangle(self) -> list[pygame.Vector2]:
        """Compute the three vertices of the player's triangular ship.

        Returns:
            list[pygame.Vector2]: Three points — nose (front) and two rear
            corners.
        """
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        right = pygame.Vector2(0, 1).rotate(self.rotation + 90) * self.radius / 1.5
        a = self.position + forward * self.radius
        b = self.position - forward * self.radius - right
        c = self.position - forward * self.radius + right
        return [a, b, c]

    def draw(self, screen: pygame.Surface) -> None:
        """Draw the player ship as a white triangle outline.

        Args:
            screen (pygame.Surface): The surface to draw on.
        """
        pygame.draw.polygon(
            screen,
            pygame.Color(255, 255, 255),  # white
            self.triangle(),
            2,
        )

    def rotate(self, dt: float) -> None:
        """Rotate the player starship.

        Args:
            dt (float): Duration in seconds.
        """
        self.rotation += dt * PLAYER_TURN_SPEED

    def update(self, dt: float) -> None:
        """Handle keyboard input and update player position, rotation, and cooldown.

        Args:
            dt (float): Duration in seconds since last frame.
        """
        keys = pygame.key.get_pressed()

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.move(dt)
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.move(-1 * dt)
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.rotate(dt)
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.rotate(-1 * dt)
        if keys[pygame.K_SPACE]:
            self.shoot()
        self.cooldown -= dt

    def move(self, dt: float) -> None:
        """Move the player starship forward or backward.

        Args:
            dt (float): Duration in seconds; negative values move backward.
        """
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        self.position += forward * PLAYER_SPEED * dt

    def shoot(self) -> None:
        """Fire a shot from the player's current position in the facing direction.

        Does nothing if the shoot cooldown has not expired yet.
        """
        if self.cooldown > 0:
            return
        shot = Shot(self.position.x, self.position.y)
        shot.velocity = pygame.Vector2(0, 1).rotate(self.rotation) * PLAYER_SHOOT_SPEED
        self.cooldown = PLAYER_SHOOT_COOLDOWN


class Shot(CircleShape):
    """A projectile fired by the player ship."""

    def __init__(self, x: float, y: float) -> None:
        """Initialise a shot at the given position.

        Args:
            x (float): Horizontal centre in pixels.
            y (float): Vertical centre in pixels.
        """
        super().__init__(x, y, SHOT_RADIUS)
        self.position = pygame.Vector2(x, y)
        self.rotation: float = 0.0

    def draw(self, screen: pygame.Surface) -> None:
        """Draw the shot as a white circle outline.

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
        """Update the position of the shot by applying its velocity.

        Args:
            dt (float): Duration in seconds since last frame.
        """
        self.position += self.velocity * dt
