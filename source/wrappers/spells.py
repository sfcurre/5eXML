from .base import Collection, Element

class Spell:
    def __init__(self, name):
        self.name = name
        self.base_spell = None
        self.classes = set()

    def set_base_spell(self, base):
        self.base_spell = base

    def update_classes(self, classes):
        self.classes.update(classes)

    def in_filter(self, sources):
        if self.base_spell is None:
            return False
        return True

    def get(self):
        self.base_spell.find('classes').text = ', '.join(sorted(self.classes))
        return self.base_spell

class SpellCollection(Collection):
    def __init__(self):
        super().__init__(Spell)

    def add_element(self, element):
        name = element.findtext('name')
        if name not in self.elements:
            self.elements[name] = Spell(name)

        if element.find('level') is not None:
            self.elements[name].set_base_spell(element)

        self.elements[name].update_classes(element.findtext('classes').split(', '))
        