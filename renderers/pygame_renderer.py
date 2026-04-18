"""Real-time Pygame renderer backend."""

import math
from typing import TYPE_CHECKING

from renderers.base import BaseRenderer

if TYPE_CHECKING:
    from core.config import EngineConfig


class PygameRenderer(BaseRenderer):
    """Renders a scene in a live Pygame window with alpha blending."""

    def __init__(self) -> None:
        """Initialize renderer state (no Pygame calls yet)."""
        self._config: "EngineConfig | None" = None
        self._screen = None       # pygame.Surface
        self._font = None         # pygame.font.Font
        self._running: bool = True

    # ------------------------------------------------------------------ #
    #  Lifecycle                                                           #
    # ------------------------------------------------------------------ #

    def initialize(self, config: "EngineConfig") -> None:
        """Create the Pygame window and font."""
        import pygame
        self._config = config
        pygame.init()
        pygame.font.init()
        self._screen = pygame.display.set_mode((config.width, config.height))
        pygame.display.set_caption("AnimEngine")
        self._font = pygame.font.SysFont("monospace", 18)
        self._debug_font = pygame.font.SysFont("monospace", 14)
        self._running = True

    def begin_frame(self, background_color: tuple) -> None:
        """Clear screen to background color and process OS events."""
        import pygame
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self._running = False
        self._screen.fill(background_color)

    def end_frame(self) -> None:
        """Flip the display buffer."""
        import pygame
        pygame.display.flip()

    def finalize(self) -> None:
        """Quit Pygame."""
        import pygame
        pygame.quit()

    @property
    def is_running(self) -> bool:
        """False after ESC or window close."""
        return self._running

    # ------------------------------------------------------------------ #
    #  Draw calls                                                          #
    # ------------------------------------------------------------------ #

    def draw_circle(
        self,
        x: float,
        y: float,
        radius: float,
        color: tuple,
        alpha: float,
        fill: bool = True,
        stroke_width: float = 2,
    ) -> None:
        """Draw an alpha-blended circle."""
        import pygame
        if alpha <= 0.0 or radius <= 0:
            return
        surf = pygame.Surface((int(radius * 2 + 4), int(radius * 2 + 4)), pygame.SRCALPHA)
        a = int(max(0, min(255, alpha * 255)))
        cx, cy = int(radius + 2), int(radius + 2)
        r = int(radius)
        if fill:
            pygame.draw.circle(surf, (*color, a), (cx, cy), r)
        else:
            pygame.draw.circle(surf, (*color, a), (cx, cy), r, int(stroke_width))
        self._screen.blit(surf, (int(x - radius - 2), int(y - radius - 2)))

    def draw_rect(
        self,
        x: float,
        y: float,
        w: float,
        h: float,
        color: tuple,
        alpha: float,
        fill: bool = True,
        stroke_width: float = 2,
    ) -> None:
        """Draw an alpha-blended rectangle."""
        import pygame
        if alpha <= 0.0 or w <= 0 or h <= 0:
            return
        surf = pygame.Surface((int(w), int(h)), pygame.SRCALPHA)
        a = int(max(0, min(255, alpha * 255)))
        rect = pygame.Rect(0, 0, int(w), int(h))
        if fill:
            pygame.draw.rect(surf, (*color, a), rect)
        else:
            pygame.draw.rect(surf, (*color, a), rect, int(stroke_width))
        self._screen.blit(surf, (int(x), int(y)))

    def draw_line(
        self,
        x1: float,
        y1: float,
        x2: float,
        y2: float,
        color: tuple,
        alpha: float,
        stroke_width: float = 2,
    ) -> None:
        """Draw an alpha-blended line."""
        import pygame
        if alpha <= 0.0:
            return
        # Build minimal bounding surface
        mx, my = min(x1, x2), min(y1, y2)
        bw = max(int(abs(x2 - x1)) + int(stroke_width) + 4, 1)
        bh = max(int(abs(y2 - y1)) + int(stroke_width) + 4, 1)
        surf = pygame.Surface((bw, bh), pygame.SRCALPHA)
        a = int(max(0, min(255, alpha * 255)))
        lx1, ly1 = int(x1 - mx + stroke_width / 2 + 2), int(y1 - my + stroke_width / 2 + 2)
        lx2, ly2 = int(x2 - mx + stroke_width / 2 + 2), int(y2 - my + stroke_width / 2 + 2)
        pygame.draw.line(surf, (*color, a), (lx1, ly1), (lx2, ly2), max(1, int(stroke_width)))
        self._screen.blit(surf, (int(mx - stroke_width / 2 - 2), int(my - stroke_width / 2 - 2)))

    def draw_polygon(
        self,
        points: list[tuple],
        color: tuple,
        alpha: float,
        fill: bool = True,
        stroke_width: float = 2,
    ) -> None:
        """Draw an alpha-blended polygon."""
        import pygame
        if alpha <= 0.0 or len(points) < 3:
            return
        xs = [p[0] for p in points]
        ys = [p[1] for p in points]
        mx, my = min(xs), min(ys)
        bw = max(int(max(xs) - mx) + int(stroke_width) + 4, 1)
        bh = max(int(max(ys) - my) + int(stroke_width) + 4, 1)
        surf = pygame.Surface((bw, bh), pygame.SRCALPHA)
        a = int(max(0, min(255, alpha * 255)))
        local = [(int(px - mx + 2), int(py - my + 2)) for px, py in points]
        if fill:
            pygame.draw.polygon(surf, (*color, a), local)
        else:
            pygame.draw.polygon(surf, (*color, a), local, max(1, int(stroke_width)))
        self._screen.blit(surf, (int(mx - 2), int(my - 2)))

    def draw_text(
        self,
        x: float,
        y: float,
        text: str,
        font_size: int,
        color: tuple,
        alpha: float,
    ) -> None:
        """Render text at screen position (x, y)."""
        import pygame
        if alpha <= 0.0:
            return
        font = pygame.font.SysFont("monospace", font_size)
        surf = font.render(text, True, color)
        surf.set_alpha(int(max(0, min(255, alpha * 255))))
        self._screen.blit(surf, (int(x), int(y)))

    def draw_debug_overlay(
        self,
        frame: int,
        elapsed: float,
        fps: float,
        obj_count: int,
    ) -> None:
        """Render debug info overlay (top-left)."""
        import pygame
        lines = [
            f"Frame: {frame}",
            f"Time:  {elapsed:.2f}s",
            f"FPS:   {fps:.1f}",
            f"Objs:  {obj_count}",
        ]
        y = 8
        for line in lines:
            surf = self._debug_font.render(line, True, (255, 255, 255))
            self._screen.blit(surf, (8, y))
            y += 16
