"""Frame clock — manages dt, frame index, and elapsed time."""


class FrameClock:
    """Tracks frame progression for both real-time and offline rendering."""

    def __init__(self, fps: int, offline: bool = False) -> None:
        """
        Initialize clock.

        Args:
            fps: Target frames per second.
            offline: If True, use fixed dt = 1/fps (SVG mode).
        """
        self.fps: int = fps
        self.offline: bool = offline
        self.frame_index: int = 0
        self.elapsed_time: float = 0.0
        self.dt: float = 1.0 / fps

        self._pygame_clock = None
        if not offline:
            try:
                import pygame
                self._pygame_clock = pygame.time.Clock()
            except ImportError:
                self.offline = True

    def tick(self) -> None:
        """Advance the clock by one frame."""
        if self.offline or self._pygame_clock is None:
            self.dt = 1.0 / self.fps
        else:
            self.dt = self._pygame_clock.tick(self.fps) / 1000.0

        self.elapsed_time += self.dt
        self.frame_index += 1
