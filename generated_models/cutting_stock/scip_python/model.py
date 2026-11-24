# cutting_stock: a SCIP (Python) model from DCP Rosetta.
# Download the `cutting_stock.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/cutting_stock.html
# Then run it on the first instance (after `pip install pyscipopt numpy`):
#   python cutting_stock.py cutting_stock.json

import numpy as np
from pyscipopt import Model


def create_model(instance):
    """Rolls of one width are cut into pieces of several ordered widths. The
    cutting patterns are given: each is one way of cutting a roll, with the
    number of pieces of each width it yields. Choose how many rolls to cut with
    each pattern so that every width gets at least its ordered number of pieces,
    using as few rolls as possible."""
    num_patterns = instance["num_patterns"]  # how many cutting patterns are listed
    pieces = np.array(instance["num_rolls_width"])  # pieces[k][i]: pieces of width i that one roll cut with pattern k gives
    orders = np.array(instance["orders"])  # orders[i]: how many pieces of width i are ordered

    model = Model("cutting_stock")

    # used[k] is how many rolls are cut with pattern k: a whole number, at least 0.
    # The data gives no upper bound on it, so none is set.
    used = model.addMatrixVar(num_patterns, vtype="I", lb=0, name="used")

    # rolls is the total number of rolls cut, held in its own integer variable.
    rolls = model.addVar("rolls", vtype="I", lb=0)
    model.addCons(rolls == used.sum())  # the total of the rolls cut with each pattern

    # Each width gets at least its ordered number of pieces. The pieces of that width
    # from all rolls cut add up to the order or more; the statement says "meets",
    # read here as "at least", since a pattern can yield more pieces than ordered.
    model.addMatrixCons(pieces.T @ used >= orders)

    # Minimise the total number of rolls cut.
    model.setObjective(rolls, "minimize")

    return model, {"min_rolls_cut": rolls, "patterns_used": used}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.hideOutput()  # no solver log
    model.optimize()

    if model.getStatus() == "optimal":  # a proven optimum, or with no objective a solution
        value = np.vectorize(lambda var: round(model.getVal(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.getStatus())
