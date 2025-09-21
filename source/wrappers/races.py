from .base import Collection, Element

class Race(Element):
    def __init__(self, name, element):
        super().__init__(name, element)
    
class RaceCollection(Collection):
    def __init__(self):
        super().__init__(Race)