# csplib_028_bibd: a cvc5 (Python) model from DCP Rosetta.
# Download the `csplib_028_bibd.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_028_bibd.html
# Then run it on the first instance (after `pip install cvc5 numpy`):
#   python csplib_028_bibd.py csplib_028_bibd.json

import cvc5.pythonic as c5


def create_model(instance):
    """Arrange v distinct objects into b blocks so that each block contains exactly k objects,
    each object occurs in exactly r blocks, and every two distinct objects occur together in
    exactly l blocks."""
    n_objects = instance["v"]            # the number of objects
    n_blocks = instance["b"]             # the number of blocks
    n_blocks_per_object = instance["r"]  # the number of blocks each object occurs in
    n_objects_per_block = instance["k"]  # the number of objects in each block
    n_blocks_per_pair = instance["l"]    # the number of blocks in which any two objects occur together

    # matrix[i][j] is true when object i belongs to block j.
    matrix = [[c5.Bool(f"matrix_{i}_{j}") for j in range(n_blocks)] for i in range(n_objects)]

    solver = c5.Solver()

    # Every object occurs in exactly n_blocks_per_object blocks.
    for i in range(n_objects):
        solver.add(
            c5.Sum([c5.If(matrix[i][j], 1, 0) for j in range(n_blocks)]) == n_blocks_per_object)

    # Every block contains exactly n_objects_per_block objects.
    for j in range(n_blocks):
        solver.add(
            c5.Sum([c5.If(matrix[i][j], 1, 0) for i in range(n_objects)]) == n_objects_per_block)

    # Any two distinct objects occur together in exactly n_blocks_per_pair blocks.
    for i in range(n_objects):
        for i2 in range(i + 1, n_objects):
            solver.add(
                c5.Sum([c5.If(c5.And(matrix[i][j], matrix[i2][j]), 1, 0) for j in range(n_blocks)])
                == n_blocks_per_pair)

    return solver, {"matrix": matrix}


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
