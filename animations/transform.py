"""Transform animations: MoveTo, ScaleTo, RotateTo."""

from typing import Callable, TYPE_CHECKING

from animations.base import Animation
from animations.easing import linear

if TYPE_CHECKING:
    from objects.base import SceneObject


def _lerp(a: float, b: float, t: float) -> float:
    """Linear interpolate between a and b at position t."""
    return a + (b - a) * t


class MoveTo(Animation):
    """Translate a scene object to a target position."""

    def __init__(
        self,
        target: "SceneObject",
        end_x: float,
        end_y: float,
        duration: float = 1.0,
        delay: float = 0.0,
        easing: Callable[[float], float] = linear,
        debug: bool = False,
    ) -> None:
        """Initialize with start position captured at construction time."""
        super().__init__(target, duration, delay, easing, debug)
        self._start_x: float = target.transform.x
        self._start_y: float = target.transform.y
        self._end_x: float = end_x
        self._end_y: float = end_y

    def apply(self, t: float) -> None:
        """Interpolate x and y positions."""
        self.target.transform.x = _lerp(self._start_x, self._end_x, t)
        self.target.transform.y = _lerp(self._start_y, self._end_y, t)


class ScaleTo(Animation):
    """Scale a scene object to a target scale value."""

    def __init__(
        self,
        target: "SceneObject",
        end_scale: float,
        duration: float = 1.0,
        delay: float = 0.0,
        easing: Callable[[float], float] = linear,
        debug: bool = False,
    ) -> None:
        """Initialize with start scale captured at construction time."""
        super().__init__(target, duration, delay, easing, debug)
        self._start_scale: float = target.transform.scale
        self._end_scale: float = end_scale

    def apply(self, t: float) -> None:
        """Interpolate scale."""
        self.target.transform.scale = _lerp(self._start_scale, self._end_scale, t)


class RotateTo(Animation):
    """Rotate a scene object to a target angle in degrees."""

    def __init__(
        self,
        target: "SceneObject",
        end_rotation: float,
        duration: float = 1.0,
        delay: float = 0.0,
        easing: Callable[[float], float] = linear,
        debug: bool = False,
    ) -> None:
        """Initialize with start rotation captured at construction time."""
        super().__init__(target, duration, delay, easing, debug)
        self._start_rotation: float = target.transform.rotation
        self._end_rotation: float = end_rotation

    def apply(self, t: float) -> None:
        """Interpolate rotation with shortest-path wraparound."""
        start = self._start_rotation
        end = self._end_rotation
        # Normalize delta to [-180, 180] for shortest path
        delta = (end - start + 180.0) % 360.0 - 180.0
        self.target.transform.rotation = start + delta * t
