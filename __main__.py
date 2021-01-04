# ############################################################################
# Repertory converter / parser / importer for OOREP (https://www.oorep.com/)
# Copyright (c) 2021  Andreas Bauer <a@pspace.org>
# License: GPL v3.0 (or higher)

import parser
import converter
import utility
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

# Then insert into DB
# (we only print the SQL statements; actual insertion is left as an exercise to the reader)
for r in remedies:
    print(r.getSqlInsertStatement())

for r in rubrics:
    print(r.getSqlInsertStatement())

for r in rubricremedies:
    print(r.getSqlInsertStatement())


import pathlib
print(pathlib.Path().absolute())

# ###################################################################
# Showcase a utility function

utility.printUniqueRemedies(allRubricsFromFile,
                            "oorep_user",
                            os.environ['OOREP_DBUSER_PASS'],
                            "127.0.0.1",
                            5432,
                            "oorep")

# ###################################################################
# Also see 'test.py' for example usage!
