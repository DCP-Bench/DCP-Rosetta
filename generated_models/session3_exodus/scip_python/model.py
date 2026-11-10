# session3_exodus: a SCIP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session3_exodus.html
# Run it (after `pip install pyscipopt numpy`) with:
#   python session3_exodus.py

import numpy as np
from pyscipopt import Model

# The lists the statement gives, in its order. The problem fixes all of them,
# so the instance file is empty ([]) and the model reads no data from it.
BERNICE, CARL, DEBBY, SAMMY, TED = range(5)  # the five children
AGES = [3, 5, 7, 8, 10]                      # the ages, in years
ETHIOPIA, KAZAKHSTAN, LITHUANIA, MOROCCO, YEMEN = range(5)  # the family countries
BURNING_BUSH, CAPTIVITY, MOSES_YOUTH, PASSOVER, TEN_COMMANDMENTS = range(5)  # the stories


def create_model(instance):
    """Five children at Hebrew school each tell one part of the Exodus story, are
    each a different age, and come from a family that made its exodus from a
    different country. Find each child's age, family country and story from five
    clues. The instance file is empty ([]), so the statement fixes all the data."""
    model = Model("session3_exodus")

    # Each child gets a number from 1 to 5, the child's place in the statement:
    # Bernice is 1, Carl 2, Debby 3, Sammy 4, Ted 5. The four output lists use
    # these numbers, so the same number in two lists is the same child.
    labels = np.arange(1, 6)

    # age_is[c, a] is 1 when child c is AGES[a], and 0 when not
    age_is = model.addMatrixVar((5, 5), vtype="B", name="age_is")
    # country_is[c, k] is 1 when child c's family is from country k
    country_is = model.addMatrixVar((5, 5), vtype="B", name="country_is")
    # story_is[c, s] is 1 when child c tells story s
    story_is = model.addMatrixVar((5, 5), vtype="B", name="story_is")

    # Each child has exactly one age, one family country and one story.
    model.addMatrixCons(age_is.sum(axis=1) == 1)
    model.addMatrixCons(country_is.sum(axis=1) == 1)
    model.addMatrixCons(story_is.sum(axis=1) == 1)

    # Each age, each country and each story belongs to exactly one child, so the
    # five children have five different ages, and so on for countries and stories.
    model.addMatrixCons(age_is.sum(axis=0) == 1)
    model.addMatrixCons(country_is.sum(axis=0) == 1)
    model.addMatrixCons(story_is.sum(axis=0) == 1)

    # age[c] is the age of child c, the value in AGES of the age that child has
    age = age_is @ np.array(AGES)

    # The age of the child from each country we need, and of the child who tells
    # each story we need. There is one such child, because each country and each
    # story goes to exactly one child (above).
    country_age = {k: model.addVar(vtype="I", lb=AGES[0], ub=AGES[-1], name=f"age_of_country_{k}")
                   for k in (ETHIOPIA, MOROCCO, YEMEN)}
    story_age = {s: model.addVar(vtype="I", lb=AGES[0], ub=AGES[-1], name=f"age_of_story_{s}")
                 for s in (MOSES_YOUTH, PASSOVER)}
    for c in range(5):
        # If child c is from country k, that country's age is child c's age.
        # Two indicators make the equality, since addConsIndicator takes no equality.
        for k, k_age in country_age.items():
            model.addConsIndicator(k_age - age[c] <= 0, binvar=country_is[c, k])
            model.addConsIndicator(k_age - age[c] >= 0, binvar=country_is[c, k])
        # If child c tells story s, that story's age is child c's age.
        for s, s_age in story_age.items():
            model.addConsIndicator(s_age - age[c] <= 0, binvar=story_is[c, s])
            model.addConsIndicator(s_age - age[c] >= 0, binvar=story_is[c, s])

    # Clue 1: Debby's family is from Lithuania.
    model.addCons(country_is[DEBBY, LITHUANIA] == 1)
    # Clue 2: the child who told the Passover story is two years older than Bernice.
    model.addCons(story_age[PASSOVER] == age[BERNICE] + 2)
    # Clue 3: the child from the Yemeni family is younger than the child from the
    # Ethiopian family. Ages are whole years and there is no strict <, so "younger
    # than" is written as at least one year less.
    model.addCons(country_age[YEMEN] <= country_age[ETHIOPIA] - 1)
    # Clue 4: the child from the Moroccan family is three years older than Ted.
    model.addCons(country_age[MOROCCO] == age[TED] + 3)
    # Clue 5: Sammy is three years older than the child who told the story of Moses's
    # youth in the house of the Pharaoh.
    model.addCons(age[SAMMY] == story_age[MOSES_YOUTH] + 3)

    # ages[a] is the number of the child with age AGES[a]
    ages = age_is.T @ labels
    # children[c] is the number of child c. It is always c + 1, so its bounds are set to
    # that value; it is a variable only so it can be printed like the other outputs.
    children = model.addMatrixVar((5,), vtype="I", lb=labels, ub=labels, name="children")
    # countries[k] is the number of the child whose family is from country k
    countries = country_is.T @ labels
    # stories[s] is the number of the child who tells story s
    stories = story_is.T @ labels

    return model, {"ages": ages, "children": children, "countries": countries, "stories": stories}


if __name__ == "__main__":
    import numpy as np

    model, outputs = create_model({})
    model.hideOutput()  # no solver log
    model.optimize()

    if model.getStatus() == "optimal":  # a proven optimum, or with no objective a solution
        value = np.vectorize(lambda var: round(model.getVal(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.getStatus())
