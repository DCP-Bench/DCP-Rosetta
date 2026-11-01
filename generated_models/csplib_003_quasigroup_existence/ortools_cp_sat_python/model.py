# csplib_003_quasigroup_existence: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
# Download the `csplib_003_quasigroup_existence.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_003_quasigroup_existence.html
# Then run it on the first instance (after `pip install ortools`):
#   python csplib_003_quasigroup_existence.py csplib_003_quasigroup_existence.json

from ortools.sat.python import cp_model


def create_model(instance):
    """QG3.m quasigroup existence: find an order m quasigroup, a Latin square of size
    m with every element once in each row and column, such that (a*b)*(b*a) = a."""
    m = instance["m"]  # the order of the quasigroup

    model = cp_model.CpModel()

    # quasigroup[a][b] is the product a*b, an element from 0 to m-1
    quasigroup = [[model.new_int_var(0, m - 1, f"quasigroup_{a}_{b}") for b in range(m)]
                  for a in range(m)]

    # Latin square: each element occurs once in every row and every column.
    for i in range(m):
        model.add_all_different(quasigroup[i])
        model.add_all_different([quasigroup[j][i] for j in range(m)])

    # QG3.m: (a*b)*(b*a) = a for all a and b. The entry in row a*b and column b*a is a.
    # The entries of the table, listed for the lookup below.
    flat = [quasigroup[i][j] for i in range(m) for j in range(m)]
    for a in range(m):
        for b in range(m):
            index = model.new_int_var(0, m * m - 1, f"index_{a}_{b}")
            model.add(index == m * quasigroup[a][b] + quasigroup[b][a])
            model.add_element(index, flat, a)

    return model, {"quasigroup": quasigroup}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    solver = cp_model.CpSolver()
    solver_value = np.vectorize(solver.value)  # make it work on nested variables

    status = solver.solve(model)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        for name, output in outputs.items():
            print(name, "=", solver_value(output))
    else:
        print("No solution:", solver.status_name(status))
