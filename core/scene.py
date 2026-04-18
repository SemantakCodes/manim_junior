

import random
from typing import TYPE_CHECKING

from core.config import EngineConfig
from core.clock import FrameClock
from core.timeline import Timeline
from camera.camera import Camera
from objects.base import SceneObject
from animations.base import Animation

if TYPE_CHECKING:
    from renderers.base import BaseRenderer


def _make_renderer(config: EngineConfig) -> "BaseRenderer":
    if config.renderer == "pygame":
        from renderers.pygame_renderer import PygameRenderer
        return PygameRenderer()
    elif config.renderer == "svg":
        from renderers.svg_renderer import SVGRenderer
        return SVGRenderer()
    else:
        raise ValueError(f"Unknown renderer: '{config.renderer}'")


class Scene:
    """
    Owns all scene objects, the timeline, camera, and rendering loop.

    Usage::

        config = EngineConfig(renderer="svg")
        scene = Scene(config)
        circle = Circle(id="c", x=0, y=0, radius=50)
        scene.add(circle)
        scene.play(FadeIn(circle, duration=1.0))
        scene.render()
    """

    def __init__(self, config: EngineConfig) -> None:
        self.config: EngineConfig = config
        random.seed(config.seed)

        self._objects: dict[str, SceneObject] = {}
        self._timeline: Timeline = Timeline(debug=config.debug_mode)
        self.camera: Camera = Camera()
        self._renderer: "BaseRenderer | None" = None

        self._sequential_cursor: float = 0.0

    def add(self, obj: SceneObject) -> None:
        if obj.id in self._objects:
            raise ValueError(f"Scene already contains object with id='{obj.id}'")
        self._objects[obj.id] = obj

    def remove(self, obj_id: str) -> None:
        """Remove a scene object by id."""
        self._objects.pop(obj_id, None)

    def get(self, obj_id: str) -> SceneObject:
        """Retrieve a scene object by id."""
        if obj_id not in self._objects:
            raise KeyError(f"No object with id='{obj_id}'")
        return self._objects[obj_id]

    
    #  Animation scheduling                                               

    def play(
        self,
        animation: Animation,
        at: float | None = None,
        debug: bool | None = None,
    ) -> None:
        """
        Schedule an animation.

        Argumentss:
            animation: The animation to schedule.
            at:        Absolute start time in seconds.  If None, the animation
                       is queued sequentially after the previous one.
            debug:     Override animation debug flag; inherits config if None.
        """
        if debug is None:
            animation.debug = self.config.debug_mode
        else:
            animation.debug = debug

        if at is not None:
            start = at
        else:
            start = self._sequential_cursor

        self._timeline.add(animation, start)
        end = start + animation.delay + animation.duration
        if end > self._sequential_cursor:
            self._sequential_cursor = end
            
            
    #  Rendering loop                                                      

    def render(self) -> None:
        renderer = _make_renderer(self.config)
        self._renderer = renderer
        renderer.initialize(self.config)

        offline = self.config.renderer != "pygame"
        clock = FrameClock(fps=self.config.fps, offline=offline)

        if offline:
            self._render_offline(renderer, clock)
        else:
            self._render_realtime(renderer, clock)

        renderer.finalize()

    def _sorted_objects(self) -> list[SceneObject]:
        return sorted(self._objects.values(), key=lambda o: o.z_order)

    def _draw_frame(self, renderer: "BaseRenderer") -> None:
        cfg = self.config
        for obj in self._sorted_objects():
            if not obj.visible:
                continue
            _draw_with_camera(obj, renderer, self.camera, cfg.width, cfg.height)

    def _render_offline(self, renderer: "BaseRenderer", clock: FrameClock) -> None:
        total = self._timeline.total_duration()
        if total <= 0.0:
            total = 1.0  # at least one frame
        total_frames = max(1, int(total * self.config.fps))

        for _ in range(total_frames):
            clock.tick()
            self.camera.update(clock.dt)
            self._timeline.update(clock.elapsed_time, clock.dt)

            for obj in self._sorted_objects():
                obj.update(clock.dt)

            renderer.begin_frame(self.config.background_color)
            self._draw_frame(renderer)
            renderer.end_frame()

            if self.config.debug_mode:
                print(f"[FRAME] #{clock.frame_index} t={clock.elapsed_time:.3f}s dt={clock.dt:.4f}s")

    def _render_realtime(self, renderer, clock: FrameClock) -> None:
        from renderers.pygame_renderer import PygameRenderer
        pg_renderer: PygameRenderer = renderer  # type: ignore[assignment]

        total = self._timeline.total_duration()

        while pg_renderer.is_running:
            clock.tick()
            self.camera.update(clock.dt)
            self._timeline.update(clock.elapsed_time, clock.dt)

            for obj in self._sorted_objects():
                obj.update(clock.dt)

            renderer.begin_frame(self.config.background_color)
            self._draw_frame(renderer)

            if self.config.debug_mode:
                fps = 1.0 / clock.dt if clock.dt > 0 else 0.0
                pg_renderer.draw_debug_overlay(
                    frame=clock.frame_index,
                    elapsed=clock.elapsed_time,
                    fps=fps,
                    obj_count=len(self._objects),
                )
                print(f"[FRAME] #{clock.frame_index} t={clock.elapsed_time:.3f}s dt={clock.dt:.4f}s")

            renderer.end_frame()

            # Stop once timeline is exhausted
            if total > 0 and clock.elapsed_time >= total + 0.5:
                break


# Camera proxy


class _CameraRenderer:
    

    def __init__(self, renderer: "BaseRenderer", camera: Camera, w: float, h: float) -> None:
        self._r = renderer
        self._cam = camera
        self._w = w
        self._h = h

    def _s(self, wx: float, wy: float) -> tuple[float, float]:
        return self._cam.world_to_screen(wx, wy, self._w, self._h)

    def _sv(self, v: float) -> float:
        return self._cam.scale_value(v)

    def draw_circle(self, x, y, radius, color, alpha, fill=True, stroke_width=2):
        sx, sy = self._s(x, y)
        self._r.draw_circle(sx, sy, self._sv(radius), color, alpha, fill, stroke_width)

    def draw_rect(self, x, y, w, h, color, alpha, fill=True, stroke_width=2):
        # top-left corner in world space: (x, y), center was already offset by shape
        sx, sy = self._s(x + w / 2, y + h / 2)
        sw = self._sv(w)
        sh = self._sv(h)
        self._r.draw_rect(sx - sw / 2, sy - sh / 2, sw, sh, color, alpha, fill, stroke_width)

    def draw_line(self, x1, y1, x2, y2, color, alpha, stroke_width=2):
        sx1, sy1 = self._s(x1, y1)
        sx2, sy2 = self._s(x2, y2)
        self._r.draw_line(sx1, sy1, sx2, sy2, color, alpha, stroke_width)

    def draw_polygon(self, points, color, alpha, fill=True, stroke_width=2):
        spts = [self._s(px, py) for px, py in points]
        self._r.draw_polygon(spts, color, alpha, fill, stroke_width)

    def draw_text(self, x, y, text, font_size, color, alpha):
        sx, sy = self._s(x, y)
        self._r.draw_text(sx, sy, text, font_size, color, alpha)


def _draw_with_camera(
    obj: SceneObject,
    renderer: "BaseRenderer",
    camera: Camera,
    w: float,
    h: float,
) -> None:
    proxy = _CameraRenderer(renderer, camera, w, h)
    obj.render(proxy)  # type: ignore[arg-type]
