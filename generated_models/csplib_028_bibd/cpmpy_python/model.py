# csplib_028_bibd: a CPMpy model from DCP Rosetta.
# Download the `csplib_028_bibd.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_028_bibd.html
# Then run it on the first instance (after `pip install cpmpy`):
#   python csplib_028_bibd.py csplib_028_bibd.json

import cpmpy as cp


def create_model(instance):
    """Arrange v objects into b blocks so that each block holds exactly k objects, each object
    occurs in exactly r blocks, and every two distinct objects occur together in exactly l blocks.
    The answer is the v-by-b incidence matrix."""
    v = instance["v"]  # the number of objects
    b = instance["b"]  # the number of blocks
    r = instance["r"]  # the number of blocks each object occurs in
    k = instance["k"]  # the number of objects in each block
    l = instance["l"]  # the number of blocks in which each pair of objects occurs together

    # matrix[i, j] is true when object i belongs to block j
    matrix = cp.boolvar(shape=(v, b), name="matrix")

    model = cp.Model()

    # Every object occurs in exactly r blocks (each row sums to r).
    model.add(matrix.sum(axis=1) == r)

    # Every block contains exactly k objects (each column sums to k).
    model.add(matrix.sum(axis=0) == k)

    # Any two distinct objects occur together in exactly l blocks (the scalar product of their
    # rows is l).
    for i in range(v):
        for j in range(i + 1, v):
            model.add(cp.sum(matrix[i, :] * matrix[j, :]) == l)

    return model, {"matrix": matrix}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    if model.solve():
        for name, variables in outputs.items():
            print(name, "=", variables.value())
    else:
        print("No solution:", model.status())
