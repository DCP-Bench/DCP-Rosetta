# bales_of_hay: an Exact (Python) model from DCP Rosetta.
# Download the `bales_of_hay.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/bales_of_hay.html
# Then run it on the first instance (after `pip install exact numpy`):
#   python bales_of_hay.py bales_of_hay.json

from collections import Counter
from itertools import combinations

from exact import Exact


def create_model(instance):
    """Bales of hay were weighed in every combination of two, and the weights of the
    pairs were written down in numerical order, without saying which pair gave which
    weight. Find the weight of each bale."""
    n = instance["n"]              # the number of bales
    weights = instance["weights"]  # the written pair weights, in numerical order

    solver = Exact()

    # Exact identifies its variables by name.
    # bales[i] is the weight of bale i; no bale is heavier than the heaviest written weight
    bales = [f"bales_{i}" for i in range(n)]
    for name in bales:
        solver.addVariable(name, 0, max(weights))

    # pairs[p] is the p-th pair of different bales
    pairs = list(combinations(range(n), 2))
    # values are the distinct written weights, in numerical order
    values = sorted(set(weights))

    # weighs[p][v] is 1 when pair p weighs values[v], and 0 when not
    weighs = [[f"pair_{i}_{j}_weighs_{v}" for v in range(len(values))] for i, j in pairs]
    for row in weighs:
        for name in row:
            solver.addVariable(name, 0, 1)

    for p, (i, j) in enumerate(pairs):
        # Each pair weighs exactly one of the written weights.
        solver.addConstraint([(1, name) for name in weighs[p]], True, 1, True, 1)
        # The two bales of a pair add up to the weight of that pair.
        solver.addConstraint([(values[v], weighs[p][v]) for v in range(len(values))]
                             + [(-1, bales[i]), (-1, bales[j])], True, 0, True, 0)

    # counts[w] is how often the weight w was written down
    counts = Counter(weights)
    # Each written weight belongs to as many pairs as it was written down.
    for v, value in enumerate(values):
        solver.addConstraint([(1, weighs[p][v]) for p in range(len(pairs))],
                             True, counts[value], True, counts[value])

    return solver, {"bales": bales}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])
    solver.runFull()  # with an objective, searches until no better solution exists

    if solver.hasSolution():
        for name, output in outputs.items():
            values = solver.getLastSolutionFor(list(np.ravel(output)))
            print(name, "=", np.reshape(values, np.shape(output)))
    else:
        print("No solution")
