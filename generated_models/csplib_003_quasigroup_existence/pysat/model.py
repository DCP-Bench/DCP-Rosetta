# csplib_003_quasigroup_existence: a PySAT (Python) model from DCP Rosetta.
# Download the `csplib_003_quasigroup_existence.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_003_quasigroup_existence.html
# Then run it on the first instance (after `pip install "python-sat[pblib]" numpy`):
#   python csplib_003_quasigroup_existence.py csplib_003_quasigroup_existence.json

from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def create_model(instance):
    """QG3.m quasigroup existence: find an order m quasigroup, an m by m table in which
    every element occurs once in each row and each column, with (a*b)*(b*a) = a for all
    a and b."""
    m = instance["m"]  # the order of the quasigroup; its elements are 0 to m-1

    pool = IDPool()
    # quasigroup[a][b] is the product a*b
    quasigroup = [[Integer(f"q_{a}_{b}", 0, m - 1, vpool=pool) for b in range(m)]
                  for a in range(m)]
    engine = IntegerEngine(vars=[cell for row in quasigroup for cell in row], vpool=pool)

    # Each element occurs once in every row and once in every column.
    for i in range(m):
        engine.add_alldifferent(quasigroup[i])
        engine.add_alldifferent([quasigroup[a][i] for a in range(m)])
    formula = engine.clausify()

    # (a*b)*(b*a) = a: when a*b is i and b*a is j, the product i*j is a.
    for a in range(m):
        for b in range(m):
            for i in range(m):
                for j in range(m):
                    formula.append([-quasigroup[a][b].equals(i),
                                    -quasigroup[b][a].equals(j),
                                    quasigroup[i][j].equals(a)])

    return formula, {"quasigroup": quasigroup}


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
        value = np.vectorize(lambda var: var.decode(model))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")
