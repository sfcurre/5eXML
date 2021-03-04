"""Create compendiums by combining the XML
Run this file from the root directory (the place where this file resides)
    $ python create_compendiums.py
This will update the XML files in the Compendiums directory.

Credit: https://github.com/ceryliae/DnDAppFiles
"""
import lxml.etree as et
from glob import glob
from collections import defaultdict
from tqdm import tqdm

COMPENDIUM = 'Compendiums/{category} Compendium.xml'

class LXMLCombiner(object):

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

def create_collection(categories):
    """Create the category compendiums
    :return: list of output paths.
    """
    root = et.Element('collection')
    for category in categories:
        print('\t' + category)
        filenames = glob(f'{category}\\*.xml')
        for fn in filenames:
            et.SubElement(root, 'doc', href=(fn).replace('\\', '/'))
    return root

def create_compendiums(xslt):
    """Create the category compendiums and combine them into full compendium"""

    xslt = et.parse(xslt)
    transform = et.XSLT(xslt)

    categories = {'Sean' : ['Core\\DungeonMastersGuide',
                            'Core\\MonsterManual',
                            'Core\\PlayersHandbook',
                            'Addons\\MordenkainensTomeOfFoes',
                            'Addons\\PlaneShift',
                            'Addons\\SwordCoastAdventurersGuide',
                            'Addons\\TashasCauldronOfEverything',
                            'DEPRECATED\\TomeOfBeasts',
                            'Addons\\UnearthedArcana\\UASubset',
                            'Addons\\VolosGuideToMonsters',
                            'Addons\\XanatharsGuideToEverything',
                            'Homebrew\\CurrentAdditions'],
                  'Core' : ['Core\\DungeonMastersGuide',
                            'Core\\MonsterManual',
                            'Core\\PlayersHandbook']}
    
    for category, xlist in categories.items():
        print(category)
        collection = create_collection(xlist)
        full_path = COMPENDIUM.format(category=category)
        LXMLCombiner(transform).combine(collection, full_path)

if __name__ == '__main__':
    create_compendiums('Utils\\merge.xslt')