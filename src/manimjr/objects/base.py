import abc
from dataclasses import dataclass, field, asdict
from typing import Dict, Any

@dataclass
class ObjectState:
    # the raw mathematical data of an object at any given frame.
    x : float = 0.0
    y: float = 0.0
    scale : float = 1.0
    opacity : float = 1.0
    color : str = "#FFFFFF" #hex used here is white
    
class AnimationProxy:
    def __init__(self, mobject):
        self.mobject = mobject

    def __getattr__(self, name):
        # This catches any method call (like .move_to) 
        # and tells the mobject to prepare for a play() call.
        def method(*args, **kwargs):
            attr = getattr(self.mobject, name)
            return attr(*args, **kwargs)
        return method

class Mobject:
    def __init__(self, **kwargs):
        self.state = ObjectState(**kwargs)
        self.target_state = ObjectState(**kwargs)
        self.animate = AnimationProxy(self) # The magic bridge
        
    def move_to(self, x, y):
        self.target_state.x = x
        self.target_state.y = y
        return self

    def set_opacity(self, value):
        self.target_state.opacity = value
        return self 