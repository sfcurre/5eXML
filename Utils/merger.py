import lxml.etree as et
from collections import defaultdict

class Merger:
    def __init__(self, tagged_elements, corrector):
        self.tagged_elements = tagged_elements
        self.data = self.divide_elements()
        self.corrector = corrector

    def divide_elements(self):
        data = defaultdict(list)
        for element, abv in self.tagged_elements:
            data[element.tag].append((element, abv))
        return data

    def merge_backgrounds(self):
        backgrounds = []
        names = set()
        for background, abv in self.data['background']:
            name = background.find('name')
            name.text = name.text.split('(')[0].strip()
            if name.text not in names:
                names.add(name.text)
                backgrounds.append(background)
        return backgrounds

    def merge_classes(self):
        core_classes = {}
        add_core_to = defaultdict(list)
        for clas, abv in self.data['class']:
            name = clas.findtext('name').split('(')[0].strip()
            if clas.find('hd') is not None: #base class
                
                self.corrector.correct_core_class(clas)

                if name not in core_classes:
                    core_classes[name] = clas
                else:
                    for element in clas:
                        feat = element.find('feature')
                        if (feat is not None and feat.get('optional') == 'YES'):
                            core_classes[name].append(feat)      
            else:
                add_core_to[name].append((clas, abv))
        add_features = defaultdict(list)

        for classname, clas in core_classes.items():
            for element in clas:
                feat = element.find('feature')
                if (feat is not None and feat.get('optional') == 'YES') or element.tag == 'name':
                    continue
                add_features[classname].append(et.tostring(element, encoding='utf-8'))

        classes = list(core_classes.values())
        for classname, clist in add_core_to.items():
            for clas, abv in clist:
                name = clas.find('name')
                name.text = name.text.split('(')[0].strip()
                name.text += f' ({abv})' * bool(abv)
                additions = []
                for element in add_features[classname]:
                    additions.append(et.XML(element))
                clas[:] = additions + clas[:]
                classes.append(clas)
        return classes

    def merge_feats(self):
        feats = []
        names = set()
        for feat, abv in self.data['feat']:
            name = feat.find('name')
            name.text = name.text.split('(')[0].strip()
            if name.text not in names:
                names.add(name.text)
                feats.append(feat)
        return feats

    def merge_items(self):
        items = []
        names = set()
        for item, abv in self.data['item']:
            name = item.find('name')
            name.text = name.text.split('(')[0].strip()
            if name.text not in names:
                names.add(name.text)
                items.append(item)
        return items

    def merge_monsters(self):
        monsters = []
        names = set()
        for monster, abv in self.data['monster']:
            name = monster.find('name')
            name.text = name.text.split('(')[0].strip()
            name.text += f' ({abv})' * bool(abv)
            if name.text not in names:
                names.add(name.text)
                monsters.append(monster)
        return monsters

    def merge_races(self):
        races = []
        blocks = set()
        for race, abv in self.data['race']:
            if abv == 'DMG':
                continue
            if (block := et.tostring(race)) not in blocks: 
                blocks.add(block)
                name = race.find('name')
                name.text = '(UA'.join(name.text.split('(Ua'))
                races.append(race)
        self.corrector.correct_race_abilities(races)
        return races

    def merge_spells(self):
        base_spells = defaultdict(list)
        spell_classes = defaultdict(set)
        for spell, abv in self.data['spell']:
            name = spell.findtext('name')
            if spell.find('level') is not None: #base class
                base_spells[name] = spell
            spell_classes[name].update(spell.findtext('classes').split(', '))
        
        spells = []
        for spellname, spell in sorted(base_spells.items()):
            spell.find('classes').text = ', '.join(sorted(spell_classes[spellname]))
            spells.append(spell)
        return spells


    def merge(self):
        backgrounds = self.merge_backgrounds()
        classes = self.merge_classes()
        feats = self.merge_feats()
        items = self.merge_items()
        monsters = self.merge_monsters()
        races = self.merge_races()
        spells = self.merge_spells()
        return [*backgrounds,
                *classes,
                *feats,
                *items,
                *monsters,
                *races,
                *spells]