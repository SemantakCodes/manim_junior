import os
import subprocess
import sys
import glob
import cairosvg

def generate_mp4(frames_dir="output/frames", output_file="output/final_video.mp4", fps=30):
    
    # validation
    if not os.path.exists(frames_dir):
        print("no dir")
        sys.exit(1)
        
    svg_files = sorted(glob.glob(os.path.join(frames_dir, "*.svg")))
    if not svg_files:
        print("No svg")
        sys.exit(1)

    print("converting")

    # convert SVGs to PNGs
    png_frames = []
    for svg_path in svg_files:
        png_path = svg_path.replace(".svg", ".temp.png")
        cairosvg.svg2png(url=svg_path, write_to=png_path)
        png_frames.append(png_path)

    print(" Compiling video ")

    # 3. The FFmpeg command
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
        subprocess.run(command, check=True)
        print(f"\n saved here : {output_file}")
        
    except FileNotFoundError:
        print(f"\n ffmpeg xaina")
    
    finally:
        print("del png")
        for png in png_frames:
            if os.path.exists(png):
                os.remove(png)

if __name__ == "__main__":
    generate_mp4(fps=30)