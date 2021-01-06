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

filename = 'oorep_importer/SKRep3.txt'
repertoryAbbrev = "bogsk-de"

# First parse
allRubricsFromFile = parser.getAllRubricsFromFile(filename)

# Then convert
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
for r in remedies:
    sqlStmt = r.getSqlInsertStatement(cursor)
    print(sqlStmt)
#     cursor.execute(sqlStmt)
# connection.commit()

# This one needs ALL rubrics, in order to find out, if a rubric is a "mother-rubric"
for r in rubrics:
    sqlStmt = r.getSqlInsertStatement(allRubricsFromFile)
    print(sqlStmt)
#     cursor.execute(sqlStmt)
# connection.commit()

for r in rubricremedies:
    sqlStmt = r.getSqlInsertStatement()
    print(sqlStmt)
#     cursor.execute(sqlStmt)
# connection.commit()

# ###################################################################
# Showcase a utility function

utility.printUniqueRemedies(allRubricsFromFile, cursor)

# ###################################################################
# Also see 'test.py' for example usage!
