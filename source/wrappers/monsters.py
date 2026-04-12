from .base import Collection, Element

class Monster(Element):
    def __init__(self, name, element):
        super().__init__(name, element)

    def get(self):
        name = self.element.find('name')
        if ' [5.5e]' in name.text:
            name.text = name.text.replace(' [5.5e]', '')
        else:
            name.text = name.text+ ' [5e]'
        return self.element
    
class MonsterCollection(Collection):
    def __init__(self):
        super().__init__(Monster)