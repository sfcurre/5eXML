import lxml.etree as et 

SOURCE_ABBREVS = {
    'DMG': 'Dungeon Master',
    'SCAG': 'Sword Coast Adventurer',
    'EGtW': 'Guide to Wildemount',
    'MToF': 'Tome of Foes',
    'ERLW': 'Eberron: Rising from the Last War',
    'XGtE': 'Guide to Everything',
    'TCoE': 'Cauldron of Everything',
    'VRGtR': 'Guide to Ravenloft',
    'FToD': 'Treasury of Dragons',
    'CR': 'Dorei Campaign Setting',
    'SotDQ': 'Shadow of the Dragon Queen',
    'GotG': 'Bigby Presents: Glory of the Giants',
    'MoM': 'Monsters of the Multiverse',
    'VGM': 'Guide to Monsters',
    'UA': 'Unearthed Arcana',
    'Legacy': 'Handbook (2014)',
    '': 'Handbook (2024)',
}

class SourceMap:
    def __init__(self):
        self.source_to_abrv = {}
        self.abrv_to_source = {}

    def __contains__(self, element):
        content = str(et.tostring(element))
        allowed = False 
        for source in self.source_to_abrv:
            if source in content:
                allowed = True
        return allowed

    def set_pair(self, abrv, title):
        self.abrv_to_source[abrv] = title
        self.source_to_abrv[title] = abrv

    def load(self, mapping):
        for abrv, title in mapping.items():
            self.set_pair(abrv, title)

    def match_title(self, element):
        text = str(et.tostring(element))
        for title, abrv in self.source_to_abrv.items():
            if title in text:
                return abrv
        
    def get_source(self, abrv):
        return self.abrv_to_source.get(abrv, None)
    
    def get_abbr(self, title):
        return self.source_to_abrv.get(title, None)

Sources = SourceMap()
Sources.load(SOURCE_ABBREVS)