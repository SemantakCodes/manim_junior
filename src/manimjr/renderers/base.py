import abc
class BaseRenderer(abc.ABC):
    @abc.abstractmethod
    def setup(self):
        pass
    
    @abc.abstractmethod
    def render_frame(self, objects: list, fame_number : int):
        pass
    
    @abc.abstractmethod
    def cleanup(self):
        pass