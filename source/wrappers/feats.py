from .base import Collection, Element

class Feat(Element):
    def __init__(self, name, element):
        super().__init__(name, element)
    
class FeatCollection(Collection):
    def __init__(self):
        super().__init__(Feat)