# csplib_003_quasigroup_existence: a cvc5 (Python) model from DCP Rosetta.
# Download the `csplib_003_quasigroup_existence.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_003_quasigroup_existence.html
# Then run it on the first instance (after `pip install cvc5 numpy`):
#   python csplib_003_quasigroup_existence.py csplib_003_quasigroup_existence.json

import cvc5.pythonic as c5


def create_model(instance):
    """QG3.m quasigroup existence: find an order m quasigroup, a Latin square of size
    m with every element once in each row and column, such that (a*b)*(b*a) = a."""
    m = instance["m"]  # the order of the quasigroup
    rng = range(m)

    # quasigroup[a][b] is the product a*b, an element from 0 to m-1.
    quasigroup = [[c5.Int(f"quasigroup_{a}_{b}") for b in rng] for a in rng]

    solver = c5.Solver()

    # Each product is an element from 0 to m-1.
    solver.add([c5.And(0 <= quasigroup[a][b], quasigroup[a][b] <= m - 1)
                for a in rng for b in rng])

    # Latin square: each element occurs once in every row and every column. A table
    # of order 1 has no two cells to tell apart.
    if m >= 2:
        solver.add([c5.Distinct(quasigroup[a]) for a in rng])
        solver.add([c5.Distinct([quasigroup[a][b] for a in rng]) for b in rng])

    # (a*b)*(b*a) = a. With p = a*b and q = b*a, the cell in row p and column q holds a.
    for a in rng:
        for b in rng:
            p = quasigroup[a][b]
            q = quasigroup[b][a]
            solver.add([c5.Or(p != i, q != j, quasigroup[i][j] == a)
                        for i in rng for j in rng])

    return solver, {"quasigroup": quasigroup}


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
