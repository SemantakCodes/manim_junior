import pygame
import sys
from .base import BaseRenderer

class PygameRenderer(BaseRenderer):
    def __init__(self, width=1280, height=720, bg_color=(10, 10, 10)):
        self.width = width
        self.height = height
        self.bg_color = bg_color
        self.screen = None
        self.clock = None

    def setup(self):
        
        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("MiniManim Preview")
        self.clock = pygame.time.Clock()

    def _to_screen_coords(self, x, y):
        
        screen_x = int(self.width / 2 + x)
        screen_y = int(self.height / 2 - y)
        return (screen_x, screen_y)

    def render_frame(self, objects, frame_number):
        
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.cleanup()
                sys.exit()

        #Clear the screen
        self.screen.fill(self.bg_color)

        #  Draw object
        for obj in objects:
            pos = self._to_screen_coords(obj.state.x, obj.state.y)
            
            # color conversion
            color = pygame.Color(obj.state.color)
            color.a = int(obj.state.opacity * 255) #boom transparency

            # dushra shape lao 
            if hasattr(obj, 'radius'):
                pygame.draw.circle(self.screen, color, pos, int(obj.state.scale * obj.radius))
            elif hasattr(obj, 'width'):
                # Draw rect centered at pos
                rect_w = obj.width * obj.state.scale
                rect_h = obj.height * obj.state.scale
                rect = pygame.Rect(pos[0] - rect_w/2, pos[1] - rect_h/2, rect_w, rect_h)
                pygame.draw.rect(self.screen, color, rect)

        #  Push  to the display
        pygame.display.flip()
        
        # Maintain the framerate 
        self.clock.tick(60)

    def cleanup(self):
        """closes the Pygame window."""
        pygame.quit()