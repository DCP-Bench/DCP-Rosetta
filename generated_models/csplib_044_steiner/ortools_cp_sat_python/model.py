# csplib_044_steiner: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
# Download the `csplib_044_steiner.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_044_steiner.html
# Then run it on the first instance (after `pip install ortools`):
#   python csplib_044_steiner.py csplib_044_steiner.json

from ortools.sat.python import cp_model


def create_model(instance):
    """Find n * (n - 1) / 6 triples of distinct elements of {1, ..., n} such that any two
    triples have at most one element in common (n is 1 or 3 modulo 6)."""
    n_elements = instance["n"]                    # the number of elements
    n_sets = n_elements * (n_elements - 1) // 6   # the number of triples required

    model = cp_model.CpModel()

    # sets[i][j] is true when element j belongs to triple i
    sets = [[model.new_bool_var(f"sets_{i}_{j}") for j in range(n_elements)] for i in range(n_sets)]

    # Each triple has exactly three elements.
    for i in range(n_sets):
        model.add(sum(sets[i]) == 3)

    # Any two triples have at most one element in common.
    for i1 in range(n_sets):
        for i2 in range(i1 + 1, n_sets):
            # both[j] is true when element j is in both triples, and at most one of them may be true.
            both = []
            for j in range(n_elements):
                both_j = model.new_bool_var(f"common_{i1}_{i2}_{j}")
                model.add_bool_or([~sets[i1][j], ~sets[i2][j], both_j])
                both.append(both_j)
            model.add(sum(both) <= 1)

    return model, {"sets": sets}


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
