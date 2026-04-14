from .base import Collection, Element

class Background(Element):
    def __init__(self, name, element):
        super().__init__(name, element)

    def get(self):
        name = self.element.find('name')
        if ' [5.5e]' in name.text:
            name.text = name.text.replace(' [5.5e]', '')
        else:
            name.text = name.text+ ' [5e]'
        return self.element

class BackgroundCollection(Collection):
    def __init__(self):
        super().__init__(Background)

    def add_element(self, element):
        name = element.find('name')
        name.text = name.text.split('(')[0].strip()
        if name.text not in self.elements:
            self.elements[name.text] = self.element_class(name.text, element)
