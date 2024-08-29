"""Base class for game objects."""

from abc import abstractmethod

import pygame


class CircleShape(pygame.sprite.Sprite):
    """Base class for game objects."""

    def __init__(self, x: float, y: float, radius: float) -> None:
        """Inits CircleShape instance."""
        if hasattr(self, "containers"):
            super().__init__(self.containers)
        else:
            super().__init__()

        self.position = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(0, 0)
        self.radius = radius

    def check_collision(self, other: "CircleShape") -> bool:
        """Check if this hitbox will collide with other one."""
        return self.position.distance_to(other.position) < self.radius + other.radius

    @abstractmethod
    def draw(self, screen: pygame.Surface):
        """Sub-classes must override."""

    @abstractmethod
    def update(self, dt: float):
        """Sub-classes must override."""
