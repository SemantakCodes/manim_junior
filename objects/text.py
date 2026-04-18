"""Text scene object."""

from typing import TYPE_CHECKING

from objects.base import SceneObject

if TYPE_CHECKING:
    from renderers.base import BaseRenderer


class TextObject(SceneObject):

    def __init__(
        self,
        id: str,
        x: float = 0.0,
        y: float = 0.0,
        text: str = "",
        font_size: int = 24,
        color: tuple = (255, 255, 255),
        alpha: float = 1.0,
        visible: bool = True,
        z_order: int = 0,
    ) -> None:
        super().__init__(id=id, x=x, y=y, color=color, alpha=alpha,
                         visible=visible, z_order=z_order)
        self.text: str = text
        self.font_size: int = font_size

    def render(self, renderer: "BaseRenderer") -> None:
        if not self.visible:
            return
        scaled_size = max(1, int(self.font_size * self.transform.scale))
        renderer.draw_text(
            x=self.transform.x,
            y=self.transform.y,
            text=self.text,
            font_size=scaled_size,
            color=self.color,
            alpha=self.alpha,
        )
