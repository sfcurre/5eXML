class Element:
    def __init__(self, name, element):
        self.name = name
        self.element = element

    def get(self):
        return self.element

    def in_filter(self, sources):
        return self.element in sources

class Collection:
    def __init__(self, element_class):
        self.element_class = element_class
        self.elements = {}
    
    def add_element(self, element):
        name = element.findtext('name')
        if name not in self.elements:
            self.elements[name] = self.element_class(name, element)
        
    def filter_elements(self, sources):
        elements = list(self.elements.items())
        for element_name, element in elements:
            if not element.in_filter(sources):
                self.elements.pop(element_name)
    
    def get_elements(self):
        elements = []
        for element in sorted(self.elements):
            elements.append(self.elements[element].get())
        return elements