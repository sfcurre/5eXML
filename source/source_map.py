import lxml.etree as et
from collections import defaultdict
import re

### VALUE SUGGESTIONS ###
# 8-10 - Core Books
# 5-7  - Official Addons
# 3-4  - Campaigns
# 1-2  - Homebrew Content
# 0    - Everything Else

SOURCE_ABBREVS = {
    'DMG': (r"Dungeon Master's Guide", 8),
    'SCAG': (r"Sword Coast Adventurer's Guide", 4),
    'EGtW': (r"Explorer's Guide to Wildemount", 4),
    'MToF': (r"Mordenkainen's Tome of Foes", 5),
    'ERLW': (r"Eberron: Rising from the Last War", 4),
    'XGtE': (r"Xanathar's Guide to Everything", 6),
    'TCoE': (r"Tasha's Cauldron of Everything", 6),
    'VRGtR': (r"Van Richten's Guide to Ravenloft", 4),
    'FToD': (r"Fizban's Treasury of Dragons", 4),
    'CR': (r"Tal'Dorei Campaign Setting", 3),
    'SotDQ': (r"Dragonlance: Shadow of the Dragon Queen", 4),
    'GotG': (r"Bigby Presents: Glory of the Giants", 4),
    'MoM': (r"Mordenkainen Presents: Monsters of the Multiverse", 6),
    'VGM': (r"Volo's Guide to Monsters", 5),
    '2014': (r"Player's Handbook \(2014\)", 7),
    '': (r"Player's Handbook \(2024\)", 10),
    'MM': (r"Monster Manual", 9),
}

class SourceMap:
    def __init__(self):
        self.source_map = defaultdict(dict)

    def __contains__(self, element):
        allowed = False 
        for abrv in self.source_map:
            if self.search(element, abrv):
                allowed = True
                break
        return allowed
    
    def load(self, mapping):
        for abrv, source in mapping.items():
            if type(source) is tuple:
                source, value = source
            else:
                value = 0
            self.source_map[abrv]['source'] = source
            self.source_map[abrv]['value'] = value

    def search(self, element, abrv):
        content = str(et.tostring(element, encoding='unicode'))
        source = self.source_map[abrv]['source']
        source = self.wrap_source(source)
        r = re.compile(source)
        if r.search(content) is not None:
            return True
        
    def findall(self, element, abrv):
        content = str(et.tostring(element, encoding='unicode'))
        source = self.source_map[abrv]['source']
        source = self.wrap_source(source)
        r = re.compile(source)
        return len(r.findall(content))

    def wrap_source(self, source):
        # look behind
        behind = r'Source:\t([^<>]|\n)*'
        # look forward
        forward = r'([^<>]|\n)*</'
        return behind + source + forward

    def get_value(self, abrv):
        if abrv not in self.source_map:
            return 0
        return self.source_map[abrv]['value']

    def match(self, element):
        for abrv in sorted(self.source_map, key=self.get_value, reverse=True):
            if self.search(element, abrv):
                return abrv
        return 'Unknown'
    
    def get_source_value(self, element):
        abrv = self.match(element)
        return self.get_value(abrv)
        
    def count_sources(self, elements):
        counts = defaultdict(int)
        for element in elements:
            for abrv in self.source_map:
                counts[abrv] += self.findall(element, abrv)
        return counts
        
Sources = SourceMap()
Sources.load(SOURCE_ABBREVS)