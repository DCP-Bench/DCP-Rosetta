# autoref: an Exact (Python) model from DCP Rosetta.
# Download the `autoref.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/autoref.html
# Then run it on the first instance (after `pip install exact numpy`):
#   python autoref.py autoref.json

from exact import Exact


def create_model(instance):
    """Find a series s[0], s[1], ..., s[n+1] in which every integer i from 0 to n
    occurs exactly s[i] times, and whose last element s[n+1] equals m."""
    n = instance["n"]  # the values 0 to n are counted in the series
    m = instance["m"]  # the required value of the last element

    solver = Exact()

    n_positions = n + 2  # the series has n + 2 elements

    # Exact identifies its variables by name.
    # s[k] is the k-th element of the series; each element lies between 0 and n
    s = [f"s_{k}" for k in range(n_positions)]
    for k in range(n_positions - 1):
        solver.addVariable(s[k], 0, n)

    # The last element is m.
    solver.addVariable(s[n_positions - 1], m, m)

    # holds[k][v] is 1 when element k of the series is v, and 0 when not
    holds = [{} for _ in range(n_positions)]
    for k in range(n_positions):
        for v in range(n + 1):
            holds[k][v] = f"holds_{k}_{v}"
            solver.addVariable(holds[k][v], 0, 1)

    # Each element of the series is exactly one value from 0 to n.
    for k in range(n_positions):
        solver.addConstraint([(1, holds[k][v]) for v in range(n + 1)], True, 1, True, 1)

    # Element s[k] is the value it holds.
    for k in range(n_positions):
        solver.addConstraint([(v, holds[k][v]) for v in range(1, n + 1)] + [(-1, s[k])], True, 0, True, 0)

    # The value i occurs exactly s[i] times in the series, for every i from 0 to n.
    for i in range(n + 1):
        solver.addConstraint([(1, holds[k][i]) for k in range(n_positions)] + [(-1, s[i])], True, 0, True, 0)

    return solver, {"s": s}


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
