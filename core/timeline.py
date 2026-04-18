

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from animations.base import Animation


class AnimationTrack:

    def __init__(self, start_time: float, animation: "Animation") -> None:
        self.start_time: float = start_time
        self.animation: "Animation" = animation
        self._activated: bool = False


class Timeline:

    def __init__(self, debug: bool = False) -> None:
        self._tracks: list[AnimationTrack] = []
        self.debug: bool = debug

    def add(self, animation: "Animation", start_time: float) -> None:
        self._tracks.append(AnimationTrack(start_time, animation))

    def update(self, elapsed_time: float, dt: float) -> None:
        active: list[AnimationTrack] = []
        for track in self._tracks:
            if elapsed_time >= track.start_time:
                track.animation.update(dt)
                if not track.animation.is_complete:
                    active.append(track)
            else:
                active.append(track)
        self._tracks = active

    def is_complete(self) -> bool:
        return len(self._tracks) == 0

    def total_duration(self) -> float:
        if not self._tracks:
            return 0.0
        return max(
            t.start_time + t.animation.delay + t.animation.duration
            for t in self._tracks
        )

    def next_end_time(self) -> float:
        if not self._tracks:
            return 0.0
        return max(
            t.start_time + t.animation.delay + t.animation.duration
            for t in self._tracks
        )
