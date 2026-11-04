# csplib_044_steiner: a cvc5 (Python) model from DCP Rosetta.
# Download the `csplib_044_steiner.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_044_steiner.html
# Then run it on the first instance (after `pip install cvc5 numpy`):
#   python csplib_044_steiner.py csplib_044_steiner.json

from itertools import combinations

import cvc5.pythonic as c5


def create_model(instance):
    """Find n * (n - 1) / 6 triples of distinct elements of {1, ..., n} such that any two
    triples have at most one element in common (n is 1 or 3 modulo 6)."""
    n = instance["n"]          # the number of elements
    n_sets = n * (n - 1) // 6  # the number of triples required

    # sets[i][j] is true when element j belongs to triple i
    sets = [[c5.Bool(f"sets_{i}_{j}") for j in range(n)] for i in range(n_sets)]

    def either(options):
        """At least one of the options holds."""
        return options[0] if len(options) == 1 else c5.Or(options)

    solver = c5.Solver()

    # Each triple has exactly three elements: no four elements are all in it, and no n - 2
    # elements are all out of it.
    for row in sets:
        solver.add([either([c5.Not(row[j]) for j in quad]) for quad in combinations(range(n), 4)])
        solver.add([either([row[j] for j in rest]) for rest in combinations(range(n), n - 2)])

    # Each element is in (n - 1) / 2 triples: it shares exactly one element with each of the
    # other n - 1 elements, and each triple through it covers two of them.
    triples_per_element = (n - 1) // 2
    solver.add([c5.Sum([c5.If(row[j], 1, 0) for row in sets]) == triples_per_element for j in range(n)])

    # Two triples share at most one element: no pair of elements lies in two triples.
    for i1, i2 in combinations(range(n_sets), 2):
        for j, k in combinations(range(n), 2):
            solver.add(c5.Not(c5.And(sets[i1][j], sets[i1][k], sets[i2][j], sets[i2][k])))

    # Every pair of elements lies in some triple.
    for j, k in combinations(range(n), 2):
        solver.add(either([c5.And(row[j], row[k]) for row in sets]))

    return solver, {"sets": sets}


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
