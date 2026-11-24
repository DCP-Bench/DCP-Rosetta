# bales_of_hay: a SCIP (Python) model from DCP Rosetta.
# Download the `bales_of_hay.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/bales_of_hay.html
# Then run it on the first instance (after `pip install pyscipopt numpy`):
#   python bales_of_hay.py bales_of_hay.json
from pyscipopt import Model, quicksum


def create_model(instance):
    """Bales of hay: the bales were weighed two at a time, and only the list of
    all the pairwise weights survived, in numerical order and without saying which
    pair produced which weight. Find the weight of each bale."""
    n = instance["n"]              # the number of bales
    weights = instance["weights"]  # the weight of every pair of bales, in numerical order
    # The pairs of bales (i, j), i < j, in a fixed order: one recorded weight each.
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    assert len(pairs) == len(weights)  # n bales give n*(n-1)/2 pair weights

    model = Model("bales_of_hay")

    # bales[i] is the weight of bale i. A weight is a whole number, not negative
    # (lb=0), and no bale is heavier than the heaviest recorded pair, since the
    # partner of a bale weighs at least 0 (ub from the data).
    bales = [model.addVar(f"bale_{i}", vtype="I", lb=0, ub=max(weights)) for i in range(n)]

    # pick[p, k] is 1 when pair p of bales is the one that gave the k-th recorded weight.
    pick = model.addMatrixVar((len(pairs), len(weights)), vtype="B", name="pick")

    # Symmetry breaking: list the bales lightest first. Reordering bales never changes
    # the pair weights, so every answer has such an order and only repeats are removed.
    for i in range(n - 1):
        model.addCons(bales[i] <= bales[i + 1])

    # Every pair of bales gives exactly one recorded weight.
    model.addMatrixCons(pick.sum(axis=1) == 1)
    # Every recorded weight comes from exactly one pair, so the pair weights match the list exactly.
    model.addMatrixCons(pick.sum(axis=0) == 1)

    # The weight of each pair of bales is the recorded weight it was matched to.
    for p, (i, j) in enumerate(pairs):
        model.addCons(bales[i] + bales[j] == quicksum(w * pick[p, k] for k, w in enumerate(weights)))

    # No objective: any set of bale weights that reproduces the list is an answer.
    return model, {"bales": bales}


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
