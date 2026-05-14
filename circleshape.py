"""Base class for game objects."""

from abc import abstractmethod

import pygame


class CircleShape(pygame.sprite.Sprite):
    """Base class for game objects."""

    def __init__(
        self,
        x: float,
        y: float,
        radius: float,
    ) -> None:
        """Initialise position, velocity, and radius; register with any containers.

        Args:
            x: Horizontal centre of the circle in pixels.
            y: Vertical centre of the circle in pixels.
            radius: Radius of the circle in pixels.
        """
        if hasattr(self, "containers"):
            super().__init__(self.containers)
        else:
            super().__init__()

        self.position = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(0, 0)
        self.radius = radius

    def check_collision(self, other: "CircleShape") -> bool:
        """Return True if this circle overlaps *other*.

        Uses distance between centres vs the sum of radii (strict less-than,
        so touching circles are not considered colliding).

        Args:
            other: Another CircleShape to test against.

        Returns:
            True if the circles overlap, False otherwise.
        """
        return self.position.distance_to(other.position) < self.radius + other.radius

    @abstractmethod
    def draw(self, screen: pygame.Surface) -> None:
        """Render this object onto *screen*.

        Args:
            screen: The pygame Surface to draw on.
        """

    @abstractmethod
    def update(self, dt: float) -> None:
        """Advance this object's state by one frame.

        Args:
            dt: Duration in seconds since the last frame.
        """
