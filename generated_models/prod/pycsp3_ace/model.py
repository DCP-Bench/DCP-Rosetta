# prod: a PyCSP3 model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/prod.html
# Download the `prod.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/prod.html
# Then run it on the first instance (after `pip install pycsp3`, which also needs Java for its ACE solver):
#   python prod.py prod.json

from pycsp3 import *


def create_model(instance):
    """Choose how many units x[j] of each element j of a set P to produce, with x[j] between
    0 and u[j]. The sum of x[j] / a[j] over P is at most b. Maximise the total profit, the
    sum of c[j] * x[j] over P."""
    a = instance["a"]  # a[j] is the rate of element j: one unit of x[j] takes 1 / a[j] of the capacity b
    b = instance["b"]  # the capacity shared by all elements
    c = instance["c"]  # c[j] is the profit of one unit of element j
    u = instance["u"]  # u[j] is the most units of element j that can be produced
    n_elements = len(a)

    # The capacity constraint has the fractions 1 / a[j], so it is scaled by a common multiple of
    # the a[j]. The product of the a[j] is used: it is a multiple of each a[j], not necessarily the
    # least one, and any common multiple gives the same constraint.
    common_multiple = 1
    for rate in a:
        common_multiple *= rate

    # x[j] is the number of units of element j produced, from 0 up to u[j].
    x = VarArray(size=n_elements, dom=lambda j: range(u[j] + 1))

    # The profit is at most the sum of c[j] * u[j] over P, taking c and u as non-negative.
    max_profit = sum(c[j] * u[j] for j in range(n_elements))
    # total_profit is the total profit, the sum of c[j] * x[j] over P.
    total_profit = Var(dom=range(max_profit + 1))

    satisfy(
        # The production uses at most the capacity b: sum of x[j] / a[j] <= b, multiplied
        # through by common_multiple so that every coefficient is an integer.
        Sum((common_multiple // a[j]) * x[j] for j in range(n_elements)) <= common_multiple * b,
        # The total profit is the sum of c[j] * x[j] over P.
        total_profit == Sum(c[j] * x[j] for j in range(n_elements)),
    )

    # The total profit is maximised.
    maximize(total_profit)

    return {"x": x, "total_profit": total_profit}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    outputs = create_model(instances[index])
    if solve() is OPTIMUM:
        print("x", "=", values(outputs["x"]))
        print("total_profit", "=", value(outputs["total_profit"]))
    else:
        print("No solution:", status())
