import time
from typing import List
from ..objects.base import Mobject
from ..renderers.base import BaseRenderer
from ..animations.easing import smooth


class Scene:
    def __init__(self, renderer: BaseRenderer, fps: int = 60):
        self.renderer = renderer
        self.fps = fps
        self.objects: List[Mobject] = []
        self.frame_count = 0
        
    def add(self, mobject: Mobject):
        self.objects.append(mobject)
        
    def play(self, duration=1.0, easing_fn = smooth):
        total_frames = int(duration * self.fps)
        
        # Capture the STARTING state of all objects before the loop begins
        # We need this so we know where we are interpolating FROM
        import copy
        start_states = {id(obj): copy.copy(obj.state) for obj in self.objects}

        for i in range(total_frames):
            # 1. Get raw linear progress (0 to 1)
            alpha = (i + 1) / total_frames 
            
            # 2. Apply the 'Vibe' (Easing)
            eased_alpha = easing_fn(alpha)
            
            # 3. Update objects
            for obj in self.objects:
                start = start_states[id(obj)]
                
                # Update properties based on start -> target
                obj.state.x = start.x + (obj.target_state.x - start.x) * eased_alpha
                obj.state.y = start.y + (obj.target_state.y - start.y) * eased_alpha
                obj.state.opacity = start.opacity + (obj.target_state.opacity - start.opacity) * eased_alpha
                obj.state.scale = start.scale + (obj.target_state.scale - start.scale) * eased_alpha
            
            # 4. Render
            self.renderer.render_frame(self.objects, self.frame_count)
            self.frame_count += 1