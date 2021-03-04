"""Create compendiums by combining the XML
Run this file from the root directory (the place where this file resides)
    $ python create_compendiums.py
This will update the XML files in the Compendiums directory.
"""
import lxml.etree as et
from glob import glob
from collections import defaultdict
import os

COMPENDIUM = 'Compendiums/{category} Compendium.xml'

class Merger:
    def __init__(self, tagged_elements):
        self.tagged_elements = tagged_elements
        self.data = self.divide_elements()

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
                races.append(race)
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

class XMLCombiner:

    """Combiner for xml files with multiple way to perform the combining"""

    def __init__(self, filenames, abbrevs):
        assert len(filenames) > 0, 'No filenames!'
        self.filenames = filenames
        self.abbrevs = abbrevs
        self.trees = [self.informed_parse(f) for f in filenames]
        self.roots = [f.getroot() for f in self.trees]

    def informed_parse(self, filename):
        try:
            return et.parse(filename)
        except:
            print(filename)
            raise

    def combine(self, output):
        """Combine the xml files and sort the items alphabetically
        Items with the same name are removed.
        :param output: filepath in with the result will be stored.
        """
        elements = []
        for r, abv in zip(self.roots, self.abbrevs):
            for element in r:
                name = element.find('name')
                text = name.text.replace('\'s', '^')
                text = text.title()
                text = text.replace('^', '\'s')
                name.text = text
                elements.append((element, abv))

        merger = Merger(elements)
        clean_elements = merger.merge()
        print('\n\t\tRemoved %d duplicate(s)' % (len(elements) - len(clean_elements)))

        root = et.Element('compendium')
        root[:] = sorted(clean_elements, key = lambda x: (x.tag, x.findtext('name')))
        root.set('version', '5')
        root.set('auto_indent', 'NO')

        with open(output, 'wb') as fp:
            fp.write(et.tostring(root, pretty_print=True, xml_declaration=True, encoding='utf-8'))
        return

def create_file_lists(categories):
    """Create the category compendiums
    :return: list of output paths.
    """
    paths = []
    abvs = []
    for category, abv in categories:
        print('\t' + category + ' (' + abv + ')')
        if os.path.isdir(category):
            filenames = glob(f'{category}\\*.xml')
            paths.extend(filenames)
            abvs.extend([abv] * len(filenames))
        else: #path is a file
            paths.append(category)
            abvs.append(abv)
    return paths, abvs

def create_compendium():
    """Create the category compendiums and combine them into full compendium"""

    categories = {'Sean' : [('Core\\DungeonMastersGuide', 'DMG'),
                            ('Core\\MonsterManual', ''),
                            ('Core\\PlayersHandbook', ''),
                            ('Addons\\MordenkainensTomeOfFoes', 'MToF'),
                            ('Addons\\PlaneShift', 'PS'),
                            ('Addons\\PrincesOfTheApocalypse\\races-eepc.xml', 'PotA'),
                            ('Addons\\SwordCoastAdventurersGuide', 'SCAG'),
                            ('Addons\\TashasCauldronOfEverything', 'TCoE'),
                            ('Addons\\ThirdParty\\TomeOfBeasts.xml', 'ToB'),
                            ('Addons\\UnearthedArcana\\races-ua-racesofeberron.xml', 'UA'),
                            ('Addons\\UnearthedArcana\\races-ua-racesofravnica.xml', 'UA'),
                            ('Addons\\UnearthedArcana\\class-paladin-ua-paladin.xml', 'UA'),
                            ('Addons\\UnearthedArcana\\class-sorcerer-ua-sorcerer.xml', 'UA'),
                            ('Addons\\UnearthedArcana\\class-warlock-ua-warlockandwizard.xml', 'UA'),
                            ('Addons\\UnearthedArcana\\class-wizard-ua-clericdruidwizard.xml', 'UA'),
                            ('Addons\\UnearthedArcana\\spells-ua-frw.xml', 'UA'),
                            ('Addons\\VolosGuideToMonsters', 'VGtM'),
                            ('Addons\\XanatharsGuideToEverything', 'XGtE'),
                            ('Homebrew\\CurrentAdditions', 'CA')],
                  'Core' : [('Core\\DungeonMastersGuide', 'DMG'),
                            ('Core\\MonsterManual', ''),
                            ('Core\\PlayersHandbook', '')]}
    
    for category, xlist in categories.items():
        print(category)
        fnames, abvs = create_file_lists(xlist)
        full_path = COMPENDIUM.format(category=category)
        XMLCombiner(fnames, abvs).combine(full_path)


if __name__ == '__main__':
    create_compendium()