"""Create compendiums by combining the XML
Run this file from the root directory (the place where this file resides)
    $ python create_compendiums.py
This will update the XML files in the Compendiums directory.
"""
import lxml.etree as et
from glob import glob
from collections import defaultdict
import os

from Utils.merger import Merger
from Utils.corrector import Corrector

COMPENDIUM = 'Compendiums/{category} Compendium.xml'

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

        merger = Merger(elements, Corrector())
        clean_elements = merger.merge()
        print('\n\t\tRemoved %d duplicate(s)' % (len(elements) - len(clean_elements)))

        root = et.Element('compendium')
        root[:] = sorted(clean_elements, key = lambda x: (x.tag, x.findtext('name')))
        root.set('version', '5')
        root.set('auto_indent', 'NO')

        with open(output, 'wb') as fp:
            fp.write(et.tostring(root, pretty_print=True, xml_declaration=True, encoding='utf-8'))
        return

class XSLTCombiner:

    """Combiner for xml files with multiple way to perform the combining"""

    def __init__(self, transform):
        self.transform = transform

    def combine(self, collection, output):
        """Combine the xml files and sort the items alphabetically
        Items with the same name are removed.
        :param output: filepath in with the result will be stored.
        """
        with open(output, 'wb') as fp:
            outxml = self.transform(collection)
            outstring = et.tostring(outxml, pretty_print=True, xml_declaration=True, encoding='utf-8')
            fp.write(outstring)
        return

    @staticmethod
    def create_collection(filelist):
        """Create the category compendiums
        :return: list of output paths.
        """
        root = et.Element('collection')
        for fname in filelist:
            et.SubElement(root, 'doc', href=(fname).replace('\\', '/'))
        return root

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