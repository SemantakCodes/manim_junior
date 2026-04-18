import os
import subprocess
import sys
import glob

try:
    import cairosvg
except ImportError:
    print("❌ Error: 'cairosvg' library not found.")
    print("Please install it using: pip install cairosvg")
    sys.exit(1)

def generate_mp4(frames_dir="output/frames", output_file="output/final_video.mp4", fps=30):
    """Converts SVG frames to PNG and then stitches them into an MP4."""
    
    # 1. Validation
    if not os.path.exists(frames_dir):
        print(f"❌ Error: The directory '{frames_dir}' does not exist.")
        sys.exit(1)
        
    svg_files = sorted(glob.glob(os.path.join(frames_dir, "*.svg")))
    if not svg_files:
        print(f"❌ Error: No .svg files found in '{frames_dir}'.")
        sys.exit(1)

    print(f"🚀 Found {len(svg_files)} SVGs. Starting conversion to PNG...")

    # 2. Convert SVGs to PNGs
    # FFmpeg handles PNGs much more reliably than SVGs across different systems.
    png_frames = []
    for svg_path in svg_files:
        png_path = svg_path.replace(".svg", ".temp.png")
        cairosvg.svg2png(url=svg_path, write_to=png_path)
        png_frames.append(png_path)

    print(f"✅ Conversion complete. Compiling video at {fps} FPS...")

    # 3. The FFmpeg command
    # Using the .temp.png pattern created above
    command = [
        "ffmpeg",
        "-y",
        "-framerate", str(fps),
        "-i", os.path.join(frames_dir, "frame_%04d.temp.png"), 
        "-c:v", "libx264",
        "-crf", "17",        # High quality setting (lower is better, 17-23 is standard)
        "-pix_fmt", "yuv420p",
        output_file
    ]

    try:
        # Run FFmpeg
        subprocess.run(command, check=True)
        print(f"\n🎉 Success! Video saved to: {output_file}")
        
    except FileNotFoundError:
        print("\n❌ Error: FFmpeg is not installed or not in your system's PATH.")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ FFmpeg failed with error code {e.returncode}.")
    
    finally:
        # 4. Cleanup temporary PNG files
        print("🧹 Cleaning up temporary PNG frames...")
        for png in png_frames:
            if os.path.exists(png):
                os.remove(png)

if __name__ == "__main__":
    generate_mp4(fps=30)