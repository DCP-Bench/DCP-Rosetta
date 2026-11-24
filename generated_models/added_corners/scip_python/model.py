# added_corners: a SCIP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/added_corners.html
# Run it (after `pip install pyscipopt numpy`) with:
#   python added_corners.py

from pyscipopt import Model, quicksum


def create_model(instance):
    """Added corners: write the digits 1 through 8 into the eight cells of a
    ring-shaped figure. Four cells are circles (C) at the corners and four are
    squares (F) on the edges. Each digit is used once, and each square holds the
    sum of the two circles that touch it.

    The instance is an empty list: the figure and the digits are fixed by the
    statement, so the argument is not read.
    """
    model = Model("added_corners")

    # Cells are numbered in reading order, left to right, top to bottom:
    #   0 top-left circle      1 top square        2 top-right circle
    #   3 left square          4 right square
    #   5 bottom-left circle   6 bottom square     7 bottom-right circle

    # digit[p] is the number written in cell p, a whole number from 1 to 8.
    # The bounds 1 and 8 come from the statement: the digits are 1 through 8.
    digit = [model.addVar(f"digit_{p}", vtype="I", lb=1, ub=8) for p in range(8)]

    # place[p, v] is 1 when cell p holds the digit v, and 0 when not.
    # SCIP has no all-different constraint, so each cell gets one binary per digit
    # (one-hot), and each digit is used in exactly one cell. This is stronger than
    # pairwise !=, which SCIP cannot state directly either.
    place = {(p, v): model.addVar(f"place_{p}_{v}", vtype="B")
             for p in range(8) for v in range(1, 9)}

    # link digit[p] to its binaries
    for p in range(8):
        # each cell holds exactly one digit
        model.addCons(quicksum(place[p, v] for v in range(1, 9)) == 1)
        # digit[p] is the digit that the chosen binary picks
        model.addCons(digit[p] == quicksum(v * place[p, v] for v in range(1, 9)))
    for v in range(1, 9):
        # the digit v is used in exactly one cell
        model.addCons(quicksum(place[p, v] for p in range(8)) == 1)

    # Each square holds the sum of the two circles that touch it.
    model.addCons(digit[1] == digit[0] + digit[2])  # top square = top-left + top-right circle
    model.addCons(digit[3] == digit[0] + digit[5])  # left square = top-left + bottom-left circle
    model.addCons(digit[4] == digit[2] + digit[7])  # right square = top-right + bottom-right circle
    model.addCons(digit[6] == digit[5] + digit[7])  # bottom square = bottom-left + bottom-right circle

    # No objective: any arrangement that meets the rules is an answer.
    return model, {"positions": digit}


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
