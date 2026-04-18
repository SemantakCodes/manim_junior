"""Camera with pan/zoom and world-to-screen transform."""

from dataclasses import dataclass
from typing import Callable

from animations.easing import linear


@dataclass
class _CameraPanAnim:
    """Internal lightweight camera pan animation."""

    start_x: float
    start_y: float
    end_x: float
    end_y: float
    duration: float
    easing: Callable[[float], float]
    elapsed: float = 0.0
    done: bool = False


@dataclass
class _CameraZoomAnim:
    """Internal lightweight camera zoom animation."""

    start_zoom: float
    end_zoom: float
    duration: float
    easing: Callable[[float], float]
    elapsed: float = 0.0
    done: bool = False


class Camera:
    """
    2D camera with position and zoom.

    World coordinates are converted to screen pixels via world_to_screen().
    """

    def __init__(self, x: float = 0.0, y: float = 0.0, zoom: float = 1.0) -> None:
        """Initialize camera centered at (x, y) with given zoom."""
        self.x: float = x
        self.y: float = y
        self.zoom: float = zoom
        self._pan_anim: _CameraPanAnim | None = None
        self._zoom_anim: _CameraZoomAnim | None = None

    def pan_to(
        self,
        x: float,
        y: float,
        duration: float = 1.0,
        easing: Callable[[float], float] = linear,
    ) -> None:
        """Schedule a smooth pan to world position (x, y)."""
        self._pan_anim = _CameraPanAnim(
            start_x=self.x,
            start_y=self.y,
            end_x=x,
            end_y=y,
            duration=duration,
            easing=easing,
        )

    def zoom_to(
        self,
        level: float,
        duration: float = 1.0,
        easing: Callable[[float], float] = linear,
    ) -> None:
        """Schedule a smooth zoom to the given level."""
        self._zoom_anim = _CameraZoomAnim(
            start_zoom=self.zoom,
            end_zoom=level,
            duration=duration,
            easing=easing,
        )

    def update(self, dt: float) -> None:
        """Advance camera animations by dt seconds."""
        if self._pan_anim and not self._pan_anim.done:
            anim = self._pan_anim
            anim.elapsed += dt
            t = min(anim.elapsed / anim.duration, 1.0) if anim.duration > 0 else 1.0
            te = anim.easing(t)
            self.x = anim.start_x + (anim.end_x - anim.start_x) * te
            self.y = anim.start_y + (anim.end_y - anim.start_y) * te
            if t >= 1.0:
                anim.done = True

        if self._zoom_anim and not self._zoom_anim.done:
            anim = self._zoom_anim
            anim.elapsed += dt
            t = min(anim.elapsed / anim.duration, 1.0) if anim.duration > 0 else 1.0
            te = anim.easing(t)
            self.zoom = anim.start_zoom + (anim.end_zoom - anim.start_zoom) * te
            if t >= 1.0:
                anim.done = True

    def world_to_screen(
        self, wx: float, wy: float, screen_w: float, screen_h: float
    ) -> tuple[float, float]:
        """Convert world coordinates to screen-space pixels."""
        sx = (wx - self.x) * self.zoom + screen_w / 2
        sy = (wy - self.y) * self.zoom + screen_h / 2
        return sx, sy

    def scale_value(self, world_val: float) -> float:
        """Scale a world-space scalar (e.g. radius) to screen space."""
        return world_val * self.zoom
