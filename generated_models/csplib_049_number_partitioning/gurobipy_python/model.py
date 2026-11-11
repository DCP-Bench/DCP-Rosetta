# csplib_049_number_partitioning: a Gurobi (Python) model from DCP Rosetta.
# Download the `csplib_049_number_partitioning.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_049_number_partitioning.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python csplib_049_number_partitioning.py csplib_049_number_partitioning.json

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """Split the numbers 1 to n into two sets A and B of equal size, with equal sums and equal sums of squares."""
    n = instance["n"]  # the numbers to split are 1 to n
    half = n // 2     # the size of A and of B: each holds half of the numbers
    values = range(1, n + 1)
    # positions 0 to half-1 hold the numbers of A, half to 2*half-1 those of B; for odd n one number
    # has no position, so the model is infeasible: equal sizes are impossible
    slots = range(2 * half)
    in_A = range(half)
    in_B = range(half, 2 * half)

    model = gp.Model("number_partitioning")

    # Positions, not one in-A flag per number, because A and B are printed as lists: position s gives
    # the s-th entry.
    # holds[s, v] is 1 when position s holds the number v, and 0 when not.
    holds = model.addVars(slots, values, vtype=GRB.BINARY, name="holds")
    # Each position holds exactly one number (holds.sum(s, "*") adds holds[s, v] over all numbers v).
    model.addConstrs((holds.sum(s, "*") == 1 for s in slots), name="slot")
    # Each number is in exactly one position (holds.sum("*", v) adds holds[s, v] over all positions s).
    model.addConstrs((holds.sum("*", v) == 1 for v in values), name="value")

    # The numbers in A and the numbers in B have the same sum.
    model.addConstr(gp.quicksum(v * holds[s, v] for s in in_A for v in values)
                    == gp.quicksum(v * holds[s, v] for s in in_B for v in values), name="sums")

    # The squares of the numbers in A and in B have the same sum.
    model.addConstr(gp.quicksum(v * v * holds[s, v] for s in in_A for v in values)
                    == gp.quicksum(v * v * holds[s, v] for s in in_B for v in values), name="squares")

    # A and B list the number held at each position: the number in position s is the sum of v * holds[s, v] over v.
    A = [gp.quicksum(v * holds[s, v] for v in values) for s in in_A]
    B = [gp.quicksum(v * holds[s, v] for v in values) for s in in_B]
    return model, {"A": A, "B": B}


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
