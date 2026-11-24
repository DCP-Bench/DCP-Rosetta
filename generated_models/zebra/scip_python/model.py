# zebra: a SCIP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/zebra.html
# Run it (after `pip install pyscipopt numpy`) with:
#   python zebra.py

import numpy as np
from pyscipopt import Model

# The statement fixes five houses and five values per category. The outputs number the houses
# 0 (leftmost) to 4 (rightmost).
HOUSES = np.arange(5)

# The values of each category, in the order the statement lists them; each is an index
# into the rows of that category's table.
YELLOW, GREEN, RED, WHITE, BLUE = range(5)
ITALY, SPAIN, JAPAN, ENGLAND, NORWAY = range(5)
CAT, ZEBRA, BEAR, SNAILS, HORSE = range(5)
MILK, WATER, TEA, COFFEE, JUICE = range(5)
PAINTER, SCULPTOR, DIPLOMAT, PIANIST, DOCTOR = range(5)


def create_model(instance):
    """The Zebra puzzle (Einstein's puzzle): five houses in a row, numbered 0 (leftmost)
    to 4 (rightmost), each with one inhabitant. Each house has a different colour, and
    each inhabitant a different nationality, pet, drink and job. Find the house of every
    colour, nationality, pet, drink and job so that all the clues hold.

    The instance file is empty ([]): the statement fixes every datum, so the instance
    argument is not read. The outputs give, for each category, the house of each of its
    values, in the order the statement lists them. The clues as written leave more than one
    assignment open, so the model returns one of them.
    """
    model = Model("zebra")

    # colour[c, h] is 1 when house h is painted colour c, and 0 when not
    colour = model.addMatrixVar((5, 5), vtype="B", name="colour")
    # nation[n, h] is 1 when the inhabitant of house h is of nationality n
    nation = model.addMatrixVar((5, 5), vtype="B", name="nation")
    # pet[p, h] is 1 when the inhabitant of house h owns pet p
    pet = model.addMatrixVar((5, 5), vtype="B", name="pet")
    # drink[d, h] is 1 when the inhabitant of house h drinks d
    drink = model.addMatrixVar((5, 5), vtype="B", name="drink")
    # job[j, h] is 1 when the inhabitant of house h has job j
    job = model.addMatrixVar((5, 5), vtype="B", name="job")

    # SCIP has no all-different constraint, so each category is written as one-hot binaries:
    # every house has exactly one value of each category (columns), and every value is in
    # exactly one house (rows).
    for table in (colour, nation, pet, drink, job):
        model.addMatrixCons(table.sum(axis=0) == 1)
        model.addMatrixCons(table.sum(axis=1) == 1)

    # The house number of each value: exactly one house term is 1, so this is that value's house.
    colour_house = (colour * HOUSES).sum(axis=1)
    nation_house = (nation * HOUSES).sum(axis=1)
    pet_house = (pet * HOUSES).sum(axis=1)
    drink_house = (drink * HOUSES).sum(axis=1)
    job_house = (job * HOUSES).sum(axis=1)

    # The painter owns the horse.
    model.addCons(job_house[PAINTER] == pet_house[HORSE])
    # The diplomat drinks coffee.
    model.addCons(job_house[DIPLOMAT] == drink_house[COFFEE])
    # The one who drinks milk lives in the white house.
    model.addCons(drink_house[MILK] == colour_house[WHITE])
    # The Spaniard is a painter.
    model.addCons(nation_house[SPAIN] == job_house[PAINTER])
    # The Englishman lives in the red house.
    model.addCons(nation_house[ENGLAND] == colour_house[RED])
    # The snails are owned by the sculptor.
    model.addCons(pet_house[SNAILS] == job_house[SCULPTOR])
    # The green house is immediately on the left of the red one.
    model.addCons(colour_house[GREEN] + 1 == colour_house[RED])
    # The Norwegian lives immediately on the right of the blue house.
    model.addCons(nation_house[NORWAY] == colour_house[BLUE] + 1)
    # The doctor drinks milk.
    model.addCons(job_house[DOCTOR] == drink_house[MILK])
    # The diplomat is Japanese.
    model.addCons(job_house[DIPLOMAT] == nation_house[JAPAN])
    # The Norwegian owns the zebra.
    model.addCons(nation_house[NORWAY] == pet_house[ZEBRA])
    # The green house is next to the white one.
    model.addCons(abs(colour_house[GREEN] - colour_house[WHITE]) == 1)
    # The horse is owned by the neighbour of the diplomat.
    model.addCons(abs(pet_house[HORSE] - job_house[DIPLOMAT]) == 1)
    # The Italian lives in the red, white or green house, so his house is neither the blue nor
    # the yellow one. In each house, being Italian and being blue (or yellow) sum to at most 1.
    model.addMatrixCons(nation[ITALY] + colour[BLUE] <= 1)
    model.addMatrixCons(nation[ITALY] + colour[YELLOW] <= 1)

    # No objective: the puzzle asks for an assignment that satisfies the clues, not an optimum.
    outputs = {
        "colors": colour_house,
        "drinks": drink_house,
        "jobs": job_house,
        "nations": nation_house,
        "pets": pet_house,
    }
    return model, outputs


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
