from .base import Collection, Element

class Race(Element):
    def __init__(self, name, element):
        super().__init__(name, element)

    def in_filter(self, sources):
        if 'Mark of' in self.name or '(' in self.name:
            return False
        if self.name == 'Custom Lineage':
            return False
        return super().in_filter(sources)
    
    def get(self):
        name = self.element.find('name')
        if ', ' in name.text:
            s1, s2 = name.text.split(', ')
            name.text = f'{s1} ({s2})'
        if ' [5.5e]' in name.text:
            name.text = name.text.replace(' [5.5e]', '')
        else:
            name.text = name.text+ ' [5e]'
        return self.element
            
class RaceCollection(Collection):
    def __init__(self):
        super().__init__(Race)