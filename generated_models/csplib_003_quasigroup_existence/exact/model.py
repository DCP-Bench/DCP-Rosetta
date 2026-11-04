# csplib_003_quasigroup_existence: an Exact (Python) model from DCP Rosetta.
# Download the `csplib_003_quasigroup_existence.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_003_quasigroup_existence.html
# Then run it on the first instance (after `pip install exact numpy`):
#   python csplib_003_quasigroup_existence.py csplib_003_quasigroup_existence.json

from exact import Exact


def create_model(instance):
    """QG3.m quasigroup existence: find an order m quasigroup, a Latin square of size
    m with every element once in each row and column, such that (a*b)*(b*a) = a."""
    m = instance["m"]  # the order of the quasigroup: the size of the table and the number of elements

    solver = Exact()

    # Exact identifies its variables by name.
    # quasigroup[i][j] is the product i*j, the element in row i and column j, from 0 to m-1.
    quasigroup = [[f"q_{i}_{j}" for j in range(m)] for i in range(m)]
    for i in range(m):
        for j in range(m):
            solver.addVariable(quasigroup[i][j], 0, m - 1)

    # is_value[i][j][v] is 1 when the product i*j is v, and 0 when not.
    is_value = [[[f"q_{i}_{j}_is_{v}" for v in range(m)] for j in range(m)] for i in range(m)]
    for i in range(m):
        for j in range(m):
            for v in range(m):
                solver.addVariable(is_value[i][j][v], 0, 1)

    # Each product i*j is exactly one element, and quasigroup[i][j] is that element.
    for i in range(m):
        for j in range(m):
            solver.addConstraint([(1, is_value[i][j][v]) for v in range(m)], True, 1, True, 1)
            solver.addConstraint([(v, is_value[i][j][v]) for v in range(1, m)]
                                 + [(-1, quasigroup[i][j])], True, 0, True, 0)

    # Each element occurs once in every row.
    for i in range(m):
        for v in range(m):
            solver.addConstraint([(1, is_value[i][j][v]) for j in range(m)], True, 1, True, 1)

    # Each element occurs once in every column.
    for i in range(m):
        for v in range(m):
            solver.addConstraint([(1, is_value[j][i][v]) for j in range(m)], True, 1, True, 1)

    # QG3.m: (a*b)*(b*a) = a. If a*b is c and b*a is d, the product c*d is a.
    for a in range(m):
        for b in range(m):
            for c in range(m):
                for d in range(m):
                    # coefficients[name] is the coefficient of the variable name in this instance of
                    # the property; a variable that appears twice gets the sum of its coefficients.
                    coefficients = {}
                    for coefficient, name in ((1, is_value[a][b][c]), (1, is_value[b][a][d]),
                                              (-1, is_value[c][d][a])):
                        coefficients[name] = coefficients.get(name, 0) + coefficient
                    solver.addConstraint([(k, name) for name, k in coefficients.items() if k],
                                         False, 0, True, 1)

    return solver, {"quasigroup": quasigroup}


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
