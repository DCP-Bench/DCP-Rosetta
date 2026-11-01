# prod: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
# Download the `prod.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/prod.html
# Then run it on the first instance (after `pip install ortools`):
#   python prod.py prod.json

from math import lcm

from ortools.sat.python import cp_model


def create_model(instance):
    """Choose a production quantity x[j] between 0 and u[j] for each element j of P,
    so that the total profit, the sum of c[j] * x[j], is as large as possible, while the
    sum of x[j] / a[j] stays at most b."""
    a = instance["a"]  # a[j]: one unit of x[j] uses 1 / a[j] of the capacity
    c = instance["c"]  # c[j]: the profit per unit of x[j]
    u = instance["u"]  # u[j]: the most units of x[j] allowed
    b = instance["b"]  # the capacity, the most the sum of x[j] / a[j] may reach

    model = cp_model.CpModel()

    # x[j] is the production quantity for element j
    x = [model.new_int_var(0, u[j], f"x_{j}") for j in range(len(a))]

    # scale: the least common multiple of the a[j], which makes the capacity terms whole numbers
    scale = lcm(*a)
    # The capacity used stays at most b, with both sides multiplied by scale.
    model.add(sum((scale // aj) * xj for aj, xj in zip(a, x)) <= b * scale)

    # total_profit is the sum of c[j] * x[j]
    total_profit = sum(cj * xj for cj, xj in zip(c, x))
    # Make the total profit as large as possible.
    model.maximize(total_profit)

    return model, {"x": x, "total_profit": total_profit}


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
