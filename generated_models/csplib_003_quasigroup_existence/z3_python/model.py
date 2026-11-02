# csplib_003_quasigroup_existence: a Z3 (Python) model from DCP Rosetta.
# Download the `csplib_003_quasigroup_existence.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_003_quasigroup_existence.html
# Then run it on the first instance (after `pip install z3-solver numpy`):
#   python csplib_003_quasigroup_existence.py csplib_003_quasigroup_existence.json

import z3


def create_model(instance):
    """QG3.m quasigroup existence: find an order m quasigroup, a Latin square of size
    m with every element once in each row and column, such that (a*b)*(b*a) = a."""
    m = instance["m"]  # the order of the quasigroup

    # table[i][j] is the product i*j, an element from 0 to m-1.
    table = [[z3.Int(f"q_{i}_{j}") for j in range(m)] for i in range(m)]

    # The same table read as one list of m * m entries, so that the entry in row r and
    # column c sits at position r * m + c.
    flat = z3.Array("quasigroup_flat", z3.IntSort(), z3.IntSort())

    solver = z3.Solver()

    # Each product is an element from 0 to m-1.
    for row in table:
        for cell in row:
            solver.add(z3.And(cell >= 0, cell <= m - 1))

    # Latin square: each element occurs once in every row and every column.
    for i in range(m):
        solver.add(z3.Distinct(table[i]))
        solver.add(z3.Distinct([table[r][i] for r in range(m)]))

    # The flat list holds the table.
    for i in range(m):
        for j in range(m):
            solver.add(z3.Select(flat, i * m + j) == table[i][j])

    # QG3.m: (a*b)*(b*a) = a for all a and b. The entry in row a*b and column b*a is a.
    for a in range(m):
        for b in range(m):
            solver.add(z3.Select(flat, table[a][b] * m + table[b][a]) == a)

    return solver, {"quasigroup": table}


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
