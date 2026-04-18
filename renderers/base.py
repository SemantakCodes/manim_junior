"""Abstract renderer interface — all backends must implement this."""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.config import EngineConfig


class BaseRenderer(ABC):
    """Dumb drawing backend"""

    @abstractmethod
    def initialize(self, config: "EngineConfig") -> None:
        """Set up the renderer (create window, init context, etc.)."""
        ...

    @abstractmethod
    def begin_frame(self, background_color: tuple) -> None:
        """Clear the canvas and prepare for a new frame."""
        ...

    @abstractmethod
    def draw_circle(
        self,
        x: float,
        y: float,
        radius: float,
        color: tuple,
        alpha: float,
        fill: bool = True,
        stroke_width: float = 2,
    ) -> None:
        """Draw a circle at (x, y) with given radius."""
        ...

    @abstractmethod
    def draw_rect(
        self,
        x: float,
        y: float,
        w: float,
        h: float,
        color: tuple,
        alpha: float,
        fill: bool = True,
        stroke_width: float = 2,
    ) -> None:
        """Draw a rectangle with top-left corner at (x, y)."""
        ...

    @abstractmethod
    def draw_line(
        self,
        x1: float,
        y1: float,
        x2: float,
        y2: float,
        color: tuple,
        alpha: float,
        stroke_width: float = 2,
    ) -> None:
        """Draw a line from (x1, y1) to (x2, y2)."""
        ...

    @abstractmethod
    def draw_polygon(
        self,
        points: list[tuple],
        color: tuple,
        alpha: float,
        fill: bool = True,
        stroke_width: float = 2,
    ) -> None:
        """Draw a closed polygon from a list of (x, y) points."""
        ...

    @abstractmethod
    def draw_text(
        self,
        x: float,
        y: float,
        text: str,
        font_size: int,
        color: tuple,
        alpha: float,
    ) -> None:
        """Render a text string at (x, y)."""
        ...

    @abstractmethod
    def end_frame(self) -> None:
        """Finalize and display/store the current frame."""
        ...

    @abstractmethod
    def finalize(self) -> None:
        """Tear down the renderer and flush all output."""
        ...
