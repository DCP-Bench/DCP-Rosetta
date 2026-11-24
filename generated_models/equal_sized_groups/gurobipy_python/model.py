# equal_sized_groups: a Gurobi (Python) model from DCP Rosetta.
# Download the `equal_sized_groups.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/equal_sized_groups.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python equal_sized_groups.py equal_sized_groups.json

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """Split a sorted list of N elements into K groups by K - 1 break points, keeping equal values
    in one group, so that the groups are as close in size to round(N / K) as possible."""
    a, k = instance["a"], instance["k"]  # a[i]: the i-th element of the sorted list (0-based); k: the number of groups
    n = len(a)  # N, the number of elements
    ideal = round(n / k)  # round(N / K), the target size of each group (Python's round: halves go to the even number)
    groups = range(k)  # group numbers 0 .. K - 1
    breaks = range(k - 1)  # break-point numbers 0 .. K - 2

    # A break point at position j (the first j elements lie before it) may not separate two equal
    # values, so it can only sit where the value changes.
    allowed = [j for j in range(1, n) if a[j - 1] != a[j]]

    model = gp.Model("equal_sized_groups")

    # at[p, j] is 1 when break point p is at position j
    at = model.addVars(breaks, allowed, vtype=GRB.BINARY, name="at")
    # Each break point is at exactly one allowed position (at.sum(p, "*") adds over the positions)
    model.addConstrs((at.sum(p, "*") == 1 for p in breaks), name="one_position")
    # x[p] is the position of break point p: the number of elements before it, which is the 1-based
    # index of the last element before the break, as printed
    x = [gp.quicksum(j * at[p, j] for j in allowed) for p in breaks]

    # The list starts at position 0 and ends at position n. Group i runs from one of these
    # positions to the next.
    bounds = [0] + x + [n]
    # size[i] is the number of elements in group i. Each group has at least one element (K groups),
    # which also keeps the break points in increasing order.
    size = model.addVars(groups, lb=1, ub=n, vtype=GRB.INTEGER, name="size")
    model.addConstrs((size[i] == bounds[i + 1] - bounds[i] for i in groups), name="group_size")

    # error[i] is how far group i's size is from the ideal size. The objective minimises their sum,
    # so at the optimum each error is exactly that distance.
    error = model.addVars(groups, lb=0, ub=n, vtype=GRB.INTEGER, name="error")
    model.addConstrs((error[i] >= size[i] - ideal for i in groups), name="error_over")
    model.addConstrs((error[i] >= ideal - size[i] for i in groups), name="error_under")

    # Minimise the total error: how far the group sizes are from round(N / K), added up.
    model.setObjective(error.sum(), GRB.MINIMIZE)

    return model, {"x": x}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.Params.OutputFlag = 0  # no solver log
    model.Params.MIPGap = 0  # prove the optimum; the default stops within 0.01% of it
    model.optimize()

    if model.Status == GRB.OPTIMAL:  # a proven optimum
        print("Objective value:", round(model.ObjVal))
        # a variable's value is var.X, an expression's is expr.getValue(); both read through LinExpr
        value = np.vectorize(lambda out: round(gp.LinExpr(out).getValue()))
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution, Gurobi status", model.Status)  # 3 infeasible, 4 infeasible or unbounded
