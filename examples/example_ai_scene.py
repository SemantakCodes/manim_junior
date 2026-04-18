"""
AI-style programmatic scene generation:
  5 circles arranged in a ring, each fading in with a 0.2s stagger.
  Demonstrates batch scene construction as an AI system would generate it.

Run directly:
    python examples/example_ai_scene.py
Or via CLI:
    python main.py --renderer svg --scene examples/example_ai_scene.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import math
import colorsys

from core.config import EngineConfig
from core.scene import Scene
from objects.shapes import Circle
from objects.text import TextObject
from animations.fade import FadeIn, FadeOut
from animations.transform import MoveTo, ScaleTo
from animations.easing import ease_out_cubic, ease_in_out_quad


def hsv_to_rgb(h: float, s: float, v: float) -> tuple:
    """Convert HSV (0–1 each) to an (R, G, B) tuple with values 0–255."""
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return (int(r * 255), int(g * 255), int(b * 255))


def run(config: EngineConfig) -> None:
    """
    AI-generated scene: programmatically build a ring of 5 staggered circles.
    Each circle fades in, pulses (scales up then back), then fades out.
    A center label fades in after the ring is complete.
    """
    config.renderer = config.renderer  # respect whatever was passed in
    scene = Scene(config)

    NUM_CIRCLES = 5
    RING_RADIUS = 200.0
    CIRCLE_RADIUS = 30.0
    STAGGER = 0.2          # seconds between each circle fade-in
    FADE_DURATION = 0.5
    PULSE_DURATION = 0.6
    RING_COMPLETE = NUM_CIRCLES * STAGGER + FADE_DURATION  # ~1.5s

    # ── Batch-generate ring circles ───────────────────────────────────────
    circles: list[Circle] = []
    for i in range(NUM_CIRCLES):
        angle_deg = (360.0 / NUM_CIRCLES) * i
        angle_rad = math.radians(angle_deg)
        cx = math.cos(angle_rad) * RING_RADIUS
        cy = math.sin(angle_rad) * RING_RADIUS
        color = hsv_to_rgb(i / NUM_CIRCLES, 1.0, 1.0)

        c = Circle(
            id=f"ring_{i}",
            x=cx, y=cy,
            radius=CIRCLE_RADIUS,
            color=color,
            alpha=0.0,
            z_order=1,
        )
        scene.add(c)
        circles.append(c)

        fade_in_start = i * STAGGER
        scene.play(FadeIn(c, duration=FADE_DURATION, easing=ease_out_cubic), at=fade_in_start)

        # Pulse: scale up to 1.5× then back to 1.0×
        pulse_start = fade_in_start + FADE_DURATION
        scene.play(ScaleTo(c, end_scale=1.5, duration=PULSE_DURATION / 2,
                           easing=ease_in_out_quad), at=pulse_start)
        scene.play(ScaleTo(c, end_scale=1.0, duration=PULSE_DURATION / 2,
                           easing=ease_in_out_quad), at=pulse_start + PULSE_DURATION / 2)

    # ── Center label ──────────────────────────────────────────────────────
    label = TextObject(
        id="center_label",
        x=-80, y=-15,
        text="AI RING",
        font_size=32,
        color=(255, 255, 255),
        alpha=0.0,
        z_order=2,
    )
    scene.add(label)
    scene.play(FadeIn(label, duration=0.6, easing=ease_out_cubic), at=RING_COMPLETE)

    # ── Rotate the whole ring by animating each circle's position ─────────
    # (simple orbit: over 2s each circle moves to the next position)
    orbit_start = RING_COMPLETE + 0.8
    ORBIT_DURATION = 2.0
    for i, c in enumerate(circles):
        next_angle_deg = (360.0 / NUM_CIRCLES) * ((i + 1) % NUM_CIRCLES)
        next_rad = math.radians(next_angle_deg)
        nx = math.cos(next_rad) * RING_RADIUS
        ny = math.sin(next_rad) * RING_RADIUS
        scene.play(
            MoveTo(c, end_x=nx, end_y=ny, duration=ORBIT_DURATION, easing=ease_in_out_quad),
            at=orbit_start,
        )

    # ── Fade everything out ───────────────────────────────────────────────
    fade_out_start = orbit_start + ORBIT_DURATION + 0.3
    for c in circles:
        scene.play(FadeOut(c, duration=0.6), at=fade_out_start)
    scene.play(FadeOut(label, duration=0.6), at=fade_out_start)

    print(f"[AI Scene] {NUM_CIRCLES} circles  stagger={STAGGER}s  "
          f"total≈{fade_out_start + 0.6:.1f}s")
    scene.render()


if __name__ == "__main__":
    cfg = EngineConfig(renderer="svg", fps=30, width=1280, height=720,
                       output_path="output/ai_scene")
    run(cfg)
