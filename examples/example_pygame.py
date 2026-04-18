"""
Pygame example scene:
  1. Fade in a blue circle at center
  2. Move it top-right while scaling 2×
  3. Fade in a red rectangle at bottom-left, rotate 360°
  4. Pan camera to follow the circle
  5. Fade everything out

Run directly:
    python examples/example_pygame.py
Or via CLI:
    python main.py --renderer pygame --scene examples/example_pygame.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config import EngineConfig
from core.scene import Scene
from objects.shapes import Circle, Rectangle
from objects.text import TextObject
from animations.fade import FadeIn, FadeOut
from animations.transform import MoveTo, ScaleTo, RotateTo
from animations.easing import ease_out_cubic, ease_in_out_quad


def run(config: EngineConfig) -> None:
    """Build and render the Pygame demo scene."""
    config.renderer = "pygame"
    scene = Scene(config)

    # ── Objects ──────────────────────────────────────────────────────────
    circle = Circle(
        id="hero_circle",
        x=0, y=0,
        radius=60,
        color=(80, 160, 255),
        alpha=0.0,
        z_order=1,
    )

    rect = Rectangle(
        id="bottom_rect",
        x=-300, y=200,
        width=120, height=70,
        color=(255, 80, 80),
        alpha=0.0,
        z_order=0,
    )

    label = TextObject(
        id="title",
        x=-160, y=-280,
        text="AnimEngine Demo",
        font_size=28,
        color=(220, 220, 220),
        alpha=0.0,
        z_order=2,
    )

    scene.add(circle)
    scene.add(rect)
    scene.add(label)

    # ── Timeline ─────────────────────────────────────────────────────────

    # Label fades in first
    scene.play(FadeIn(label, duration=0.8, easing=ease_out_cubic))

    # Circle fades in
    scene.play(FadeIn(circle, duration=1.0, easing=ease_out_cubic))

    # Simultaneously move & scale the circle
    scene.play(MoveTo(circle, end_x=300, end_y=-150, duration=1.8, easing=ease_out_cubic), at=1.8)
    scene.play(ScaleTo(circle, end_scale=2.0, duration=1.8, easing=ease_out_cubic), at=1.8)

    # Rectangle fades in at bottom-left
    scene.play(FadeIn(rect, duration=0.8, easing=ease_out_cubic), at=1.8)

    # Rotate the rectangle 360°
    scene.play(RotateTo(rect, end_rotation=360.0, duration=2.0, easing=ease_in_out_quad), at=2.6)

    # Camera pans to follow the circle's destination
    scene.camera.pan_to(150, -75, duration=1.8, easing=ease_out_cubic)

    # Fade everything out at the end
    fade_start = 4.8
    scene.play(FadeOut(circle, duration=0.8), at=fade_start)
    scene.play(FadeOut(rect,   duration=0.8), at=fade_start)
    scene.play(FadeOut(label,  duration=0.8), at=fade_start)

    scene.render()


if __name__ == "__main__":
    cfg = EngineConfig(renderer="pygame", fps=60, width=1280, height=720)
    run(cfg)
