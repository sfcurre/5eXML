import lxml.etree as et
from collections import defaultdict
from glob import glob

#TODO:
#Correct spell slots for fighter, rogue <slots optional="YES">2, 2</slots> as necessary
#Correct optional ability modifiers for races

class Corrector:

    def correct_element_division(self, element, data):
        pass

    def correct_core_class(self, clas):
        corrections = et.parse("Corrections/class-slots.xml")
        artificer_corrections = et.parse("Corrections\class-artificer-tce-only.xml")
        name = clas.findtext('name')
        for correct in corrections.getroot():
            if name == correct.findtext('name'):
                clas.extend(correct[:])

        if name == artificer_corrections.getroot()[0].findtext('name'):
            clas[:] = artificer_corrections.getroot()[0][:]

    def correct_race_abilities(self, races):
        corrections = et.parse("Corrections/races-ability-scores.xml")
        for race in races:
            for correct in corrections.getroot():
                if race.findtext('name') == correct.findtext('name'):
                    race.insert(7, correct.find('trait'))

class ArchivistCorrector:

    def correct_element_division(self, element, data, abv):
        if element.tag == 'class':
            name = element.findtext('name').split('(')[0].strip()
            if 'sidekick' in name.lower():
                return True
            if name == 'Artificer':
                data['class'].append((element, 'TCE'))
            
            roots = {}
            for feature in element:
                feat = feature.find('feature')
                if (feat is not None and feat.get('optional') == 'YES'):
                    n = feat.findtext('name')
                    if any(n.startswith(p) for p in ['Starting', 'Multiclass', 'Fighting', 'Meta', 'Pact']):
                        continue

                    if feat[-1].text.startswith('Source'):
                        source = feat[-1].text
                        
                        if 'Dungeon' in source:
                            modname = 'DMG'
                        elif 'Sword Coast' in source:
                            modname = 'SCAG'
                        elif 'Wildemount' in source:
                            modname = 'EGW'
                        elif 'Xanathar' in source:
                            modname = 'XGE'
                        elif 'Tasha' in source:
                            modname = 'TCE'
                        elif 'Ravenloft' in source:
                            modname = 'VRGR'
                        elif 'Fizban' in source:
                            modname = 'FTD'
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

            data['class'].append((element, abv))
            for name, mod in roots:
                data['class'].append((roots[name, mod], mod))

            return True
        return False

    def correct_core_class(self, clas):
        name = clas.findtext('name')
        if name == 'Wizard':
            for element in clas:
                feat = element.find('feature')
                if (feat is not None and feat.findtext('name') in ['Signature Spell', 'Spell Mastery']):
                    feat.attrib.pop('optional')

    def correct_race_abilities(self, races):
        pass