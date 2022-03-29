import lxml.etree as et
from collections import defaultdict
from glob import glob

#TODO:
#Correct spell slots for fighter, rogue <slots optional="YES">2, 2</slots> as necessary
#Correct optional ability modifiers for races

class Corrector:

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