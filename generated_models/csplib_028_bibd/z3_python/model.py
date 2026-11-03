# csplib_028_bibd: a Z3 (Python) model from DCP Rosetta.
# Download the `csplib_028_bibd.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_028_bibd.html
# Then run it on the first instance (after `pip install z3-solver numpy`):
#   python csplib_028_bibd.py csplib_028_bibd.json

import z3


def create_model(instance):
    """Arrange v objects into b blocks so that each block holds exactly k objects, each object is
    in exactly r blocks, and every two distinct objects share exactly l blocks. The answer is the
    v-by-b incidence matrix."""
    v = instance["v"]  # the number of objects
    b = instance["b"]  # the number of blocks
    r = instance["r"]  # the number of blocks each object is in
    k = instance["k"]  # the number of objects in each block
    l = instance["l"]  # the number of blocks that contain any two given objects

    # matrix[i][j] is true when object i is in block j
    matrix = [[z3.Bool(f"matrix_{i}_{j}") for j in range(b)] for i in range(v)]

    solver = z3.Solver()

    # Every object is in exactly r blocks.
    solver.add([z3.PbEq([(matrix[i][j], 1) for j in range(b)], r) for i in range(v)])

    # Every block contains exactly k objects.
    solver.add([z3.PbEq([(matrix[i][j], 1) for i in range(v)], k) for j in range(b)])

    # Any two distinct objects are together in exactly l blocks.
    for i1 in range(v):
        for i2 in range(i1 + 1, v):
            solver.add(
                z3.PbEq([(z3.And(matrix[i1][j], matrix[i2][j]), 1) for j in range(b)], l))

    return solver, {"matrix": matrix}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])

    status = solver.check()
    if status == z3.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output, model_completion=True))
    else:
        print("No solution:", status)
