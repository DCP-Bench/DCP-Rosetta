# session2_color_simple: a SCIP (Python) model from DCP Rosetta.
# Download the `session2_color_simple.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session2_color_simple.html
# Then run it on the first instance (after `pip install pyscipopt numpy`):
#   python session2_color_simple.py session2_color_simple.json

import numpy as np
from pyscipopt import Model, quicksum


def create_model(instance):
    """Colour six countries (Belgium, Denmark, France, Germany, Netherlands and
    Luxembourg) so that neighbouring countries get different colours, using as
    few colours as possible. Colours are numbered from 1."""
    # The statement names six countries, so their number is fixed by the problem,
    # not read from the instance. Country i is the i-th name in the statement.
    n = 6

    # instance["graph"]: each [a, b] is a pair of neighbouring countries, numbered
    # from 1 in the order of the statement, so country a is row a - 1 below.
    borders = instance["graph"]

    # One colour per country always works, so n colours are enough. This bound
    # follows from the problem; it does not depend on the instance.
    n_colours = n

    model = Model("session2_color_simple")

    # b[i, k] is 1 when country i has colour k + 1, and 0 when not
    b = model.addMatrixVar((n, n_colours), vtype="B", name="b")

    # Each country has exactly one colour.
    model.addMatrixCons(b.sum(axis=1) == 1)

    # Neighbouring countries cannot have the same colour: for each border and each
    # colour, the two countries cannot both have that colour.
    for a, c in borders:
        model.addMatrixCons(b[a - 1] + b[c - 1] <= 1)

    # used[k] is 1 exactly when some country has colour k + 1. The OR constraint
    # forces it both ways, so it does not rely on the objective.
    used = model.addMatrixVar(n_colours, vtype="B", name="used")
    for k in range(n_colours):
        model.addConsOr(list(b[:, k]), used[k])

    # Minimise the number of colours used: the number of colours k with used[k] = 1.
    model.setObjective(quicksum(used), "minimize")

    # colors[i] is the colour number of country i, 1 to n_colours.
    colors = b @ np.arange(1, n_colours + 1)
    return model, {"colors": colors}


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
