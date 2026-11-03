# prod: a hermax (Python) model from DCP Rosetta.
# Download the `prod.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/prod.html
# Then run it on the first instance (after `pip install hermax`):
#   python prod.py prod.json

from math import lcm

from hermax.model import Model


def create_model(instance):
    """Production planning: choose how many units X[j] of each product j to make, within
    the time available, so that the total profit is as large as possible. Product j needs
    1/a[j] hours of the shared time per unit, product j earns c[j] per unit, and it can be
    made at most u[j] times."""
    a = instance["a"]  # a[j]: the number of units of product j made per hour
    b = instance["b"]  # b: the total hours available for production
    c = instance["c"]  # c[j]: the profit of one unit of product j
    u = instance["u"]  # u[j]: the most units of product j that can be made
    n = len(a)  # n: the number of products

    # Time is measured in units of 1/L hour, with L = lcm(a), so that every
    # product's time per unit, 1/a[j] hours, is the whole number L // a[j].
    L = lcm(*a)

    m = Model()

    # X[j] is the number of units of product j to make, from 0 to u[j]
    X = m.vector([m.int(f"x_{j}", 0, u[j]) for j in range(n)])

    # The time spent on all products must fit in the b hours available (b * L units of 1/L hour).
    m &= (sum((L // a[j]) * X[j] for j in range(n)) <= b * L)

    # The total profit of the units made: the sum of c[j] * X[j].
    total_profit = sum(c[j] * X[j] for j in range(n))

    # Maximise the total profit, by minimising its negation.
    m.obj += -total_profit

    return m, {"x": X, "total_profit": total_profit}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
    else:
        print("No solution:", result.status)
