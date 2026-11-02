# bin_packing: a PySAT (Python) model from DCP Rosetta.
# Download the `bin_packing.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/bin_packing.html
# Then run it on the first instance (after `pip install "python-sat[pblib]" numpy`):
#   python bin_packing.py bin_packing.json

from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine
from pysat.pb import PBEnc


def create_model(instance):
    """Assign each item to a bin so that the total weight of the items in each bin does
    not exceed the bin capacity."""
    weights = instance["weights"]    # weights[j]: the weight of item j
    capacity = instance["capacity"]  # the most weight a bin can hold
    num_bins = instance["num_bins"]  # the number of bins, numbered from 0
    n_items = len(weights)

    pool = IDPool()

    # bins[j] is the bin that item j goes into
    bins = [Integer(f"bin{j}", 0, num_bins - 1, vpool=pool) for j in range(n_items)]
    engine = IntegerEngine(vars=bins, vpool=pool)
    formula = engine.clausify()

    for b in range(num_bins):
        # items_in_bin[j] is true when item j goes into bin b
        items_in_bin = [bins[j].equals(b) for j in range(n_items)]
        # The items in bin b weigh no more than the capacity.
        formula.extend(PBEnc.leq(lits=items_in_bin, weights=weights, bound=capacity,
                                 vpool=pool).clauses)

    return formula, {"bins": bins}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np
    from pysat.solvers import Solver

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    formula, outputs = create_model(instances[index])

    solver = Solver(bootstrap_with=formula)
    solver.solve()
    model = solver.get_model()  # None when there is no solution

    if model:
        value = np.vectorize(lambda var: var.decode(model))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")
