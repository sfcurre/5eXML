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
        if ' [5.5e]' in name.text:
            name.text = name.text.replace(' [5.5e]', '')
        else:
            name.text = name.text+ ' [5e]'
        return self.element
    
class FeatCollection(Collection):
    def __init__(self):
        super().__init__(Feat)