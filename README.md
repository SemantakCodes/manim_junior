# AnimEngine

A lightweight, modular Python animation engine inspired by Manim — built from
first principles for clarity, performance, and AI-driven scene generation.

---

## Features

- **Two pluggable backends**: real-time Pygame window + offline SVG frame export
- **Timeline-based animation**: sequential and parallel scheduling with `scene.play()`
- **Camera system**: smooth pan and zoom with easing, applied to all draw calls
- **Rich easing library**: linear, quad, cubic, smooth-step variants
- **AI-friendly API**: construct entire scenes programmatically in a loop
- **Deterministic output**: seeded RNG, fixed dt for SVG renders
- **Debug mode**: frame counter overlay, animation lifecycle logging

---

## Install

```bash
# Python 3.10+ required
pip install pygame          # only external dependency

# Or use requirements.txt
pip install -r requirements.txt
```

---

## Quick Start

```python
from animengine import Scene, EngineConfig
from animengine.objects.shapes import Circle
from animengine.animations.fade import FadeIn, FadeOut
from animengine.animations.transform import MoveTo
from animengine.animations.easing import ease_out_cubic

config = EngineConfig(renderer="svg", fps=30, width=1280, height=720)
scene  = Scene(config)

circle = Circle(id="c1", x=0, y=0, radius=50, color=(100, 200, 255))
scene.add(circle)

scene.play(FadeIn(circle, duration=1.0, easing=ease_out_cubic))
scene.play(MoveTo(circle, end_x=300, end_y=100, duration=1.5))
scene.play(FadeOut(circle, duration=0.5))

scene.render()
# → writes SVG frames to output/frames/frame_NNNN.svg
```

---

## Running the Examples

### Pygame (real-time window)

```bash
python -m animengine.main \
    --renderer pygame \
    --scene animengine/examples/example_pygame.py \
    --fps 60
```

Press **ESC** to exit early.

### SVG export

```bash
python -m animengine.main \
    --renderer svg \
    --scene animengine/examples/example_svg.py \
    --output output/svg_demo \
    --fps 30
```

Frames are written to `output/frames/frame_NNNN.svg`.

### AI-generated ring scene

```bash
python -m animengine.main \
    --renderer svg \
    --scene animengine/examples/example_ai_scene.py \
    --output output/ai_scene \
    --fps 30
```

### Debug mode (any example)

```bash
python -m animengine.main \
    --renderer svg \
    --scene animengine/examples/example_svg.py \
    --debug
```

Prints `[FRAME] #N t=X.XXXs dt=...` and `[ANIM] ... started/50%/completed` to stdout.

---

## CLI Reference

```
python -m animengine.main [options]

Options:
  --renderer  {pygame,svg}   Backend (default: svg)
  --width     INT            Canvas width in pixels (default: 1280)
  --height    INT            Canvas height in pixels (default: 720)
  --fps       INT            Frames per second (default: 60)
  --output    PATH           Output path prefix — no extension (default: output/scene)
  --scene     FILE           Python scene file with a run(config) function [required]
  --debug                    Enable debug overlay and logging
  --seed      INT            RNG seed for determinism (default: 42)
  --bg R G B                 Background color as three integers (default: 15 15 25)
```

---

## Writing a Scene

A scene file is any Python module that exposes a `run(config: EngineConfig)` function:

```python
from animengine.core.config import EngineConfig
from animengine.core.scene import Scene
from animengine.objects.shapes import Rectangle
from animengine.animations.fade import FadeIn
from animengine.animations.easing import ease_in_out_quad

def run(config: EngineConfig) -> None:
    scene = Scene(config)

    box = Rectangle(id="box", x=0, y=0, width=200, height=100, color=(255, 200, 0))
    scene.add(box)

    scene.play(FadeIn(box, duration=1.5, easing=ease_in_out_quad))
    scene.render()
```

### Sequential vs parallel scheduling

```python
# Sequential (default) — each play() starts after the previous finishes
scene.play(FadeIn(a, duration=1.0))
scene.play(MoveTo(b, 200, 0, duration=1.0))   # starts at t=1.0

# Parallel — provide an absolute start time with at=
scene.play(FadeIn(a,  duration=1.0), at=0.0)
scene.play(FadeIn(b,  duration=1.0), at=0.5)  # overlaps with a
```

---

## Architecture

```
animengine/
│
├── core/
│   ├── config.py       EngineConfig dataclass (resolution, fps, renderer, seed…)
│   ├── clock.py        FrameClock — fixed dt (SVG) or wall-clock (Pygame)
│   ├── timeline.py     Timeline — schedules & drives Animation tracks
│   └── scene.py        Scene — top-level orchestrator; owns objects, timeline, camera
│
├── renderers/
│   ├── base.py         BaseRenderer ABC — primitive draw interface
│   ├── pygame_renderer.py   Real-time Pygame window with alpha blending
│   └── svg_renderer.py      Offline per-frame SVG via xml.etree (stdlib only)
│
├── objects/
│   ├── base.py         SceneObject ABC + Transform dataclass
│   ├── shapes.py       Circle, Rectangle, Line, Polygon
│   └── text.py         TextObject
│
├── animations/
│   ├── base.py         Animation ABC — update(dt) → apply(t_eased)
│   ├── easing.py       linear, ease_in/out quad/cubic, smooth_step
│   ├── fade.py         FadeIn, FadeOut
│   └── transform.py    MoveTo, ScaleTo, RotateTo
│
├── camera/
│   └── camera.py       Camera — pan_to, zoom_to, world_to_screen()
│
├── examples/
│   ├── example_pygame.py     Real-time demo (circle + rectangle + camera pan)
│   ├── example_svg.py        Same scene, SVG output
│   └── example_ai_scene.py  AI-style batch generation: 5-circle staggered ring
│
└── main.py             CLI entry point (argparse → EngineConfig → scene.run())
```

### Data flow per frame

```
FrameClock.tick()
    │
    ▼
Camera.update(dt)           ← advances internal pan/zoom animations
    │
    ▼
Timeline.update(elapsed, dt) ← drives all Animation objects
    │    each Animation.update(dt) → apply(t_eased) → mutates SceneObject fields
    ▼
SceneObject.update(dt)       ← per-object custom logic (optional)
    │
    ▼
renderer.begin_frame(bg)
    │
    ├─ for each object (sorted by z_order):
    │      _CameraRenderer wraps draw calls
    │      → world_to_screen() applied to every coordinate
    │      → BaseRenderer.draw_*() called with screen-space values
    ▼
renderer.end_frame()         ← Pygame: flip buffer  /  SVG: write .svg file
```

### Renderer isolation

Renderers are **dumb** — they only accept screen-space coordinates and call
platform APIs (`pygame.draw.*` or `xml.etree`). They never import from
`objects/` or `animations/`. Objects call renderer methods; renderers never
call back into objects.

---

## Extending AnimEngine

### Add a new shape

```python
# objects/shapes.py  (or a new file)
from animengine.objects.base import SceneObject

class Star(SceneObject):
    def __init__(self, id, x, y, outer_r, inner_r, points=5, **kwargs):
        super().__init__(id=id, x=x, y=y, **kwargs)
        self.outer_r = outer_r
        self.inner_r = inner_r
        self.num_points = points

    def render(self, renderer):
        import math
        pts = []
        for i in range(self.num_points * 2):
            r = self.outer_r if i % 2 == 0 else self.inner_r
            a = math.radians(i * 180 / self.num_points - 90)
            pts.append((self.transform.x + r * math.cos(a),
                        self.transform.y + r * math.sin(a)))
        renderer.draw_polygon(pts, self.color, self.alpha)
```

### Add a new animation

```python
from animengine.animations.base import Animation

class ColorTo(Animation):
    def __init__(self, target, end_color, duration=1.0, **kwargs):
        super().__init__(target, duration, **kwargs)
        self._start = target.color
        self._end   = end_color

    def apply(self, t):
        self.target.color = tuple(
            int(s + (e - s) * t) for s, e in zip(self._start, self._end)
        )
```

### Add a new renderer

Subclass `BaseRenderer`, implement all abstract methods, then add a branch in
`core/scene.py → _make_renderer()`.

---

## License

MIT
