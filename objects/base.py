"""Abstract base for all scene objects."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from renderers.base import BaseRenderer


@dataclass
class Transform:
    """Spatial transform for a scene object."""

    x: float = 0.0
    y: float = 0.0
    scale: float = 1.0
    rotation: float = 0.0  # degrees


class SceneObject(ABC):
    """
    Abstract base for every drawable entity in a scene.

    Subclasses implement render() to call appropriate renderer primitives.
    """

    def __init__(
        self,
        id: str,
        x: float = 0.0,
        y: float = 0.0,
        color: tuple = (255, 255, 255),
        alpha: float = 1.0,
        visible: bool = True,
        z_order: int = 0,
    ) -> None:
        """Initialize common scene object attributes."""
        self.id: str = id
        self.transform: Transform = Transform(x=x, y=y)
        self.color: tuple = color
        self.alpha: float = alpha
        self.visible: bool = visible
        self.z_order: int = z_order

    def update(self, dt: float) -> None:
        """Called once per frame; override for per-frame logic."""
        pass

    @abstractmethod
    def render(self, renderer: "BaseRenderer") -> None:
        """Draw this object using the given renderer."""
        ...
