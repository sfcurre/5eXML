from .base import Collection

from ..source_map import Sources

class Spell:
    def __init__(self, name):
        self.name = name
        self.base_spell = None
        self.classes = set()

    def set_base_spell(self, base):
        self.base_spell = base

    def update_classes(self, classes):
        for clas in sorted(classes):
            if ' [5.5e]' in clas:
                clas = clas.replace(' [5.5e]', '')
            if ' (Legacy)' in clas:
                clas = clas.replace(' (Legacy)', '')
            if ' Domain' in clas:
                clas = clas.replace(' Domain', '')
            if 'Gloomstalker' in clas:
                clas = clas.replace('Gloomstalker', 'Gloom Stalker')
            self.classes.add(clas)

    def in_filter(self, sources):
        if self.base_spell is None:
            return False
        if self.base_spell not in sources:
            if not Sources.check_source_string(self.base_spell, r'Strixhaven: A Curriculum of Chaos'):
                return False
        return True
    
    def filter_classes(self, subclass_names):
        for clas in list(self.classes):
            if 'School:' in clas or clas == 'Touch Spells':
                self.classes.remove(clas)
            elif '(UA)' in clas:
                self.classes.remove(clas)
            elif '(HB)' in clas or '(Heliana)' in clas:
                self.classes.remove(clas)
            elif 'Mark of' in clas:
                self.classes.remove(clas)
            elif not self.check_against_subclasses(clas, subclass_names):
                self.classes.remove(clas)

    def check_against_subclasses(self, clas, subclass_names):
        start_index = clas.find('(')
        if start_index == -1:
            return True
        
        clas_ = clas[:clas.find(' ')].strip()
        if clas_ not in subclass_names:
            return True
        
        end_index = clas.find(')')
        subclas = clas[start_index+1:end_index]
        for subclass_title in subclass_names[clas_]:
            if subclas in subclass_title:
                return True
        return False
        
    def get(self):
        name = self.base_spell.find('name')
        if ' [5.5e]' in name.text:
            name.text = name.text.replace(' [5.5e]', '')
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

        if element in Sources:
            self.elements[name].update_classes(element.findtext('classes').split(', '))

    def filter_classes(self, subclass_names):
        for spell in self.elements.values():
            spell.filter_classes(subclass_names)
        