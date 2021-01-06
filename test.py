# ############################################################################
# Repertory converter / parser / importer for OOREP (https://www.oorep.com/)
# Copyright (c) 2021  Andreas Bauer <a@pspace.org>
# License: GPL v3.0 (or higher)

import parser
from parser import *
import converter
import unittest

glob_filename = 'SKRep3.txt'
glob_repertoryAbbrev = 'bogsk-de'

class SimpleParser(unittest.TestCase):
    def test(self):
        print("*** Remedy(ies)Parser: ")
        print(RemedyParser.remedy.parse('RUTA')) # This is 4-valued
        print(RemedyParser.remedy.parse('Ruta')) # This is 1-valued
        print(RemedyParser.remedy.parse('Ars.'))
        print(RemedyParser.remedy.parse('Ars-alb.'))
        print(RemedyParser.remedy.parse('Ars. (3)'))
        print(RemediesParser.remedies.parse('Ars.  (3)    Ruta Ars-i. (2) BRY.'))

        print("*** RubricTextParser: ")
        print(RubricTextParser.rubricText.parse('= Zeit'))
        print(RubricTextParser.rubricText.parse('== agg. (vgl. Dünnschiss)'))


        print("*** RubricParser: ")
        print(RubricParser.rubric.parse('= Zeit.'))
        print(RubricParser.rubric.parse('== agg. (vgl. Dünnschiss): Ars. Ruta Ars-i. (2)'))
        print(RubricParser.rubric.parse('==== agg. (vgl. Dünnschiss): Ars.  (3)  Ruta Ars-i. (2) Sulph.'))
        print(RubricParser.rubric.parse('=== agg.: Aran. Ars. (3) Cact. Cedr. Chin. (3)'))
        print(RubricParser.rubric.parse('== Atmen, tief, agg.: Acon. (2) Arn. Bor. (2) BRY. Calc. Caust. Kali-c. (2) Phos. (2) Ran-b. Rhus-t. Rumx. Sabin. Sang. Spig. Squil. Sulph.'))
        print(RubricParser.rubric.parse('=== amel.: Asaf. (2) Bism. (2) Calc. (2) Cycl. (2) Mur-ac. (2) Thuj. (2)'))
        print(RubricParser.rubric.parse('=== agg.: Acon. (2) Bell. Bry. (3) Cad-s. Cham. COCC. Ferr. Ign. Merc-i-f. (2) Nat-m. Nux-v. Op. Phos. Phyt. (2) Puls. Rhus-t. Sil. Sulph. Verat-v. Vib.'))
        print(RubricParser.rubric.parse('=== links, nach: Apis, BELL. Caust. LYC. MERC-I-F. Phos. Sabad. Sang. Sul-ac.'))

class CompleteParser(unittest.TestCase):
    tmpAllRubrics = []

    @classmethod
    def setUpClass(cls):
        cls.tmpAllRubrics = parser.getAllRubricsFromFile(glob_filename)

    def test_outputOfParsedFile(self):
        for rubric in self.tmpAllRubrics:
            print(str(rubric.index).zfill(4) + " [" + str(rubric.parentIndex).zfill(4) + "] ", end='')
            for i in range(1, rubric.depth):
                print("    ", end='')
            print(rubric)

    def test_getFullpathsOfParsedRubrics(self):
        for rubric in self.tmpAllRubrics:
            print(rubric.getFullPath(self.tmpAllRubrics))

class ConvertersRemedy(unittest.TestCase):
    repertoryAbbrev = glob_repertoryAbbrev
    filename = glob_filename
    allRubricsFromFile = []

    @classmethod
    def setUpClass(cls):
        cls.allRubricsFromFile = parser.getAllRubricsFromFile(cls.filename)

    def test_getTable(self):
        tableRemedy = converter.getCompleteRemedyTable(self.__class__.allRubricsFromFile, self.__class__.repertoryAbbrev)
        print("#tableRemedy: " + str(len(tableRemedy)))

class ConvertersRubric(unittest.TestCase):
    repertoryAbbrev = glob_repertoryAbbrev
    filename = glob_filename
    allRubricsFromFile = []
    tableRemedy: list[converter.TableRowRemedy] = []

    @classmethod
    def setUpClass(cls):
        cls.allRubricsFromFile = parser.getAllRubricsFromFile(cls.filename)
        cls.tableRemedy = converter.getCompleteRemedyTable(cls.allRubricsFromFile, cls.repertoryAbbrev)

    def test_getTable(self):
        tableRubric = converter.getCompleteRubricTable(self.__class__.allRubricsFromFile, self.__class__.repertoryAbbrev)
        print("#tableRubric: " + str(len(tableRubric)))

class ConvertersRubricRemedy(unittest.TestCase):
    repertoryAbbrev = glob_repertoryAbbrev
    filename = glob_filename
    allRubricsFromFile = []
    tableRemedy: list[converter.TableRowRemedy] = []
    tableRubric: list[converter.TableRowRubric] = []

    @classmethod
    def setUpClass(cls):
        cls.allRubricsFromFile = parser.getAllRubricsFromFile(cls.filename)
        cls.tableRemedy = converter.getCompleteRemedyTable(cls.allRubricsFromFile, cls.repertoryAbbrev)
        cls.tableRubric = converter.getCompleteRubricTable(cls.allRubricsFromFile, cls.repertoryAbbrev)

    def test_getTable(self):
        tableRubricRemedy = converter.getCompleteRubricRemedyTable(self.__class__.tableRemedy, self.__class__.tableRubric, self.__class__.allRubricsFromFile)
        print("#tableRubricRemedy: " + str(len(tableRubricRemedy)))

class Consistency(unittest.TestCase):
    repertoryAbbrev = glob_repertoryAbbrev
    filename = glob_filename
    allRubricsFromFile = []
    tableRemedy: list[converter.TableRowRemedy] = []
    tableRubric: list[converter.TableRowRubric] = []

    @classmethod
    def setUpClass(cls):
        cls.allRubricsFromFile = parser.getAllRubricsFromFile(cls.filename)
        cls.tableRemedy = converter.getCompleteRemedyTable(cls.allRubricsFromFile, cls.repertoryAbbrev)
        cls.tableRubric = converter.getCompleteRubricTable(cls.allRubricsFromFile, cls.repertoryAbbrev)

    def test_sameSizeAsRawData(self):
        self.assertTrue(len(self.tableRubric) == len(self.allRubricsFromFile))

    def test_samePathsAsRawData(self):
        for i in range(0, len(self.allRubricsFromFile)):
            self.assertTrue(self.allRubricsFromFile[i].text == self.tableRubric[i].path)

    def test_extractedRemediesSameAsInRawData(self):
        extractedRawRemedyAbbrevs = set()
        for rubric in self.allRubricsFromFile:
            extractedRawRemedyAbbrevs.update(map((lambda remedy: remedy.abbrev), rubric.remedies))

        tableRemedies = list(map((lambda r: r.nameabbrev), self.tableRemedy))
        for remedyAbbrev in extractedRawRemedyAbbrevs:
            self.assertTrue(remedyAbbrev in tableRemedies)