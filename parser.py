# ############################################################################
# Repertory converter / parser / importer for OOREP (https://www.oorep.com/)
# Copyright (c) 2021  Andreas Bauer <a@pspace.org>
# License: GPL v3.0 (or higher)

from parsita import *

# Types ######################################################################

class Remedy:
    def __init__(self, abbrev: str, weight: int):
        self.abbrev = abbrev.capitalize()
        self.weight = weight
    def __str__(self):
        if self.weight > 1:
            return self.abbrev + " (" + str(self.weight) + ")"
        else:
            return self.abbrev
    def __repr__(self):
        return str(self)

class Rubric:
    index = -1
    parentIndex = -1
    fullPath = []

    def __init__(self, text: str, depth: int, remedies: list[Remedy]):
        self.text = text
        self.depth = depth
        self.remedies = remedies

    def __str__(self):
        if len(self.remedies) > 0:
            remedies = ""
            for remedy in self.remedies:
                remedies += str(remedy) + " "
            return (self.depth * " ") + self.text + ": " + remedies.rstrip()
        else:
            return (self.depth * " ") + self.text

    def __repr__(self):
        return str(self)

    def getParentPathFromParentIndices(self, indices: list[int], allRubrics):
        fullPath = []
        for parent in indices:
            fullPath.append(allRubrics[parent].text)
        return fullPath[::-1]

    def getParentIndices(self, rubric, indices: list[int], allRubrics):
        if rubric.parentIndex < 0:
            return indices
        else:
            indices.append(rubric.parentIndex)
            return rubric.getParentIndices(allRubrics[rubric.parentIndex], indices, allRubrics)

    def getFullPath(self, allRubrics):
        path = self.getParentPathFromParentIndices(self.getParentIndices(self, [], allRubrics), allRubrics)
        path.append(self.text)
        return path

# Parsers ####################################################################

class RemedyLexer(TextParsers, whitespace=None):
    abbrev = reg(r'[A-Z](-?[a-z]+)+\.?')
    abbrevFourValued = reg(r'[A-Z](-?[A-Z]+)+\.?')
    weight = reg(r'[0-9]+') > int
    weightBrackets = '(' >> weight << ')'

class RemedyParser(TextParsers, whitespace=None):
    remedyFourValued = RemedyLexer.abbrevFourValued > (lambda x: Remedy(x, 4))
    remedyNoWeight = RemedyLexer.abbrev > (lambda x: Remedy(x, 1))
    remedyWithWeight = RemedyLexer.abbrev << reg(r'[ \t]*') & RemedyLexer.weightBrackets > (lambda x: Remedy(x[0], x[1]))

    remedy = remedyWithWeight | remedyFourValued | remedyNoWeight

class RemediesParser(TextParsers, whitespace=None):
    remedies = repsep(RemedyParser.remedy, reg(r',?[ \t]+'))

class RubricTextParser(TextParsers, whitespace=None):
    rubricRawString = reg(r'[A-Za-z\-äöüßÄÖÜ0-9 \.,;\(\)]+[A-Za-zäöüßÄÖÜ0-9\(\)\.]')
    rubricDepth = reg(r'=+') > (lambda x: int(len(x)))
    rubricText = rubricDepth & reg(r'[ \t]*') >> rubricRawString

class RubricParser(TextParsers, whitespace=None):
    emptyRubric = RubricTextParser.rubricText << reg(r'(\.|:)?[ \t]*$') > (lambda x: Rubric(x[1], x[0], []))
    nonEmptyRubric = RubricTextParser.rubricText << ':' & reg(r'[ \t]*') >> RemediesParser.remedies > (lambda x: Rubric(x[0][1], x[0][0], x[1]))

    rubric = nonEmptyRubric | emptyRubric

# The actual parser to call from the outside #################################
# Returns a list of type list[Rubric]

def getAllRubricsFromFileContents(lines: list[str]):
    rubricIndex = 0  # an index that will be incr. and added to every parsed rubric
    resultRubrics = []  # where the parsed rubrics gonna end up in
    parents = []

    for line in lines:
        if len(line) > 0:
            result = RubricParser.rubric.parse(line)
            if isinstance(result, Failure):
                print(result)
                exit(1)
            else:
                rubric = result.value
                rubric.index = rubricIndex

                # Adjust parents-array to link all rubrics transitively back to the chapter/root rubric node
                if rubric.depth == 1:
                    parents = [(rubric.depth, rubric.index)]
                # Subrubrics must only be at most one level deeper than parent.
                elif rubric.depth == parents[-1][0] + 1:
                    rubric.parentIndex = parents[-1][1]
                    parents.append((rubric.depth, rubric.index))
                elif rubric.depth == parents[-1][0]:
                    del parents[-1]
                    rubric.parentIndex = parents[-1][1]
                    parents.append((rubric.depth, rubric.index))
                elif rubric.depth < parents[-1][0]:
                    depthDifference = parents[-1][0] - rubric.depth + 1
                    for i in range(depthDifference):
                        del parents[-1]
                    rubric.parentIndex = parents[-1][1]
                    parents.append((rubric.depth, rubric.index))
                else:
                    print("ERROR: Subrubrics must only be at most one level deeper than parent. Check out line: " + rubric.text)
                    exit(1)

                resultRubrics.append(rubric)
                rubricIndex += 1

    return resultRubrics
