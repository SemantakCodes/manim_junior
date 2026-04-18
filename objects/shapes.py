"""Concrete shape objects: Circle, Rectangle, Line, Polygon."""

import math
from typing import TYPE_CHECKING

from objects.base import SceneObject

if TYPE_CHECKING:
    from renderers.base import BaseRenderer


class Circle(SceneObject):

    def __init__(
        self,
        id: str,
        x: float = 0.0,
        y: float = 0.0,
        radius: float = 50.0,
        color: tuple = (255, 255, 255),
        alpha: float = 1.0,
        fill: bool = True,
        stroke_width: float = 2.0,
        visible: bool = True,
        z_order: int = 0,
    ) -> None:
        super().__init__(id=id, x=x, y=y, color=color, alpha=alpha,
                         visible=visible, z_order=z_order)
        self.radius: float = radius
        self.fill: bool = fill
        self.stroke_width: float = stroke_width

    def render(self, renderer: "BaseRenderer") -> None:
        if not self.visible:
            return
        renderer.draw_circle(
            x=self.transform.x,
            y=self.transform.y,
            radius=self.radius * self.transform.scale,
            color=self.color,
            alpha=self.alpha,
            fill=self.fill,
            stroke_width=self.stroke_width,
        )


class Rectangle(SceneObject):

    def __init__(
        self,
        id: str,
        x: float = 0.0,
        y: float = 0.0,
        width: float = 100.0,
        height: float = 60.0,
        color: tuple = (255, 255, 255),
        alpha: float = 1.0,
        fill: bool = True,
        stroke_width: float = 2.0,
        visible: bool = True,
        z_order: int = 0,
    ) -> None:
        super().__init__(id=id, x=x, y=y, color=color, alpha=alpha,
                         visible=visible, z_order=z_order)
        self.width: float = width
        self.height: float = height
        self.fill: bool = fill
        self.stroke_width: float = stroke_width

    def render(self, renderer: "BaseRenderer") -> None:
        if not self.visible:
            return
        sw = self.width * self.transform.scale
        sh = self.height * self.transform.scale
        renderer.draw_rect(
            x=self.transform.x - sw / 2,
            y=self.transform.y - sh / 2,
            w=sw,
            h=sh,
            color=self.color,
            alpha=self.alpha,
            fill=self.fill,
            stroke_width=self.stroke_width,
        )


class Line(SceneObject):

    def __init__(
        self,
        id: str,
        x: float = 0.0,
        y: float = 0.0,
        x2: float = 100.0,
        y2: float = 0.0,
        color: tuple = (255, 255, 255),
        alpha: float = 1.0,
        stroke_width: float = 2.0,
        visible: bool = True,
        z_order: int = 0,
    ) -> None:
        super().__init__(id=id, x=x, y=y, color=color, alpha=alpha,
                         visible=visible, z_order=z_order)
        self.x2: float = x2
        self.y2: float = y2
        self.stroke_width: float = stroke_width

    def render(self, renderer: "BaseRenderer") -> None:
        if not self.visible:
            return
        renderer.draw_line(
            x1=self.transform.x,
            y1=self.transform.y,
            x2=self.x2,
            y2=self.y2,
            color=self.color,
            alpha=self.alpha,
            stroke_width=self.stroke_width,
        )


class Polygon(SceneObject):

    def __init__(
        self,
        id: str,
        x: float = 0.0,
        y: float = 0.0,
        points: list[tuple[float, float]] | None = None,
        color: tuple = (255, 255, 255),
        alpha: float = 1.0,
        fill: bool = True,
        stroke_width: float = 2.0,
        visible: bool = True,
        z_order: int = 0,
    ) -> None:
        
        super().__init__(id=id, x=x, y=y, color=color, alpha=alpha,
                         visible=visible, z_order=z_order)
        self.points: list[tuple[float, float]] = points or []
        self.fill: bool = fill
        self.stroke_width: float = stroke_width

    def render(self, renderer: "BaseRenderer") -> None:
        if not self.visible or not self.points:
            return
        s = self.transform.scale
        angle_rad = math.radians(self.transform.rotation)
        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)

        transformed: list[tuple[float, float]] = []
        for px, py in self.points:
            sx, sy = px * s, py * s
            rx = sx * cos_a - sy * sin_a + self.transform.x
            ry = sx * sin_a + sy * cos_a + self.transform.y
            transformed.append((rx, ry))

        renderer.draw_polygon(
            points=transformed,
            color=self.color,
            alpha=self.alpha,
            fill=self.fill,
            stroke_width=self.stroke_width,
        )
