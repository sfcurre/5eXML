from .base import Collection, Element

class Feat(Element):
    def __init__(self, name, element):
        super().__init__(name, element)

    def in_filter(self, sources):
        abrv = sources.match(self.element)
        if abrv in ['SotDQ', 'ERLW', 'VRGtR']:
            return False
        if 'Draconic Gift:' in self.name:
            return False
        return super().in_filter(sources)
    
    def get(self):
        name = self.element.find('name')
        if ' [2024]' in name.text:
            name.text = name.text.replace(' [2024]', '')
        return self.element
    
class FeatCollection(Collection):
    def __init__(self):
        super().__init__(Feat)