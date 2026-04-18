"""Offline SVG renderer — writes per-frame SVG files using stdlib xml.etree."""

import os
import xml.etree.ElementTree as ET
from typing import TYPE_CHECKING

from renderers.base import BaseRenderer

if TYPE_CHECKING:
    from core.config import EngineConfig


def _rgb_to_hex(color: tuple) -> str:
    """Convert (R, G, B) tuple to '#RRGGBB' hex string."""
    r, g, b = (max(0, min(255, int(c))) for c in color)
    return f"#{r:02X}{g:02X}{b:02X}"


def _opacity(alpha: float) -> str:
    """Clamp alpha and return as a string for SVG opacity attributes."""
    return f"{max(0.0, min(1.0, alpha)):.3f}"


class SVGRenderer(BaseRenderer):
    """Writes one SVG file per frame into output_path/frames/."""

    def __init__(self) -> None:
        """Initialize renderer state."""
        self._config: "EngineConfig | None" = None
        self._frame_index: int = 0
        self._current_root: ET.Element | None = None
        self._current_group: ET.Element | None = None
        self._bg_color: tuple = (0, 0, 0)
        self._frames_dir: str = ""

    def initialize(self, config: "EngineConfig") -> None:
        """Create output directories."""
        self._config = config
        self._frames_dir = os.path.join(config.output_path, "frames")
        os.makedirs(self._frames_dir, exist_ok=True)
        self._frame_index = 0

    def begin_frame(self, background_color: tuple) -> None:
        """Create the SVG root element for this frame."""
        cfg = self._config
        self._bg_color = background_color
        self._current_root = ET.Element("svg", {
            "xmlns": "http://www.w3.org/2000/svg",
            "width": str(cfg.width),
            "height": str(cfg.height),
            "viewBox": f"0 0 {cfg.width} {cfg.height}",
        })
        # Background rect
        ET.SubElement(self._current_root, "rect", {
            "x": "0", "y": "0",
            "width": str(cfg.width),
            "height": str(cfg.height),
            "fill": _rgb_to_hex(background_color),
        })
        self._current_group = ET.SubElement(self._current_root, "g", {
            "id": f"frame-{self._frame_index}",
        })
        if cfg.debug_mode:
            comment = ET.Comment(f" frame={self._frame_index} ")
            self._current_group.append(comment)

    def end_frame(self) -> None:
        """Serialize current SVG to a numbered file."""
        if self._current_root is None:
            return
        filename = f"frame_{self._frame_index:04d}.svg"
        path = os.path.join(self._frames_dir, filename)
        tree = ET.ElementTree(self._current_root)
        ET.indent(tree, space="  ")
        tree.write(path, encoding="unicode", xml_declaration=False)
        self._frame_index += 1
        self._current_root = None
        self._current_group = None

    def finalize(self) -> None:
        """No-op for frame-based SVG output; all frames already written."""
        pass

    # ------------------------------------------------------------------ #
    #  Draw calls                                                          #
    # ------------------------------------------------------------------ #

    def _g(self) -> ET.Element:
        """Return the current frame group (assert safety)."""
        if self._current_group is None:
            raise RuntimeError("SVGRenderer: begin_frame() not called")
        return self._current_group

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
        """Append a <circle> element."""
        attrib: dict[str, str] = {
            "cx": f"{x:.2f}",
            "cy": f"{y:.2f}",
            "r": f"{radius:.2f}",
        }
        if fill:
            attrib["fill"] = _rgb_to_hex(color)
            attrib["fill-opacity"] = _opacity(alpha)
        else:
            attrib["fill"] = "none"
            attrib["stroke"] = _rgb_to_hex(color)
            attrib["stroke-opacity"] = _opacity(alpha)
            attrib["stroke-width"] = f"{stroke_width:.1f}"
        ET.SubElement(self._g(), "circle", attrib)

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
        """Append a <rect> element."""
        attrib: dict[str, str] = {
            "x": f"{x:.2f}",
            "y": f"{y:.2f}",
            "width": f"{w:.2f}",
            "height": f"{h:.2f}",
        }
        if fill:
            attrib["fill"] = _rgb_to_hex(color)
            attrib["fill-opacity"] = _opacity(alpha)
        else:
            attrib["fill"] = "none"
            attrib["stroke"] = _rgb_to_hex(color)
            attrib["stroke-opacity"] = _opacity(alpha)
            attrib["stroke-width"] = f"{stroke_width:.1f}"
        ET.SubElement(self._g(), "rect", attrib)

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
        """Append a <line> element."""
        ET.SubElement(self._g(), "line", {
            "x1": f"{x1:.2f}", "y1": f"{y1:.2f}",
            "x2": f"{x2:.2f}", "y2": f"{y2:.2f}",
            "stroke": _rgb_to_hex(color),
            "stroke-opacity": _opacity(alpha),
            "stroke-width": f"{stroke_width:.1f}",
        })

    def draw_polygon(
        self,
        points: list[tuple],
        color: tuple,
        alpha: float,
        fill: bool = True,
        stroke_width: float = 2,
    ) -> None:
        """Append a <polygon> element."""
        pts_str = " ".join(f"{px:.2f},{py:.2f}" for px, py in points)
        attrib: dict[str, str] = {"points": pts_str}
        if fill:
            attrib["fill"] = _rgb_to_hex(color)
            attrib["fill-opacity"] = _opacity(alpha)
        else:
            attrib["fill"] = "none"
            attrib["stroke"] = _rgb_to_hex(color)
            attrib["stroke-opacity"] = _opacity(alpha)
            attrib["stroke-width"] = f"{stroke_width:.1f}"
        ET.SubElement(self._g(), "polygon", attrib)

    def draw_text(
        self,
        x: float,
        y: float,
        text: str,
        font_size: int,
        color: tuple,
        alpha: float,
    ) -> None:
        """Append a <text> element."""
        el = ET.SubElement(self._g(), "text", {
            "x": f"{x:.2f}",
            "y": f"{y:.2f}",
            "font-size": str(font_size),
            "font-family": "monospace",
            "fill": _rgb_to_hex(color),
            "fill-opacity": _opacity(alpha),
        })
        el.text = text
