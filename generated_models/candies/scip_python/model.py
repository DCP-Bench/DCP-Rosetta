# candies: a SCIP (Python) model from DCP Rosetta.
# Download the `candies.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/candies.html
# Then run it on the first instance (after `pip install pyscipopt numpy`):
#   python candies.py candies.json

from pyscipopt import Model, quicksum


def create_model(instance):
    """Alice gives candies to the children, who sit in a line, each with a
    rating score. Every child gets at least one candy, and of two neighbours
    the one with the higher rating gets more candies than the other. Minimise
    the total number of candies handed out."""
    ratings = instance["ratings"]  # ratings[i]: the rating score of child i, in line order
    n = len(ratings)               # the number of children

    model = Model("candies")

    # x[i] is the number of candies child i gets. The bounds come from the
    # problem: at least 1 candy each. The upper bound n holds for an optimal
    # handout: the chain of neighbours that forces a child's count is strictly
    # monotone in rating, so it has at most n children.
    x = [model.addVar(f"x_{i}", vtype="I", lb=1, ub=n) for i in range(n)]

    # z is the total number of candies. It is a variable (not a bare expression)
    # so the optimum can be pinned when enumerating optimal handouts. Its bounds
    # follow from the bounds on x: at least one candy each, at most n each.
    z = model.addVar("z", vtype="I", lb=n, ub=n * n)

    # Neighbours with different ratings: the child with the higher rating gets
    # more candies. Neighbours with equal ratings have no constraint between them.
    for i in range(n - 1):
        if ratings[i] > ratings[i + 1]:
            model.addCons(x[i] >= x[i + 1] + 1)  # child i has the higher rating
        elif ratings[i] < ratings[i + 1]:
            model.addCons(x[i + 1] >= x[i] + 1)  # child i + 1 has the higher rating

    # z is the total of all candies handed out.
    model.addCons(z == quicksum(x))

    # Minimise the total number of candies.
    model.setObjective(z, "minimize")

    return model, {"x": x, "z": z}


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
