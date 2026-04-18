"""Engine-wide configuration dataclass."""

from dataclasses import dataclass, field


@dataclass
class EngineConfig:

    width: int = 1280
    height: int = 720
    fps: int = 60
    renderer: str = "pygame"           # "pygame" | "svg"
    output_path: str = "output/"
    output_filename: str = "scene"     # renderer appends extension
    background_color: tuple = (15, 15, 25)
    debug_mode: bool = False
    seed: int = 42
