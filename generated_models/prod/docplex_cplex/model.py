# prod: a CPLEX (Python) model from DCP Rosetta.
# Download the `prod.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/prod.html
# Then run it on the first instance (after `pip install docplex cplex`; the CPLEX that comes
# with pip allows models up to 1000 variables and 1000 constraints):
#   python prod.py prod.json

import math
from docplex.mp.model import Model


def create_model(instance):
    """Choose a quantity x[j] between 0 and u[j] for every product j so that the sum of x[j] / a[j]
    is at most b, maximising the total profit, the sum of c[j] * x[j]."""
    a = instance["a"]  # a[j]: each unit of product j counts 1 / a[j] towards the limit b
    c = instance["c"]  # c[j]: the profit of one unit of product j
    u = instance["u"]  # u[j]: the largest quantity of product j
    b = instance["b"]  # the limit on the sum of x[j] / a[j]
    products = range(len(a))

    model = Model("prod")

    # x[j] is the quantity of product j, between 0 and u[j].
    x = [model.integer_var(0, u[j], name=f"x_{j}") for j in products]

    # The sum of x[j] / a[j] is at most b. Both sides are multiplied by the least common
    # multiple of the a[j] so that every coefficient is an integer and the check is exact,
    # not subject to floating-point tolerance.
    lcm_a = math.lcm(*a)
    model.add_constraint(model.sum((lcm_a // a[j]) * x[j] for j in products) <= b * lcm_a,
                         ctname="budget")

    # Maximise the total profit.
    total_profit = model.dot(x, c)
    model.maximize(total_profit)

    return model, {"x": x, "total_profit": total_profit}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.parameters.mip.tolerances.mipgap = 0  # prove the optimum; the default stops within 0.01% of it
    solution = model.solve()

    if solution:  # a proven optimum
        print("Objective value:", round(solution.objective_value))

        def value(out):  # a variable, a linear expression or a number, or lists of them
            if isinstance(out, (list, tuple)):
                return [value(item) for item in out]
            return out if isinstance(out, int) else round(out.solution_value)

        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.solve_details.status)
