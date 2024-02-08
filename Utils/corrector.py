import lxml.etree as et
from collections import defaultdict
from glob import glob

#TODO:
#Correct spell slots for fighter, rogue <slots optional="YES">2, 2</slots> as necessary
#Correct optional ability modifiers for races

class Corrector:

    def correct_division(self, element, data):
        pass

    def correct_classes(self, clas):
        corrections = et.parse("Corrections/class-slots.xml")
        artificer_corrections = et.parse("Corrections\class-artificer-tce-only.xml")
        name = clas.findtext('name')
        for correct in corrections.getroot():
            if name == correct.findtext('name'):
                clas.extend(correct[:])

        if name == artificer_corrections.getroot()[0].findtext('name'):
            clas[:] = artificer_corrections.getroot()[0][:]

    def correct_races(self, races):
        corrections = et.parse("Corrections/races-ability-scores.xml")
        for race in races:
            for correct in corrections.getroot():
                if race.findtext('name') == correct.findtext('name'):
                    race.insert(7, correct.find('trait'))

class ArchivistCorrector:

    def correct_division(self, element, data, abv):
        if element.tag == 'class':
            name = element.findtext('name').split('(')[0].strip()
            if 'sidekick' in name.lower():
                return True

            roots = {}
            for feature in element:
                feat = feature.find('feature')
                if feat is not None:
                    n = feat.findtext('name')
                    if n.startswith('Additional') and n.endswith('Spells'):
                        feature.getparent().remove(feature)
                        continue

                if (feat is not None and feat.get('optional') == 'YES'):
                    if any(n.startswith(p) for p in ['Starting', 'Multiclass', 'Fighting Style', 'Metamagic', 'Pact Boon']):
                        continue
                    if ('replaces' in n):
                        continue
                    
                    #doesn't work if proficiency is added as part of feature

                    if feat.findall('text')[-1].text is None:
                        continue

                    if feat.findall('text')[-1].text.startswith('Source'):
                        source = feat.findall('text')[-1].text
                        
                        if 'Dungeon' in source:
                            modname = 'DMG'
                        elif 'Sword Coast' in source:
                            modname = 'SCAG'
                        elif 'Wildemount' in source:
                            modname = 'EGtW'
                        elif 'Xanathar' in source:
                            modname = 'XGtE'
                        elif 'Tasha' in source and name != 'Artificer':
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
                        else:
                            modname = ''

                        if modname:
                            if (name, modname) not in roots:
                                roots[(name, modname)] = et.Element('class')
                                name_element = et.Element('name')
                                name_element.text = name
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

    def correct_classes(self, clas):
        name = clas.findtext('name')
        if name == 'Wizard':
            for element in clas:
                feat = element.find('feature')
                if (feat is not None and feat.findtext('name') in ['Signature Spell', 'Spell Mastery']):
                    feat.attrib.pop('optional')

    def correct_races(self, races):
        for race in races:
            name = race.find('name')
            n = name.text.split(', ')
            if len(n) == 2:
                name.text = f'{n[0]} ({n[1]})'

    def filter_merge(self, clean_elements):
        fb = lambda s: 'Ravnica' in s or 'Baldur' in s
        ff = lambda c: c.tag == 'feat' and ':' in c.findtext('name')
        fs = lambda c: 'Strixhaven' in str(et.tostring(c)) or 'Acquisitions' in str(et.tostring(c))
        fss = lambda c: 'Spelljammer' in str(et.tostring(c))
        fsp = lambda c: c.tag == 'spell' and 'Ravnica' in str(et.tostring(c))
        fr = lambda c: c.tag == 'race' and 'Mark Of' in c.findtext('name')
        fdg = lambda c: c.tag == 'feat' and ('Dragonlance: Shadow' in str(et.tostring(c)) or 'Bigby Presents:' in str(et.tostring(c))) 
        filter_ = lambda c: not(fs(c) or fss(c) or fsp(c) or ff(c) or fr(c) or fdg(c) or 
                                (c.tag == 'background' and fb(str(et.tostring(c)))))
        return list(filter(filter_, clean_elements))
