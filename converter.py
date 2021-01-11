# ############################################################################
# Repertory converter / parser / importer for OOREP (https://www.oorep.com/)
# Copyright (c) 2021  Andreas Bauer <a@pspace.org>
# License: GPL v3.0 (or higher)

import parser
import psycopg2

# Types ######################################################################

class TableRowRemedy:
    def __init__(self, abbrev: str, _id: int, nameabbrev: str):
        self.abbrev = abbrev
        self._id = _id
        self.nameabbrev = nameabbrev
    # This one needs a live DB cursor, so we can lookup a remedy's longname in the DB, if there is one
    def getSqlInsertStatement(self, cursor: psycopg2._psycopg.cursor):
        cursor.execute("select namelong from remedy where nameabbrev='" + self.nameabbrev + "';")
        longNames = list(set(cursor.fetchall()))
        if len(longNames) == 1:
            return ("insert into remedy(abbrev, id, nameabbrev, namelong) values('" +
                    self.abbrev + "', " + str(self._id) + ", '" + self.nameabbrev + "', '" + longNames[0][0] + "');")
        elif len(longNames) > 1:
            print("Long remedy names should be unique in the database! Found:")
            print(longNames)
            print("for " + self.nameabbrev + ".")
            exit(1)
        else:
            return ("insert into remedy(abbrev, id, nameabbrev, namelong) values('" +
                    self.abbrev + "', " + str(self._id) + ", '" + self.nameabbrev + "', '');")

class TableRowRubric:
    def __init__(self, abbrev: str, _id: int, mother: int, chapterid: int, fullpath: str, path: str):
        self.abbrev = abbrev
        self._id = _id
        self.mother = mother
        self.chapterid = chapterid
        self.fullpath = fullpath
        self.path = path
    # This one needs ALL rubrics, in order to find out, if a rubric is a "mother-rubric"
    def getSqlInsertStatement(self, rubrics: list[parser.Rubric]):
        isMother = 't' if len(list(filter((lambda rubric: int(rubric.parentIndex) == int(self._id)), rubrics))) > 0 else 'f'
        return("insert into rubric(abbrev, id, mother, ismother, chapterid, fullpath, path) values('" +
               self.abbrev + "', " +
               str(self._id) + ", " +
               str(self.mother) + ", '" +
               isMother + "', " +
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

    for rubricid in range(0, len(allParsedRubricsFromFile)):
        for remedy in allParsedRubricsFromFile[rubricid].remedies:
            tableRows.append(TableRowRubricRemedy(
                tableRubric[0].abbrev,
                rubricid,
                list(filter((lambda trem: True if trem.nameabbrev == remedy.abbrev else False), tableRemedy))[0]._id,
                remedy.weight,
                tableRubric[rubricid - 1].chapterid
            ))

    return tableRows
