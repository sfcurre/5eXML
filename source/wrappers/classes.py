import lxml.etree as et
from collections import defaultdict
import copy

from .base import Collection
from ..source_map import Sources

class Class:
    def __init__(self, name):
        self.name = name
        self.subclasses = defaultdict(list)
        self.base_class = et.Element('class')
        
    def set_base_content(self, base):
        self.base_class = et.Element('class')
        for element in base:
            feat = element.find('feature')
            if feat is None or not self.is_subclass_feature(feat):
                self.base_class.append(element)

    def add_subclass_content(self, subclass):
        for element in subclass:
            feat = element.find('feature')
            if feat is not None and self.is_subclass_feature(feat):
                modname = Sources.match(element)
                if modname is not None:
                    self.subclasses[modname].append(element)

    def is_subclass_feature(self, feat):
        if feat is not None and feat.get('optional') == 'YES':
            n = feat.findtext('name')
            if 'Subclass' in n or ('(' in n and ')' in n):
                return True
        return False
    
    def in_filter(self, sources):
        # check base class
        if self.base_class not in sources:
            return False
        
        # check subclasses
        subclasses = list(self.subclasses.items())
        for modname, features in subclasses:
            clean_features = []
            for feat in features:
                if feat in sources:
                    clean_features.append(feat)
            self.subclasses[modname] = clean_features
            if not clean_features:
                self.subclasses.pop(modname)

        if not self.subclasses:
            return False
        return True

    def get(self):
        elements = []
        for modname, features in self.subclasses.items():
            subclass = copy.deepcopy(self.base_class)
            name = subclass.find('name')
            if modname:
                name.text = f'{name.text} ({modname})'
            subclass.extend(features)
            elements.append(subclass)
        return elements
    
class ClassCollection(Collection):
    def __init__(self):
        super().__init__(Class)
        self.base_values = defaultdict(int)

    def add_element(self, element):
        name = element.find('name')
        class_name = name.text.split()[0]
        if class_name not in self.elements:
            self.elements[class_name] = Class(class_name)

        if (value := Sources.get_source_value(element)) > self.base_values[class_name]:
            name.text = class_name
            self.elements[class_name].set_base_content(element)
            self.base_values[class_name] = value
        self.elements[class_name].add_subclass_content(element)

    def get_elements(self):
        elements = []
        for element in sorted(self.elements):
            elements.extend(self.elements[element].get())
        return elements