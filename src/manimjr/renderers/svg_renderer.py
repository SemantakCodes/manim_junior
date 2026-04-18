import os
from .base import BaseRenderer

class SVGRenderer(BaseRenderer):
    def __init__(self, output_dir="frames", width=1280, height=720):
        self.output_dir = output_dir
        self.width = width
        self.height = height
        # Standard SVG header for a dark background
        self.header = (
            f'<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" '
            'xmlns="http://www.w3.org/2000/svg" '
            'style="background-color: #0A0A0A;">\n'
        )

    def setup(self):
        """Ensure the output directory exists."""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def _to_screen_coords(self, x, y):
        """Map math coordinates to SVG coordinates (origin top-left)."""
        screen_x = self.width / 2 + x
        screen_y = self.height / 2 - y
        return screen_x, screen_y

    def render_frame(self, objects, frame_number):
        """Write the math state to a text file."""
        frame_path = os.path.join(self.output_dir, f"frame_{frame_number:04d}.svg")
        
        with open(frame_path, "w") as f:
            f.write(self.header)
            
            for obj in objects:
                x, y = self._to_screen_coords(obj.state.x, obj.state.y)
                color = obj.state.color
                opacity = obj.state.opacity
                
                # Render logic for shapes
                if hasattr(obj, 'radius'):
                    r = obj.radius * obj.state.scale
                    f.write(f'  <circle cx="{x}" cy="{y}" r="{r}" fill="{color}" fill-opacity="{opacity}" />\n')
                elif hasattr(obj, 'width'):
                    w = obj.width * obj.state.scale
                    h = obj.height * obj.state.scale
                    f.write(f'  <rect x="{x-w/2}" y="{y-h/2}" width="{w}" height="{h}" fill="{color}" fill-opacity="{opacity}" />\n')
            
            f.write('</svg>')

    def cleanup(self):
        print(f"✅ Generated SVG frames in ./{self.output_dir}")