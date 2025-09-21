from .base import Collection, Element

class Monster(Element):
    def __init__(self, name, element):
        super().__init__(name, element)
    
class MonsterCollection(Collection):
    def __init__(self):
        super().__init__(Monster)