# ############################################################################
# Repertory converter / parser / importer for OOREP (https://www.oorep.com/)
# Copyright (c) 2021  Andreas Bauer <a@pspace.org>
# License: GPL v3.0 (or higher)

import parser
import psycopg2

# Find those remedies in the parsed repertory that do not appear or have different names
# in the repertories stored already in OOREP's database

def printUniqueRemedies(rubrics: list[parser.Rubric], cursor: psycopg2._psycopg.cursor):
    # Extract all local remedies from 'rubrics'
    allRemedies = set()
    for rubric in rubrics:
        for remedy in rubric.remedies:
            allRemedies.add(remedy.abbrev)

    cursor.execute("select nameabbrev from remedy;")
    dbRemedies = list(map(lambda x: x[0], cursor.fetchall()))

    # Find and print those local remedies, which are not in the DB
    for remedy in sorted(allRemedies):
        if not remedy in sorted(dbRemedies):
            print(remedy)
