#Fade animations: FadeIn and FadeOut.

from typing import Callable, TYPE_CHECKING

from animations.base import Animation
from animations.easing import linear

if TYPE_CHECKING:
    from objects.base import SceneObject


class FadeIn(Animation):

    def __init__(
        self,
        target: "SceneObject",
        duration: float = 1.0,
        delay: float = 0.0,
        easing: Callable[[float], float] = linear,
        debug: bool = False,
    ) -> None:
        super().__init__(target, duration, delay, easing, debug)
        target.alpha = 0.0

    def apply(self, t: float) -> None:
        self.target.alpha = t


class FadeOut(Animation):

    def __init__(
        self,
        target: "SceneObject",
        duration: float = 1.0,
        delay: float = 0.0,
        easing: Callable[[float], float] = linear,
        debug: bool = False,
    ) -> None:
        super().__init__(target, duration, delay, easing, debug)

    def apply(self, t: float) -> None:
        self.target.alpha = 1.0 - t
