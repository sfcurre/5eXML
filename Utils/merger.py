import lxml.etree as et
from collections import defaultdict

class Merger:
    def __init__(self, tagged_elements, corrector):
        self.tagged_elements = tagged_elements
        self.corrector = corrector
        self.data = self.divide_elements()

    def divide_elements(self):
        data = defaultdict(list)
        for element, abv in self.tagged_elements:
            element.getparent().remove(element)
            # print(et.tostring(element, encoding='utf-8'))
            # input()
            if not self.corrector.correct_division(element, data, abv):
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
                self.corrector.correct_classes(clas)

                if name not in core_classes:
                    core_classes[name] = clas

            else:
                add_core_to[name].append((clas, abv))
        add_features = defaultdict(list)

        for classname, clas in core_classes.items():
            for element in clas:
                feat = element.find('feature')
                if element.tag == 'name':
                    continue
                if (feat is not None and feat.get('optional') == 'YES'):
                    n = feat.findtext('name')
                    if not any(n.startswith(p) for p in ['Starting', 'Multiclass', 'Fighting Style', 'Metamagic', 'Pact Boon']):
                        continue                        
                add_features[classname].append(element)
                #add_features[classname].append(et.tostring(element, encoding='utf-8'))

        classes = list(core_classes.values())
        for classname, clist in add_core_to.items():
            for clas, abv in clist:
                name = clas.find('name')
                name.text = name.text.split('(')[0].strip()
                name.text += f' ({abv})' * bool(abv)
                additions = []
                for element in add_features[classname]:
                    try:
                        #additions.append(et.XML(element))
                        additions.append(element)
                    except:
                        print(element)
                        raise
                clas[:] = additions + clas[:]
                classes.append(clas)
        return classes

    def merge_feats(self):
        feats = []
        names = set()
        for feat, abv in self.data['feat']:
            name = feat.find('name')
            if name.text not in names:
                names.add(name.text)
                feats.append(feat)
        return feats

    def merge_items(self):
        items = []
        names = set()
        for item, abv in self.data['item']:
            name = item.find('name')
            # name.text = name.text.split('(')[0].strip()
            if name.text not in names:
                names.add(name.text)
                items.append(item)
        return items

    def merge_monsters(self):
        monsters = []
        names = set()
        for monster, abv in self.data['monster']:
            name = monster.find('name')
            # name.text = name.text.split('(')[0].strip()
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
        self.corrector.correct_races(races)
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
        self.backgrounds = self.corrector.filter_merge(self.merge_backgrounds())
        self.classes = self.corrector.filter_merge(self.merge_classes())
        self.feats = self.corrector.filter_merge(self.merge_feats())
        self.items = self.corrector.filter_merge(self.merge_items())
        self.monsters = self.corrector.filter_merge(self.merge_monsters())
        self.races = self.corrector.filter_merge(self.merge_races())
        self.spells = self.corrector.filter_merge(self.merge_spells())
        return [*self.backgrounds,
                *self.classes,
                *self.feats,
                *self.items,
                *self.monsters,
                *self.races,
                *self.spells]

    def split(self, filebase):
        todo = {'Backgrounds': self.backgrounds,
                'Classes': self.classes,
                'Feats': self.feats,
                'Items': self.items,
                'Monsters': self.monsters,
                'Races': self.races,
                'Spells': self.spells}
        
        for label, category in todo.items():
            root = et.Element('compendium')
            root[:] = sorted(category, key = lambda x: (x.tag, x.findtext('name')))
            root.set('version', '5')
            root.set('auto_indent', 'NO')

            with open(f'{filebase}{label}.xml', 'wb') as fp:
                fp.write(et.tostring(root, pretty_print=True, xml_declaration=True, encoding='utf-8'))