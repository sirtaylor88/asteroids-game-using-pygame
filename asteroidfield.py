"""Asteroid Field objects."""

import random
from typing import Any

import pygame

from asteroid import Asteroid
from constants import (
    ASTEROID_KINDS,
    ASTEROID_MAX_RADIUS,
    ASTEROID_MIN_RADIUS,
    ASTEROID_SPAWN_RATE,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
)


class AsteroidField(pygame.sprite.Sprite):
    """Define Asteroid Field."""

    edges: list[list[Any]] = [
        [
            pygame.Vector2(1, 0),
            lambda y: pygame.Vector2(-ASTEROID_MAX_RADIUS, y * SCREEN_HEIGHT),
        ],
        [
            pygame.Vector2(-1, 0),
            lambda y: pygame.Vector2(
                SCREEN_WIDTH + ASTEROID_MAX_RADIUS, y * SCREEN_HEIGHT
            ),
        ],
        [
            pygame.Vector2(0, 1),
            lambda x: pygame.Vector2(x * SCREEN_WIDTH, -ASTEROID_MAX_RADIUS),
        ],
        [
            pygame.Vector2(0, -1),
            lambda x: pygame.Vector2(
                x * SCREEN_WIDTH, SCREEN_HEIGHT + ASTEROID_MAX_RADIUS
            ),
        ],
    ]

    def __init__(self) -> None:
        """Inits AsteroidField."""
        pygame.sprite.Sprite.__init__(self, self.containers)  # type: ignore[attr-defined]
        self.spawn_timer: float = 0.0

    def spawn(
        self,
        radius: float,
        position: pygame.Vector2,
        velocity: pygame.Vector2,
    ) -> None:
        """Spawn a single asteroid at the given position.

        Args:
            radius: Radius of the new asteroid in pixels.
            position: Spawn position as a 2-D vector.
            velocity: Initial velocity as a 2-D vector.
        """
        asteroid = Asteroid(position.x, position.y, radius)
        asteroid.velocity = velocity

    def update(self, dt: float) -> None:
        """Tick the spawn timer and emit a new asteroid when it fires.

        Args:
            dt: Duration in seconds since last frame.
        """
        self.spawn_timer += dt
        if self.spawn_timer > ASTEROID_SPAWN_RATE:
            self.spawn_timer = 0.0

            # spawn a new asteroid at a random edge
            edge = random.choice(self.edges)
            direction: pygame.Vector2 = edge[0]
            speed = random.randint(40, 100)
            velocity: pygame.Vector2 = direction * speed
            velocity = velocity.rotate(random.randint(-30, 30))
            position: pygame.Vector2 = edge[1](random.uniform(0, 1))
            kind = random.randint(1, ASTEROID_KINDS)
            self.spawn(ASTEROID_MIN_RADIUS * kind, position, velocity)
