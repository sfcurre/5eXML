import lxml.etree as et
from collections import defaultdict
import copy

from .wrappers import *

class Organizer:
    def __init__(self, elements=None):
        self.collections = {
            'background': BackgroundCollection(),
            'class': ClassCollection(),
            'feat': FeatCollection(),
            'item': ItemCollection(),
            'monster': MonsterCollection(),
            'race': RaceCollection(),
            'spell': SpellCollection()
        }
        if elements:
            self.add_elements(elements)

    def add_elements(self, elements):
        for element in elements:
            element.getparent().remove(element)

            if element.tag in self.collections:
                self.collections[element.tag].add_element(element)
            else:
                print(f'Missing "{element.tag}" tag for element')

    def filter_elements(self, sources):
        for collection in self.collections.values():
            collection.filter_elements(sources)

    def gather_elements(self):
        elements = []
        for collection in self.collections.values():
            elements.extend(collection.get_elements())
        return elements
    
    def organize(self, sources):
        self.filter_elements(sources)
        return self.gather_elements()
