import os
import subprocess
import glob
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM

def compile_video(frames_dir="frames", fps=60):
    # --- Feature: Folder and Naming ---
    video_folder = "Videos"
    if not os.path.exists(video_folder):
        os.makedirs(video_folder)

    file_name = input("Enter the name for your .mp4 file: ")
    output_path = os.path.join(video_folder, f"{file_name}.mp4")

    # --- The Fix: SVG to PNG using svglib ---
    print("🎨 Converting SVGs to PNGs (Windows-friendly mode)...")
    svg_files = sorted(glob.glob(os.path.join(frames_dir, "*.svg")))
    
    for svg in svg_files:
        png = svg.replace('.svg', '.png')
        # Load SVG math and render to PNG pixels
        drawing = svg2rlg(svg)
        renderPM.drawToFile(drawing, png, fmt="PNG")

    # --- The Stitching: FFmpeg ---
    print(f"🎬 Stitching with FFmpeg into {output_path}...")
    ffmpeg_cmd = [
        'ffmpeg', '-y', '-framerate', str(fps),
        '-i', os.path.join(frames_dir, 'frame_%04d.png'),
        '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '18',
        output_path
    ]
    
    try:
        subprocess.run(ffmpeg_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        print(f"✨ Success! Saved to {output_path}")
    except FileNotFoundError:
        print("❌ FFmpeg.exe not found. Make sure it's in your PATH!")

    # Cleanup
    for png in glob.glob(os.path.join(frames_dir, "*.png")):
        os.remove(png)