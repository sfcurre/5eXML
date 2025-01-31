import lxml.etree as et

CORE_CLASS_FEATURES = ['Becoming', 'Divine Order', 'Blessed Strikes', 'Primal Order', 'Elemental Fury', 'Fighting Style:']

class ArchivistCorrector:

    def correct_division(self, element, data, abv):
        if element.tag == 'class':
            name = element.findtext('name')
            if 'Artificer' in name and not '[2024]' in name:
                return True

            if 'sidekick' in name.lower():
                return True

            roots = {}
            for feature in element:
                feat = feature.find('feature')
                if feat is not None:
                    n = feat.findtext('name')

                    if feat.get('optional') == 'YES':
                        if any(p in n for p in CORE_CLASS_FEATURES):
                            continue
                    
                    #doesn't work if proficiency is added as part of feature
                    if feat.findall('text')[-1].text is None:
                        continue

                    if 'Source:' in feat.findall('text')[-1].text:
                        source = feat.findall('text')[-1].text
                        source = source[source.find('Source:'):]
                        
                        if 'Dungeon' in source:
                            modname = 'DMG'
                        elif 'Sword Coast' in source:
                            modname = 'SCAG'
                        elif 'Wildemount' in source:
                            modname = 'EGtW'
                        elif 'Xanathar' in source:
                            modname = 'XGtE'
                        elif 'Tasha' in source:
                            modname = 'TCoE'
                        elif 'Ravenloft' in source:
                            modname = 'VRGtR'
                        elif 'Fizban' in source:
                            modname = 'FToD'
                        elif 'Tal\'Dorei' in source or 'Mercer' in source:
                            modname = 'CR'
                        elif 'Shadow' in source:
                            modname = 'SotDQ'
                        elif 'Bigby' in source:
                            modname = 'GotG'
                        elif 'Player\'s Handbook p.' in source:
                            modname = '2014'
                        else:
                            modname = ''

                        if modname:
                            if (name, modname) not in roots:
                                roots[(name, modname)] = et.Element('class')
                                name_element = et.Element('name')
                                name_element.text = name.replace(' [2024]', '')
                                roots[(name, modname)].append(name_element)
                            feature.getparent().remove(feature)
                            roots[(name, modname)].append(feature)

                counters = feature.findall('counter')
                if counters:
                    for counter in counters:
                        counter.getparent().remove(counter)

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
        fb = lambda s: 'Ravnica' in s or 'Baldur' in s
        ff = lambda c: c.tag == 'feat' and ':' in c.findtext('name') and not c.findtext('name').startswith('Origin')
        fs = lambda c: ('Strixhaven' in str(et.tostring(c)) and c.tag != 'spell') or 'Acquisitions' in str(et.tostring(c))
        fss = lambda c: 'Spelljammer' in str(et.tostring(c))
        fsp = lambda c: c.tag == 'spell' and 'Ravnica' in str(et.tostring(c))
        fr = lambda c: c.tag == 'race' and 'Mark Of' in c.findtext('name')
        fdg = lambda c: c.tag == 'feat' and ('Dragonlance: Shadow' in str(et.tostring(c)))# or 'Bigby Presents:' in str(et.tostring(c))) 
        filter_ = lambda c: not(fs(c) or fss(c) or fsp(c) or ff(c) or fr(c) or fdg(c) or 
                                (c.tag == 'background' and fb(str(et.tostring(c)))))
        return list(filter(filter_, clean_elements))
