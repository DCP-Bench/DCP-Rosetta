# csplib_044_steiner: an Exact (Python) model from DCP Rosetta.
# Download the `csplib_044_steiner.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_044_steiner.html
# Then run it on the first instance (after `pip install exact numpy`):
#   python csplib_044_steiner.py csplib_044_steiner.json

from exact import Exact


def create_model(instance):
    """Find n * (n - 1) / 6 triples of distinct elements of {1, ..., n} such that any two
    triples have at most one element in common (n is 1 or 3 modulo 6)."""
    n = instance["n"]          # the number of elements
    n_sets = n * (n - 1) // 6  # the number of triples required

    solver = Exact()

    # Exact identifies its variables by name.
    # sets[i][j] is 1 when element j belongs to triple i
    sets = [[f"sets_{i}_{j}" for j in range(n)] for i in range(n_sets)]
    for row in sets:
        for name in row:
            solver.addVariable(name, 0, 1)

    # Each triple has exactly three elements.
    for row in sets:
        solver.addConstraint([(1, name) for name in row], True, 3, True, 3)

    # Each pair of elements lies in at most one triple.
    for p in range(n):
        for q in range(p + 1, n):
            # both[i] is 1 when triple i holds elements p and q.
            both = []
            for i in range(n_sets):
                name = f"both_{p}_{q}_{i}"
                solver.addVariable(name, 0, 1)
                solver.addConstraint([(1, name), (-1, sets[i][p]), (-1, sets[i][q])], True, -1)
                both.append((1, name))
            solver.addConstraint(both, False, 0, True, 1)

    return solver, {"sets": sets}


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
