# csplib_028_bibd: an Exact (Python) model from DCP Rosetta.
# Download the `csplib_028_bibd.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_028_bibd.html
# Then run it on the first instance (after `pip install exact numpy`):
#   python csplib_028_bibd.py csplib_028_bibd.json

from exact import Exact


def create_model(instance):
    """Balanced incomplete block design: arrange v objects into b blocks so that every block holds
    k objects, every object lies in r blocks, and any two distinct objects share exactly l blocks."""
    v = instance["v"]  # the number of objects
    b = instance["b"]  # the number of blocks
    r = instance["r"]  # the number of blocks each object lies in
    k = instance["k"]  # the number of objects in each block
    l = instance["l"]  # the number of blocks that any two distinct objects share

    solver = Exact()

    # Exact identifies its variables by name.
    # matrix[i][j] is 1 when object i belongs to block j, and 0 when not
    matrix = [[f"matrix_{i}_{j}" for j in range(b)] for i in range(v)]
    for row in matrix:
        for name in row:
            solver.addVariable(name, 0, 1)

    # Each object lies in exactly r blocks.
    for i in range(v):
        solver.addConstraint([(1, name) for name in matrix[i]], True, r, True, r)
    # Each block holds exactly k objects.
    for j in range(b):
        solver.addConstraint([(1, matrix[i][j]) for i in range(v)], True, k, True, k)

    # Any two distinct objects share exactly l blocks.
    for i1 in range(v):
        for i2 in range(i1 + 1, v):
            # both[i1][i2][j] is 1 when objects i1 and i2 both belong to block j, and 0 when not
            together = []
            for j in range(b):
                both = f"both_{i1}_{i2}_{j}"
                solver.addVariable(both, 0, 1)
                solver.addConstraint([(1, both), (-1, matrix[i1][j])], False, 0, True, 0)
                solver.addConstraint([(1, both), (-1, matrix[i2][j])], False, 0, True, 0)
                solver.addConstraint([(1, both), (-1, matrix[i1][j]), (-1, matrix[i2][j])], True, -1)
                together.append((1, both))
            solver.addConstraint(together, True, l, True, l)

    return solver, {"matrix": matrix}


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
