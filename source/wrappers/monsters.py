from .base import Collection, Element

class Monster(Element):
    def __init__(self, name, element):
        super().__init__(name, element)

    def get(self):
        name = self.element.find('name')
        if ' [2024]' in name.text:
            name.text = name.text.replace(' [2024]', '')
        return self.element
    
class MonsterCollection(Collection):
    def __init__(self):
        super().__init__(Monster)