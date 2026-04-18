"""Timeline — schedules and drives animations by elapsed time."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from animations.base import Animation


class AnimationTrack:
    """Pair of (start_time, animation) — a single entry in the timeline."""

    def __init__(self, start_time: float, animation: "Animation") -> None:
        """Initialize track with its scheduled start offset."""
        self.start_time: float = start_time
        self.animation: "Animation" = animation
        self._activated: bool = False


class Timeline:
    """Manages ordered animation tracks and drives them by elapsed scene time."""

    def __init__(self, debug: bool = False) -> None:
        """Initialize an empty timeline."""
        self._tracks: list[AnimationTrack] = []
        self.debug: bool = debug

    def add(self, animation: "Animation", start_time: float) -> None:
        """Schedule an animation to begin at start_time seconds."""
        self._tracks.append(AnimationTrack(start_time, animation))

    def update(self, elapsed_time: float, dt: float) -> None:
        """Tick all active animations; prune completed ones."""
        active: list[AnimationTrack] = []
        for track in self._tracks:
            if elapsed_time >= track.start_time:
                track.animation.update(dt)
                if not track.animation.is_complete:
                    active.append(track)
                # completed tracks are dropped
            else:
                # not yet started — keep in list
                active.append(track)
        self._tracks = active

    def is_complete(self) -> bool:
        """True when all animations have finished."""
        return len(self._tracks) == 0

    def total_duration(self) -> float:
        """Return the time at which the last animation finishes."""
        if not self._tracks:
            return 0.0
        return max(
            t.start_time + t.animation.delay + t.animation.duration
            for t in self._tracks
        )

    def next_end_time(self) -> float:
        """Return earliest end time among currently scheduled tracks (for sequential queueing)."""
        if not self._tracks:
            return 0.0
        return max(
            t.start_time + t.animation.delay + t.animation.duration
            for t in self._tracks
        )
