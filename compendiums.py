"""Create compendiums by combining the XML
Run this file from the root directory (the place where this file resides)
    $ python create_compendiums.py
This will update the XML files in the Compendiums directory.
"""
import lxml.etree as et
from glob import glob
import os

from source.organizer import Organizer
from source.source_map import Sources

COMPENDIUM = 'Compendiums/{category} Compendium.xml'

class XMLCombiner:

    """Combiner for xml files with multiple way to perform the combining"""

    def __init__(self, filenames):
        assert len(filenames) > 0, 'No filenames!'
        self.filenames = filenames
        self.trees = [self.informed_parse(f) for f in filenames]
        self.roots = [f.getroot() for f in self.trees]

    def informed_parse(self, filename):
        try:
            return et.parse(filename)
        except:
            print(filename)
            raise

    def combine(self, output, sources):
        """Combine the xml files and sort the items alphabetically
        Items with the same name are removed.
        :param output: filepath in with the result will be stored.
        """
        elements = []
        for r in self.roots:
            for element in r:
                # name = element.find('name')
                # text = name.text.replace('\'s', '^')
                # text = text.title()
                # text = text.replace('^', '\'s')
                # name.text = text
                elements.append(element)
        
        organizer = Organizer(elements)
        clean_elements = organizer.organize(sources)
        print('\n\t\tRemoved %d elements(s)' % (len(elements) - len(clean_elements)))
        # print(sources.count_sources(clean_elements))

        root = et.Element('compendium')
        root[:] = sorted(clean_elements, key = lambda x: (x.tag, x.findtext('name')))
        root.set('version', '5')
        root.set('auto_indent', 'NO')

        with open(output, 'wb') as fp:
            fp.write(et.tostring(root, pretty_print=True, xml_declaration=True, encoding='utf-8'))
        return

def create_file_lists(xlist):
    paths = []
    for path in xlist:
        print('\t' + path)
        if os.path.isdir(path):
            filenames = glob(f'{path}\\*.xml')
            paths.extend(filenames)
        else: #path is a file
            paths.append(path)
    return paths

def create_compendium():
    
    categories = {'Renewed': ['Compendiums/WotC_5.5e+Legacy_5e_WotC_SemiOfficial.xml']
                }
    
    for category, xlist in categories.items():
        print(category)
        fnames = create_file_lists(xlist)
        full_path = COMPENDIUM.format(category=category)
        XMLCombiner(fnames).combine(full_path, Sources)

if __name__ == '__main__':
    create_compendium()