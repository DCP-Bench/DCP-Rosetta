# knapsack: a PySAT (Python) model from DCP Rosetta.
# Download the `knapsack.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/knapsack.html
# Then run it on the first instance (after `pip install "python-sat[pblib]" numpy`):
#   python knapsack.py knapsack.json

from pysat.formula import IDPool, WCNF
from pysat.pb import PBEnc


def create_model(instance):
    """A hiker chooses which items to pack: as much total value as possible,
    without the items weighing more than the backpack can carry."""
    values = instance["values"]      # values[i]: the value of item i
    weights = instance["weights"]    # weights[i]: the weight of item i
    capacity = instance["capacity"]  # the most weight the backpack can carry

    pool = IDPool()

    # x[i] is true when the hiker packs item i
    x = [pool.id(("x", i)) for i in range(len(values))]

    formula = WCNF()

    # The packed items weigh no more than the backpack can carry.
    formula.extend(PBEnc.leq(lits=x, weights=weights, bound=capacity, vpool=pool).clauses)

    # Pack the most valuable selection. RC2 minimises the weight of the soft clauses it
    # falsifies, so leaving item i behind costs its value.
    for xi, v in zip(x, values):
        if v > 0:
            formula.append([xi], weight=v)

    # The objective in the problem's terms: the total value of the packed items
    # (RC2's cost is the value left behind).
    objective = [(v, xi) for xi, v in zip(x, values)]

    return formula, {"x": x}, objective


if __name__ == "__main__":
    import json
    import sys
    import numpy as np
    from pysat.examples.rc2 import RC2Stratified

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    formula, outputs, objective = create_model(instances[index])

    # falsify as little soft-clause weight as possible
    model = RC2Stratified(formula).compute()

    if model:
        # a literal is true when it is in the model
        value = np.vectorize(lambda lit: lit in model)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")
