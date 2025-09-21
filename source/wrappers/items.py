from .base import Collection, Element

class Item(Element):
    def __init__(self, name, element):
        super().__init__(name, element)
    
class ItemCollection(Collection):
    def __init__(self):
        super().__init__(Item)