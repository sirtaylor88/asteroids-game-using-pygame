"""Player objects."""

import random

import pygame

from core.circle_shape import CircleShape
from core.constants import (
    PLAYER_INVINCIBILITY_DURATION,
    PLAYER_MAX_HP,
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
        self.thrusting: bool = False
        self.hp: int = PLAYER_MAX_HP
        self.invincible_timer: float = 0.0

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

    def _ship_points(self) -> list[pygame.Vector2]:
        """Return the five vertices of the ship hull in world space.

        Returns:
            list[pygame.Vector2]: Hull vertices — nose, right wing, right rear,
            left rear, left wing.
        """
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        right = pygame.Vector2(0, 1).rotate(self.rotation + 90)
        r = self.radius
        return [
            self.position + forward * r,
            self.position + right * r * 0.9 - forward * r * 0.1,
            self.position + right * r * 0.35 - forward * r * 0.9,
            self.position - right * r * 0.35 - forward * r * 0.9,
            self.position - right * r * 0.9 - forward * r * 0.1,
        ]

    def draw(self, screen: pygame.Surface) -> None:
        """Draw the player ship with hull, cockpit, engine glow, and thrust flame.

        Args:
            screen (pygame.Surface): The surface to draw on.
        """
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        right = pygame.Vector2(0, 1).rotate(self.rotation + 90)
        r = self.radius

        if self.invincible_timer > 0 and int(self.invincible_timer * 8) % 2 == 0:
            return

        if self.thrusting:
            flame_tip = self.position - forward * r * 1.7
            fl = self.position - forward * r * 0.85 - right * r * 0.28
            fr = self.position - forward * r * 0.85 + right * r * 0.28
            flame_color = (255, random.randint(80, 180), 0)
            pygame.draw.polygon(screen, flame_color, [fl, fr, flame_tip])

        hull = self._ship_points()
        pygame.draw.polygon(screen, (15, 25, 45), hull)
        pygame.draw.polygon(screen, (0, 210, 255), hull, 2)

        cockpit = self.position + forward * r * 0.3
        pygame.draw.circle(screen, (150, 220, 255), (int(cockpit.x), int(cockpit.y)), 4)

        engine = self.position - forward * r * 0.75
        pygame.draw.circle(screen, (255, 130, 0), (int(engine.x), int(engine.y)), 4)

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
        self.invincible_timer = max(0.0, self.invincible_timer - dt)
        keys = pygame.key.get_pressed()
        self.thrusting = bool(keys[pygame.K_w] or keys[pygame.K_UP])

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

    def take_damage(self, amount: int) -> None:
        """Reduce HP by *amount* and start the invincibility window.

        Does nothing while the invincibility timer is active, so a single
        collision event cannot drain more than one hit's worth of HP.

        Args:
            amount (int): HP to subtract (clamped so HP never goes below 0).
        """
        if self.invincible_timer > 0:
            return
        self.hp = max(0, self.hp - amount)
        self.invincible_timer = PLAYER_INVINCIBILITY_DURATION


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
        """Draw the shot as a yellow laser bolt with a short tail.

        Args:
            screen (pygame.Surface): The surface to draw on.
        """
        if self.velocity.length() > 0:
            tail = self.position - self.velocity.normalize() * self.radius * 3
            pygame.draw.line(screen, (255, 200, 50), tail, self.position, 2)
        pygame.draw.circle(
            screen,
            (255, 255, 130),
            (int(self.position.x), int(self.position.y)),
            self.radius,
        )

    def update(self, dt: float) -> None:
        """Update the position of the shot by applying its velocity.

        Args:
            dt (float): Duration in seconds since last frame.
        """
        self.position += self.velocity * dt
