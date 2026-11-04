# bales_of_hay: a cvc5 (Python) model from DCP Rosetta.
# Download the `bales_of_hay.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/bales_of_hay.html
# Then run it on the first instance (after `pip install cvc5 numpy`):
#   python bales_of_hay.py bales_of_hay.json

import cvc5.pythonic as c5


def create_model(instance):
    """Bales of hay were weighed in every combination of two, and the weights of the pairs
    were written down in numerical order without saying which pair gave which weight.
    Find the weight of each bale."""
    n = instance["n"]              # the number of bales
    weights = instance["weights"]  # the weight of each pair of bales, in numerical order
    n_weights = len(weights)

    # bales[i] is the weight of bale i
    bales = [c5.Int(f"bale_{i}") for i in range(n)]

    # every pair of different bales
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    n_pairs = len(pairs)

    # t[q] is the position in weights of the weight written down for pair q
    t = [c5.Int(f"t_{q}") for q in range(n_pairs)]

    solver = c5.Solver()

    # Each bale weighs between 0 and the heaviest written weight.
    solver.add([b >= 0 for b in bales] + [b <= max(weights) for b in bales])

    # The total weight of each pair is the written weight at its position t[q].
    for q, (i, j) in enumerate(pairs):
        solver.add(t[q] >= 0)
        solver.add(t[q] < n_weights)
        options = [c5.And(t[q] == k, bales[i] + bales[j] == weights[k]) for k in range(n_weights)]
        solver.add(c5.Or(options) if n_weights > 1 else options[0])

    # Each written weight belongs to exactly one pair.
    if n_pairs >= 2:
        solver.add(c5.Distinct(t))

    return solver, {"bales": bales}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])
    status = solver.check()

    if status == c5.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output))
    else:
        print("No solution:", status)
