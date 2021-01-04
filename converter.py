# ############################################################################
# Repertory converter / parser / importer for OOREP (https://www.oorep.com/)
# Copyright (c) 2021  Andreas Bauer <a@pspace.org>
# License: GPL v3.0 (or higher)

import parser

# Types ######################################################################

class TableRowRemedy:
    def __init__(self, abbrev: str, ID: int, nameabbrev: str):
        self.abbrev = abbrev
        self.ID = ID
        self.nameabbrev = nameabbrev
    def getSqlInsertStatement(self):
        return ("insert into remedy(abbrev, id, nameabbrev) values('" +
                self.abbrev + "', " + str(self.ID) + ", '" + self.nameabbrev + "');")

class TableRowRubric:
    def __init__(self, abbrev: str, ID: int, mother: int, chapterid: int, fullpath: str, path: str):
        self.abbrev = abbrev
        self.ID = ID
        self.mother = mother
        self.chapterid = chapterid
        self.fullpath = fullpath
        self.path = path
    def getSqlInsertStatement(self):
        return("insert into rubric(abbrev, id, mother, chapterid, fullpath, path) values('" +
               self.abbrev + "', " +
               str(self.ID) + ", " +
               str(self.mother) + ", " +
               str(self.chapterid) + ", '" +
               self.fullpath + "', '" +
               self.path + "');")

class TableRowRubricRemedy:
    def __init__(self, abbrev: str, rubricid: int, remedyid: int, weight: int, chapterid: int):
        self.abbrev = abbrev
        self.rubricid = rubricid
        self.remedyid = remedyid
        self.weight = weight
        self.chapterid = chapterid
    def getSqlInsertStatement(self):
        return ("insert into rubricremedy(abbrev, rubricid, remedyid, weight, chapterid) values('" +
                self.abbrev + "', " +
                str(self.rubricid) + ", " +
                str(self.remedyid) + ", " +
                str(self.weight) + ", " +
                str(self.chapterid) + ");")

# The actual converter functions #############################################

# Returns a list of type TableRowRemedy (meant to correspond to the DB table 'remedy')

def getCompleteRemedyTable(rubrics: list[parser.Rubric], repertoryAbbrev: str):
    def extractAllRemedyAbbrevsFromRubrics(rubrics: list[parser.Rubric]):
        allAbbrevs = set()
        for rubric in rubrics:
            allAbbrevs.update(list(map((lambda remedy: remedy.abbrev), rubric.remedies)))
        return sorted(allAbbrevs)

    tableRows = []
    allRemedyAbbrevs = extractAllRemedyAbbrevsFromRubrics(rubrics)

    for i in range(0, len(allRemedyAbbrevs)):
        tableRows.append(TableRowRemedy(repertoryAbbrev, i, allRemedyAbbrevs[i]))

    return tableRows

# Returns a list of type TableRowRubric (meant to correspond to the DB table 'rubric')

def getCompleteRubricTable(rubrics: list[parser.Rubric], repertoryAbbrev: str):
    tableRows = []
    chapterCounter = 0

    for rubric in rubrics:
        if rubric.parentIndex < 0:
            chapterCounter = chapterCounter + 1

        tableRows.append(TableRowRubric(
            repertoryAbbrev,
            str(rubric.index),
            str(rubric.parentIndex),
            str(chapterCounter),
            ', '.join(rubric.getFullPath(rubrics)),
            rubric.text
        ))

    return tableRows

# Returns a list of type TableRowRubricRemedy (meant to correspond to the DB table 'rubricremedy')

def getCompleteRubricRemedyTable(tableRemedy: list[TableRowRemedy],
                                 tableRubric: list[TableRowRubric],
                                 allParsedRubricsFromFile: list[parser.Rubric]):
    tableRows = []

    for rubric in allParsedRubricsFromFile:
        # TODO: I have no idea, why I need explicit conversion to int here. ID should be int by definition:
        rubricid = int(list(filter((lambda trub: True if trub.path == rubric.text else False), tableRubric))[0].ID)
        for remedy in rubric.remedies:
            tableRows.append(TableRowRubricRemedy(
                tableRubric[0].abbrev,
                rubricid,
                list(filter((lambda trem: True if trem.nameabbrev == remedy.abbrev else False), tableRemedy))[0].ID,
                remedy.weight,
                tableRubric[rubricid - 1].chapterid
            ))

    return tableRows
