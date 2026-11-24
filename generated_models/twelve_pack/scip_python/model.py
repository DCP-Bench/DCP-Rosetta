# twelve_pack: a SCIP (Python) model from DCP Rosetta.
# Download the `twelve_pack.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/twelve_pack.html
# Then run it on the first instance (after `pip install pyscipopt numpy`):
#   python twelve_pack.py twelve_pack.json

import math

from pyscipopt import Model, quicksum


def create_model(instance):
    """Given a target number of items, find the closest combination of packs of
    different sizes that meets or exceeds the target: the packs bought must hold
    at least the target number of items, and as few items as possible above it.
    The output counts lists how many packs of each size to buy."""
    packs = instance["packs"]    # packs[i]: the number of items in one pack of kind i
    target = instance["target"]  # the least number of items the bought packs must hold

    model = Model("twelve_pack")

    # counts[i] is the number of packs of size packs[i] to buy, a whole number from
    # 0 up to its upper bound. The bound is implied, not stated by the problem: an
    # optimal solution never buys more than ceil(target / size) packs of one size,
    # since one pack fewer would still hold the target and buy fewer items. This
    # needs every pack size to be positive; a target of 0 or less gives bound 0.
    counts = []
    for i, size in enumerate(packs):
        ub = max(0, math.ceil(target / size))
        counts.append(model.addVar(name=f"count_{i}", vtype="I", lb=0, ub=ub))

    # The number of items in the bought packs.
    items_bought = quicksum(size * count for size, count in zip(packs, counts))

    # The bought packs hold at least the target number of items.
    model.addCons(items_bought >= target)

    # Among those, buy as few items as possible: the closest combination.
    model.setObjective(items_bought, "minimize")

    return model, {"counts": counts}


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
