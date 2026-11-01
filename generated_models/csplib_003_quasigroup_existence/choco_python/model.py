# csplib_003_quasigroup_existence: a Choco-solver (Python) model from DCP Rosetta.
# Download the `csplib_003_quasigroup_existence.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_003_quasigroup_existence.html
# Then run it on the first instance (after `pip install pychoco numpy`):
#   python csplib_003_quasigroup_existence.py csplib_003_quasigroup_existence.json

from pychoco.model import Model


def create_model(instance):
    """QG3.m quasigroup existence: find an order m quasigroup, a Latin square of size m
    with every element once in each row and column, such that (a*b)*(b*a) = a."""
    m = instance["m"]  # order of the quasigroup, so the table has m rows and m columns

    model = Model()

    # quasigroup[i][j] is the product i*j, a value from 0 to m-1.
    quasigroup = [[model.intvar(0, m - 1, name=f"q_{i}_{j}") for j in range(m)] for i in range(m)]

    # Each value occurs once in every row.
    for i in range(m):
        model.all_different(quasigroup[i]).post()

    # Each value occurs once in every column.
    for j in range(m):
        model.all_different([quasigroup[i][j] for i in range(m)]).post()

    # is_value[i][j][v] is true when the product i*j is v.
    is_value = [[[model.arithm(quasigroup[i][j], "=", v).reify() for v in range(m)]
                 for j in range(m)] for i in range(m)]

    # (a*b)*(b*a) = a for all a and b. If a*b is u and b*a is w, then u*w is a.
    # For a equal to b, a*a is u and also w, so only u equal to w matters, and then u*u is a.
    for a in range(m):
        for b in range(m):
            for u in range(m):
                for w in range(m):
                    if a == b:
                        if u == w:
                            model.scalar([is_value[a][a][u], is_value[u][u][a]], [1, -1], "<=", 0).post()
                    else:
                        model.scalar([is_value[a][b][u], is_value[b][a][w], is_value[u][w][a]],
                                     [1, 1, -1], "<=", 1).post()

    return model, {"quasigroup": quasigroup}, None


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs, objective = create_model(instances[index])
    solver = model.get_solver()

    if objective:  # optimisation: find a solution and prove no better one exists
        solution = solver.find_optimal_solution(**objective)
    else:  # satisfaction: any solution will do
        solution = solver.find_solution()

    if solution:
        solution_value = np.vectorize(solution.get_int_val)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", solution_value(output))
    else:
        print("No solution")
