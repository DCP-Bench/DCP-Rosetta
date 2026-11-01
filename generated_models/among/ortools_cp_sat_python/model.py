# among: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
# Download the `among.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/among.html
# Then run it on the first instance (after `pip install ortools`):
#   python among.py among.json

from ortools.sat.python import cp_model


def create_model(instance):
    """Exactly m of the values in x take one of the values in v. Every value in x
    is at least 0 and at most 7."""
    n_values = instance["n"]      # the number of values in x
    n_matches = instance["m"]     # how many values in x must take a value from v
    v = instance["v"]             # the values that are counted

    model = cp_model.CpModel()

    # x[i] is the value at position i
    x = [model.new_int_var(0, 7, f"x_{i}") for i in range(n_values)]

    # hit[i][k] marks whether x[i] takes the value v[k]
    hit = [[model.new_bool_var(f"hit_{i}_{k}") for k in range(len(v))] for i in range(n_values)]
    # A mark is set exactly when the value at position i equals v[k].
    for i in range(n_values):
        for k, number in enumerate(v):
            model.add(x[i] == number).only_enforce_if(hit[i][k])
            model.add(x[i] != number).only_enforce_if(~hit[i][k])

    # Exactly n_matches positions take a value from v.
    model.add(sum(h for row in hit for h in row) == n_matches)

    return model, {"x": x}


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
