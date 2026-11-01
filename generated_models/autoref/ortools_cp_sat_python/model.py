# autoref: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
# Download the `autoref.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/autoref.html
# Then run it on the first instance (after `pip install ortools`):
#   python autoref.py autoref.json

from ortools.sat.python import cp_model


def create_model(instance):
    """Find a series s[0], s[1], ..., s[n+1] in which every integer i from 0 to n
    occurs exactly s[i] times, and whose last element s[n+1] equals m."""
    n = instance["n"]  # the values 0 to n are counted in the series
    m = instance["m"]  # the required value of the last element

    model = cp_model.CpModel()

    # s[k] is the k-th element of the series; every element lies between 0 and n
    s = [model.new_int_var(0, n, f"s_{k}") for k in range(n + 2)]

    # The last element is m.
    model.add(s[n + 1] == m)

    # The value i occurs exactly s[i] times.
    for i in range(n + 1):
        # is_value[k] is true when s[k] is i
        is_value = []
        for k in range(n + 2):
            b = model.new_bool_var(f"is_{i}_at_{k}")
            model.add(s[k] == i).only_enforce_if(b)
            model.add(s[k] != i).only_enforce_if(~b)
            is_value.append(b)
        model.add(sum(is_value) == s[i])

    return model, {"s": s}


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
