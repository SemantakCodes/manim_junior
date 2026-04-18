"""Fade animations: FadeIn and FadeOut."""

from typing import Callable, TYPE_CHECKING

from animations.base import Animation
from animations.easing import linear

if TYPE_CHECKING:
    from objects.base import SceneObject


class FadeIn(Animation):
    """Animate target.alpha from 0.0 to 1.0."""

    def __init__(
        self,
        target: "SceneObject",
        duration: float = 1.0,
        delay: float = 0.0,
        easing: Callable[[float], float] = linear,
        debug: bool = False,
    ) -> None:
        """Initialize FadeIn; sets target alpha to 0 immediately."""
        super().__init__(target, duration, delay, easing, debug)
        target.alpha = 0.0

    def apply(self, t: float) -> None:
        """Set alpha proportional to t."""
        self.target.alpha = t


class FadeOut(Animation):
    """Animate target.alpha from 1.0 to 0.0."""

    def __init__(
        self,
        target: "SceneObject",
        duration: float = 1.0,
        delay: float = 0.0,
        easing: Callable[[float], float] = linear,
        debug: bool = False,
    ) -> None:
        """Initialize FadeOut; target alpha is unchanged until animation starts."""
        super().__init__(target, duration, delay, easing, debug)

    def apply(self, t: float) -> None:
        """Set alpha inversely proportional to t."""
        self.target.alpha = 1.0 - t
