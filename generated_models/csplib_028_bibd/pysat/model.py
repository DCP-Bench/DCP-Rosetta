# csplib_028_bibd: a PySAT (Python) model from DCP Rosetta.
# Download the `csplib_028_bibd.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_028_bibd.html
# Then run it on the first instance (after `pip install "python-sat[pblib]" numpy`):
#   python csplib_028_bibd.py csplib_028_bibd.json

from pysat.card import CardEnc, EncType
from pysat.formula import CNF, IDPool


def create_model(instance):
    """Arrange v objects into b blocks so that each block holds exactly k objects, each object lies
    in exactly r blocks, and every two distinct objects lie together in exactly lambda blocks. The
    answer is the v-by-b incidence matrix."""
    v = instance["v"]    # the number of objects
    b = instance["b"]    # the number of blocks
    r = instance["r"]    # the number of blocks each object lies in
    k = instance["k"]    # the number of objects in each block
    lam = instance["l"]  # lambda: the number of blocks that any two distinct objects share

    pool = IDPool()

    # matrix[i][j] is true when object i belongs to block j
    matrix = [[pool.id(("matrix", i, j)) for j in range(b)] for i in range(v)]

    cnf = CNF()

    # Every object lies in exactly r blocks.
    for i in range(v):
        cnf.extend(CardEnc.equals(lits=matrix[i], bound=r, vpool=pool, encoding=EncType.seqcounter).clauses)

    # Every block holds exactly k objects.
    for j in range(b):
        cnf.extend(CardEnc.equals(lits=[matrix[i][j] for i in range(v)], bound=k, vpool=pool,
                                  encoding=EncType.seqcounter).clauses)

    # Any two distinct objects share exactly lam blocks.
    for i1 in range(v):
        for i2 in range(i1 + 1, v):
            # the blocks that contain both i1 and i2
            together = []
            for j in range(b):
                # both is true exactly when objects i1 and i2 both belong to block j
                both = pool.id(("both", i1, i2, j))
                cnf.append([-both, matrix[i1][j]])
                cnf.append([-both, matrix[i2][j]])
                cnf.append([both, -matrix[i1][j], -matrix[i2][j]])
                together.append(both)
            cnf.extend(CardEnc.equals(lits=together, bound=lam, vpool=pool, encoding=EncType.seqcounter).clauses)

    return cnf, {"matrix": matrix}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np
    from pysat.solvers import Solver

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    formula, outputs = create_model(instances[index])

    solver = Solver(bootstrap_with=formula)
    solver.solve()
    model = solver.get_model()  # None when there is no solution

    if model:
        # a literal is true when it is in the model
        value = np.vectorize(lambda lit: lit in model)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")
