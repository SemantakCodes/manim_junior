# examples/test_preview.py
from manimjr.core.scene import Scene
from manimjr.renderers.pygame_renderer import PygameRenderer
from manimjr.objects.base import Mobject

# 1. Setup
renderer = PygameRenderer()
renderer.setup()
scene = Scene(renderer)

# 2. Create a Square Math Object manually
class Square(Mobject):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.width = 100
        self.height = 100

sq = Square(x=-300, color="#00FFCC")
scene.add(sq)

# 3. Define a simple target and play
sq.target_state.x = 300
scene.play(duration=10.0) # SQUARE MOVE FOR 2 SECONDS GO BRRRRRRRRRRRRRRRRRRRRRR

renderer.cleanup()