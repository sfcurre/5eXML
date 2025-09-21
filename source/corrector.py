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

class Corrector:

    def correct_division(self, element, data, abv):
        if element.tag == 'class':
            name = element.findtext('name')
            
            if 'sidekick' in name.lower():
                return True

            roots = {}
            for feature in element:
                feat = feature.find('feature')
                if feat is not None:
                    n = feat.findtext('name')

                    if not ('Subclass' in n or ('(' in n and ')' in n)):
                        # base class content
                        continue
                    
                    #doesn't work if proficiency is added as part of feature
                    if feat.findall('text')[-1].text is None:
                        continue

                    if 'Source:' in feat.findall('text')[-1].text:
                        source = feat.findall('text')[-1].text
                        
                        modname = None
                        for abbr, full in SOURCE_ABBREVS.items():
                            if full in source:
                                modname = abbr
                                break
                        
                        if modname is not None:
                            if (name, modname) not in roots:
                                roots[(name, modname)] = et.Element('class')
                                name_element = et.Element('name')
                                name_element.text = name.replace(' [2024]', '')
                                roots[(name, modname)].append(name_element)
                            feature.getparent().remove(feature)
                            roots[(name, modname)].append(feature)

                # counters = feature.findall('counter')
                # if counters:
                #     for counter in counters:
                #         counter.getparent().remove(counter)

            data['class'].append((element, abv))
            for name, mod in roots:
                data['class'].append((roots[name, mod], mod))

            return True
        return False

    def correct_races(self, races):
        for race in races:
            name = race.find('name')
            n = name.text.split(', ')
            if len(n) == 2:
                name.text = f'{n[0]} ({n[1]})'

    def filter_merge(self, clean_elements):
        filtered = []
        for element in clean_elements:
            if self.filter_element(element):
                filtered.append(element)
        return filtered
    
    def filter_element(self, element):
        if element.tag == 'background':
            disallowed_sources = ['SotDQ']
            return self.source_filter(element, exclude=disallowed_sources)
        if element.tag == 'class':
            lambda_filter = lambda e: 'Illrigger' in e.findtext('name') or 'Tamer' in e.findtext('name')
            return self.source_filter(element)
        if element.tag == 'feat':
            disallowed_sources = ['SotDQ']
            return self.source_filter(element, exclude=disallowed_sources)
        if element.tag == 'item':
            return True
        if element.tag == 'monster':
            return True
        if element.tag == 'race':
            include_sources = ['Eberron', 'Ravnica']
            lambda_filter = lambda e: 'Mark Of' in e.findtext('name')
            return self.source_filter(element, lambda_filter=lambda_filter)
        if element.tag == 'spell':
            include_sources = ['Strixhaven']
            return self.source_filter(element, include=include_sources)
        
    def source_filter(self, element, exclude=[], include=[], lambda_filter=None, verbose=False):
        source = str(et.tostring(element))
        allowed = False 
        for abbr, full in SOURCE_ABBREVS.items():
            if full in source and abbr not in exclude:
                allowed = True
            if any(part in source for part in include):
                allowed = True
        if lambda_filter is not None and lambda_filter(element):
            allowed = False
        if not allowed and verbose:
            name = element.findtext('name')
            print(f'Excluding {element.tag}: {name}')
        return allowed
        