# prod: a Choco-solver (Python) model from DCP Rosetta.
# Download the `prod.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/prod.html
# Then run it on the first instance (after `pip install pychoco numpy`):
#   python prod.py prod.json

from math import lcm

from pychoco.model import Model


def create_model(instance):
    """Production planning: choose how many units x[j] of each product to make, at most u[j]
    of product j, so that the production time used does not exceed b and the total profit
    is as large as possible. One unit of product j takes 1 / a[j] of the time."""
    a = instance["a"]  # a[j]: units of product j made per unit of time
    c = instance["c"]  # c[j]: profit of one unit of product j
    u = instance["u"]  # u[j]: most units of product j that may be made
    b = instance["b"]  # the available production time
    n_products = len(a)

    model = Model()

    # x[j]: units of product j made
    x = [model.intvar(0, u[j], name=f"x_{j}") for j in range(n_products)]

    # scale: the least common multiple of the a[j]. Multiplying the time limit by it turns the
    # fractions 1 / a[j] into whole numbers.
    scale = lcm(*a)

    # The production time used by all products is at most b.
    model.scalar(x, [scale // a[j] for j in range(n_products)], "<=", b * scale).post()

    # total_profit: the profit of all units made.
    total_profit = model.intvar(0, sum(c[j] * u[j] for j in range(n_products)), name="total_profit")
    model.scalar(x, c, "=", total_profit).post()

    # Maximise the total profit.
    return model, {"x": x, "total_profit": total_profit}, {"objective": total_profit, "maximize": True}


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
