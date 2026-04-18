"""CLI entry point — dynamically loads and runs a scene script."""

import argparse
import importlib.util
import os
import sys
import subprocess
import glob

# Try to import cairosvg for the conversion step
try:
    import cairosvg
    CAIRO_AVAILABLE = True
except (ImportError, OSError):
    CAIRO_AVAILABLE = False

# Ensure the project root is importable regardless of working directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.config import EngineConfig

def compile_video(config: EngineConfig):
    """Helper to convert SVG frames to PNG and stitch them into an MP4."""
    frames_dir = os.path.join(config.output_path, "frames")
    output_file = os.path.join(config.output_path, f"{config.output_filename}.mp4")

    if not os.path.exists(frames_dir):
        print(f"[Video] ❌ Frames directory not found: {frames_dir}")
        return

    svg_files = sorted(glob.glob(os.path.join(frames_dir, "*.svg")))
    if not svg_files:
        print("[Video] ❌ No SVG frames found to compile.")
        return

    if not CAIRO_AVAILABLE:
        print("[Video] ❌ Cannot compile: cairosvg or Cairo DLLs missing.")
        return

    print(f"[Video] Converting {len(svg_files)} SVGs to temporary PNGs...")
    
    # 1. Convert to temporary PNGs
    png_pattern = os.path.join(frames_dir, "temp_frame_%04d.png")
    for i, svg_path in enumerate(svg_files):
        target_png = os.path.join(frames_dir, f"temp_frame_{i+1:04d}.png")
        cairosvg.svg2png(url=svg_path, write_to=target_png)

    # 2. Run FFmpeg
    print(f"[Video] Stitching with FFmpeg at {config.fps} FPS...")
    command = [
        "ffmpeg", "-y",
        "-framerate", str(config.fps),
        "-i", png_pattern,
        "-c:v", "libx264",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        output_file
    ]

    try:
        subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        print(f"[Video] ✅ Success! Created: {output_file}")
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"[Video] ❌ FFmpeg failed. Ensure FFmpeg is installed and in your PATH.")
    finally:
        # 3. Cleanup
        temp_pngs = glob.glob(os.path.join(frames_dir, "temp_frame_*.png"))
        for png in temp_pngs:
            os.remove(png)

def load_scene_module(path: str):
    """Dynamically import a Python file and return its module object."""
    abs_path = os.path.abspath(path)
    if not os.path.exists(abs_path):
        print(f"[ERROR] Scene file not found: {abs_path}")
        sys.exit(1)

    spec = importlib.util.spec_from_file_location("_scene_module", abs_path)
    if spec is None or spec.loader is None:
        print(f"[ERROR] Could not load scene module: {abs_path}")
        sys.exit(1)

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return module

def main() -> None:
    """Parse CLI args, build EngineConfig, and run the requested scene."""
    parser = argparse.ArgumentParser(
        description="AnimEngine — render a Python scene file",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "--renderer",
        choices=["pygame", "svg"],
        default="svg",
        help="Rendering backend (default: svg)",
    )
    parser.add_argument("--width",  type=int, default=1280, help="Canvas width in pixels")
    parser.add_argument("--height", type=int, default=720,  help="Canvas height in pixels")
    parser.add_argument("--fps",    type=int, default=60,   help="Frames per second")
    parser.add_argument(
        "--output",
        default="output/scene",
        help="Output path prefix, e.g. output/my_scene (no extension)",
    )
    parser.add_argument(
        "--scene",
        required=True,
        help="Path to a Python scene file exposing a run(config) function",
    )
    parser.add_argument("--video", action="store_true", default=True, help="Compile to MP4 after rendering (SVG only)")
    parser.add_argument("--no-video", action="store_false", dest="video", help="Disable MP4 compilation")
    parser.add_argument("--debug", action="store_true", help="Enable debug overlay/logging")
    parser.add_argument("--seed",  type=int, default=42,   help="RNG seed for determinism")
    parser.add_argument(
        "--bg",
        nargs=3,
        type=int,
        metavar=("R", "G", "B"),
        default=[15, 15, 25],
        help="Background color as R G B values (default: 15 15 25)",
    )

    args = parser.parse_args()

    output_path = os.path.dirname(args.output) or "output/"
    output_filename = os.path.basename(args.output) or "scene"

    config = EngineConfig(
        width=args.width,
        height=args.height,
        fps=args.fps,
        renderer=args.renderer,
        output_path=output_path,
        output_filename=output_filename,
        background_color=tuple(args.bg),
        debug_mode=args.debug,
        seed=args.seed,
    )

    module = load_scene_module(args.scene)

    if not hasattr(module, "run"):
        print(f"[ERROR] Scene file must define a run(config) function: {args.scene}")
        sys.exit(1)

    print(f"[AnimEngine] renderer={config.renderer}  {config.width}x{config.height}  {config.fps}fps")
    print(f"[AnimEngine] scene={args.scene}")
    
    # Run the actual animation engine
    module.run(config)
    
    # If using SVG and video flag is set, compile the video
    if config.renderer == "svg" and args.video:
        compile_video(config)

    print("[AnimEngine] Done.")


if __name__ == "__main__":
    main()