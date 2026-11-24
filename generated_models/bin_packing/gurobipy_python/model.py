# bin_packing: a Gurobi (Python) model from DCP Rosetta.
# Download the `bin_packing.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/bin_packing.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python bin_packing.py bin_packing.json

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """Assign each item to one of the bins so that the total weight of the items in every bin
    does not exceed the bin's capacity."""
    weights = instance["weights"]    # weights[j]: the weight of item j
    capacity = instance["capacity"]  # the most weight a single bin can hold
    num_bins = instance["num_bins"]  # the number of bins available

    items = range(len(weights))
    bins = range(num_bins)

    model = gp.Model("bin_packing")

    # put[j, b] is 1 when item j goes into bin b, and 0 when not.
    put = model.addVars(items, bins, vtype=GRB.BINARY, name="put")

    # Every item goes into exactly one bin (put.sum(j, "*") adds put[j, b] over all bins b).
    model.addConstrs((put.sum(j, "*") == 1 for j in items), name="one_bin")

    # The items in each bin weigh no more than the capacity.
    model.addConstrs((gp.quicksum(weights[j] * put[j, b] for j in items) <= capacity
                      for b in bins), name="capacity")

    # bin_of[j] is the bin of item j, 0-indexed: the bin number b with put[j, b] equal to 1.
    bin_of = [gp.quicksum(b * put[j, b] for b in bins) for j in items]

    # No objective is set: any assignment that respects the capacities is a solution.
    return model, {"bins": bin_of}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.Params.OutputFlag = 0  # no solver log
    model.optimize()

    if model.Status == GRB.OPTIMAL:  # a solution
        # a variable's value is var.X, an expression's is expr.getValue(); both read through LinExpr
        value = np.vectorize(lambda out: round(gp.LinExpr(out).getValue()))
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution, Gurobi status", model.Status)  # 3 infeasible, 4 infeasible or unbounded
