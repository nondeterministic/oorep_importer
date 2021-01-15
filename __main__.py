# ############################################################################
# Repertory converter / parser / importer for OOREP (https://www.oorep.com/)
# Copyright (c) 2021  Andreas Bauer <a@pspace.org>
# License: GPL v3.0 (or higher)

import parser
import converter
import utility
import psycopg2
import os

# ###################################################################
# Showcase conversion pipeline from raw repertory to database inserts

filenames = ['oorep_importer/SKRep4.txt', 'oorep_importer/SRT3.txt']
repertoryAbbrev = "bogsk-de"

# First concatenate input files line by line into a single list of strings
completeInputFiles = []
for filename in filenames:
    with open(filename, encoding='utf-8-sig') as f:
        lines = [line.rstrip() for line in f]
        completeInputFiles.extend(lines)

# Then parse this complete input consisting of all files and get list of rubrics
allRubricsFromFile = []
for filename in filenames:
    allRubricsFromFile = parser.getAllRubricsFromFileContents(completeInputFiles)

# Then convert them...
remedies = converter.getCompleteRemedyTable(allRubricsFromFile, repertoryAbbrev)
rubrics = converter.getCompleteRubricTable(allRubricsFromFile, repertoryAbbrev)
rubricremedies = converter.getCompleteRubricRemedyTable(remedies, rubrics, allRubricsFromFile)

# Then print & insert into DB
# (we only print the SQL statements; actual insertion is done by removing comment from
# cursor.execute and connection.commit statements)

connection = psycopg2.connect(user = "oorep_user",
                             password = os.environ['OOREP_DBUSER_PASS'],
                             host = "127.0.0.1",
                             port = "5432",
                             database = "oorep")
cursor = connection.cursor()

# This one needs a live DB cursor, so we can lookup a remedy's longname in the DB, if there is one
for i in range(0, len(remedies)):
     sqlStmt = remedies[i].getSqlInsertStatement(cursor)
     print(str(i + 1) + ": " + sqlStmt)
#      cursor.execute(sqlStmt)
# connection.commit()

# This one needs ALL rubrics, in order to find out, if a rubric is a "mother-rubric"
for i in range(0, len(rubrics)):
    sqlStmt = rubrics[i].getSqlInsertStatement(allRubricsFromFile)
    print(str(i + 1) + ": " + sqlStmt)
#     cursor.execute(sqlStmt)
# connection.commit()

for i in range(0, len(rubricremedies)):
    sqlStmt = rubricremedies[i].getSqlInsertStatement()
    print(str(i + 1) + ": " + sqlStmt)
#     cursor.execute(sqlStmt)
# connection.commit()

# ###################################################################
# Showcase a utility function

utility.printUniqueRemedies(allRubricsFromFile, cursor)

# ###################################################################
# Also see 'test.py' for example usage!
