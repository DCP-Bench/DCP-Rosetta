# kakuro: a Python-MIP (Python) model from DCP Rosetta.
# Download the `kakuro.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/kakuro.html
# Then run it on the first instance (after `pip install mip numpy`):
#   python kakuro.py kakuro.json

import mip


def create_model(instance):
    """Insert a digit from 1 to 9 into each white cell so that the digits in each entry
    add up to its clue and no digit repeats within an entry."""
    n = instance["n"]              # the grid is n by n
    blanks = instance["blanks"]    # the cells that hold no digit: black cells and clue cells
    problem = instance["problem"]  # the entries: each is its clue followed by the cells it covers

    model = mip.Model(solver_name="CBC")

    # the set of cells that hold no digit
    blank = {(r - 1, c - 1) for r, c in blanks}
    # the white cells, which take a digit
    white = [(r, c) for r in range(n) for c in range(n) if (r, c) not in blank]
    # the digits that can be placed in a white cell
    digits = list(range(1, 10))

    # value[(r, c)] is the digit in white cell (r, c)
    value = {}
    # pick[(r, c)][d] is 1 when cell (r, c) holds digit d, and 0 when not
    pick = {}
    for (r, c) in white:
        value[(r, c)] = model.add_var(f"x_{r}_{c}", lb=1, ub=9, var_type=mip.INTEGER)
        pick[(r, c)] = {}
        for d in digits:
            pick[(r, c)][d] = model.add_var(f"p_{r}_{c}_{d}", var_type=mip.BINARY)
        # Each white cell holds exactly one digit.
        model.add_constr(mip.xsum(pick[(r, c)][d] for d in digits) == 1)
        # The digit in the cell is the one picked.
        model.add_constr(value[(r, c)] == mip.xsum(d * pick[(r, c)][d] for d in digits))

    # the entries as (clue, cells) pairs
    entries = [(segment[0], [(r - 1, c - 1) for r, c in segment[1:]]) for segment in problem]

    # The digits in each entry add up to its clue.
    for clue, cells in entries:
        model.add_constr(mip.xsum(value[cell] for cell in cells) == clue)

    # No digit repeats within an entry.
    for _, cells in entries:
        for d in digits:
            model.add_constr(mip.xsum(pick[cell][d] for cell in cells) <= 1)

    # x is the grid row by row: the digit of each white cell, and 0 for a blank cell (an empty expression).
    x = [[value[(r, c)] if (r, c) in value else mip.LinExpr() for c in range(n)] for r in range(n)]

    return model, {"x": x}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.verbose = 0  # no solver log
    model.max_mip_gap = 0  # prove the optimum; the default stops within 0.01% of it
    status = model.optimize()

    if status == mip.OptimizationStatus.OPTIMAL:
        value = np.vectorize(lambda var: round(var.x))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", status.name)
