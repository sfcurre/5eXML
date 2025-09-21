from .base import Collection, Element

class Background(Element):
    def __init__(self, name, element):
        super().__init__(name, element)

class BackgroundCollection(Collection):
    def __init__(self):
        super().__init__(Background)

    def add_element(self, element):
        name = element.find('name')
        name.text = name.text.split('(')[0].strip()
        if name.text not in self.elements:
            self.elements[name.text] = self.element_class(name.text, element)
