"""Abstract Animation base class."""

from abc import ABC, abstractmethod
from typing import Callable, TYPE_CHECKING

from animations.easing import linear

if TYPE_CHECKING:
    from objects.base import SceneObject


class Animation(ABC):
    """
    Base for all time-based animations.

    Subclasses implement apply(t) to mutate the target object.
    """

    def __init__(
        self,
        target: "SceneObject",
        duration: float,
        delay: float = 0.0,
        easing: Callable[[float], float] = linear,
        debug: bool = False,
    ) -> None:
        """
        Initialize animation parameters.

        Args:
            target:   The SceneObject this animation mutates.
            duration: Length in seconds.
            delay:    Pre-delay in seconds before animation runs.
            easing:   Easing function (float → float).
            debug:    If True, print progress messages.
        """
        self.target: "SceneObject" = target
        self.duration: float = duration
        self.delay: float = delay
        self.easing: Callable[[float], float] = easing
        self.debug: bool = debug
        self._elapsed: float = 0.0
        self._started: bool = False
        self._completed: bool = False

    def update(self, dt: float) -> None:
        """Advance the animation by dt seconds and apply the interpolated value."""
        if self._completed:
            return

        self._elapsed += dt

        # still in delay window
        effective = self._elapsed - self.delay
        if effective <= 0.0:
            return

        if not self._started:
            self._started = True
            if self.debug:
                print(f"[ANIM] {type(self).__name__} on '{self.target.id}' started")

        if self.duration <= 0.0:
            t = 1.0
        else:
            t = min(effective / self.duration, 1.0)

        t_eased = self.easing(t)
        self.apply(t_eased)

        if self.debug and abs(t - 0.5) < 0.02 and not hasattr(self, "_half_logged"):
            self._half_logged = True  # type: ignore[attr-defined]
            print(f"[ANIM] {type(self).__name__} on '{self.target.id}' 50%")

        if t >= 1.0:
            self._completed = True
            if self.debug:
                print(f"[ANIM] {type(self).__name__} on '{self.target.id}' completed")

    @abstractmethod
    def apply(self, t: float) -> None:
        """Apply the animated value at normalized time t ∈ [0, 1]."""
        ...

    @property
    def is_complete(self) -> bool:
        """True when the animation (including delay) has finished."""
        return self._completed
