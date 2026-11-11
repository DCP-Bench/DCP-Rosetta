# csplib_028_bibd: a PyCSP3 model from DCP Rosetta.
# Download the `csplib_028_bibd.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_028_bibd.html
# Then run it on the first instance (after `pip install pycsp3`, which also needs Java for its ACE solver):
#   python csplib_028_bibd.py csplib_028_bibd.json

from pycsp3 import *


def create_model(instance):
    """Find a balanced incomplete block design: an arrangement of v distinct objects into b blocks such
    that each block contains exactly k distinct objects, each object occurs in exactly r blocks, and
    every two distinct objects occur together in exactly lambda blocks. Give its v by b incidence
    matrix, which has exactly r ones per row, k ones per column, and a scalar product of lambda between
    any two distinct rows."""
    n_objects = instance["v"]   # v, the number of objects (the rows of the incidence matrix)
    n_blocks = instance["b"]    # b, the number of blocks (the columns)
    r = instance["r"]           # r, the number of blocks each object occurs in
    k = instance["k"]           # k, the number of objects each block contains
    lam = instance["l"]         # lambda, the number of blocks in which every two objects occur together

    # incidence[i][j] is 1 when object i is in block j, and 0 otherwise
    incidence = VarArray(size=[n_objects, n_blocks], dom={0, 1})

    satisfy(
        # Each object occurs in exactly r blocks.
        [Sum(row) == r for row in incidence],
        # Each block contains exactly k objects.
        [Sum(column) == k for column in columns(incidence)],
        # Every two distinct objects occur together in exactly lambda blocks: the scalar product of their rows
        # counts the blocks that contain both.
        [Sum(incidence[first][j] * incidence[second][j] for j in range(n_blocks)) == lam
         for first in range(n_objects) for second in range(first + 1, n_objects)],
    )

    return {"matrix": incidence}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    outputs = create_model(instances[index])
    if solve() is SAT:
        print("matrix", "=")
        for row in outputs["matrix"]:
            print(values(row))
    else:
        print("No solution:", status())
